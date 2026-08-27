"""Stdlib-only runtime query layer over the local SQLite FTS5 database of US
primary law built by ``scripts/fetch_open_us_law.py`` from the HuggingFace
dataset ``vaquill/open-us-law`` (CC-BY-4.0, attribution Vaquill AI).

Two-tier architecture:
  Tier-1 = curated ``_statute_corpus`` digests (STATUS: VERIFIED, hand-shaped).
  Tier-2 = full-text statutory lookup served by this module (CC-BY-4.0,
           Vaquill AI). Currency is NOT uniform: ``act_status='snapshot'``
           rows are unrefreshed captures with good-law status unknown. The
           Tier-1 STATUS: VERIFIED discipline does NOT transfer to Tier-2.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
import textwrap
from pathlib import Path
from typing import Any

DISCLAIMER = (
    "Tier-2 full-text statutory layer sourced from vaquill/open-us-law "
    "(HuggingFace), CC-BY-4.0, attribution Vaquill AI. Currency is NOT "
    "uniform: act_status='snapshot' rows are unrefreshed captures with "
    "good-law status unknown. Every section MUST be re-verified against "
    "its source_url / the official government source before use in any "
    "filing or advice. The Tier-1 curated digests' STATUS: VERIFIED "
    "discipline does NOT transfer to Tier-2."
)


class Tier2Unavailable(RuntimeError):
    """Raised when the Tier-2 SQLite FTS5 database is absent."""


DEFAULT_DB_PATH = (
    Path(__file__).resolve().parent.parent
    / "_statute_corpus"
    / "_tier2_open_us_law"
    / "open_us_law.sqlite3"
)

_SECTIONS_COLUMNS = [
    "id",
    "collection",
    "act_id",
    "citation",
    "citation_short",
    "state",
    "jurisdiction",
    "document_type",
    "title_number",
    "title_name",
    "chapter",
    "chapter_name",
    "section_number",
    "section_title",
    "breadcrumb",
    "display_path",
    "act_status",
    "text",
    "word_count",
    "source_url",
    "last_amended_year",
    "subsection_count",
    "cross_references_usc",
    "cross_references_cfr",
    "public_laws_referenced",
    "year",
]

_SELECT_COLUMNS = ", ".join(f"s.{c}" for c in _SECTIONS_COLUMNS)


class Tier2Statutes:
    def __init__(self, db_path: str | Path | None = None) -> None:
        self.db_path: Path = Path(db_path) if db_path is not None else DEFAULT_DB_PATH

    def is_available(self) -> bool:
        return self.db_path.is_file()

    def _ensure_available(self) -> None:
        if not self.is_available():
            raise Tier2Unavailable(
                "Tier-2 database not found at "
                f"{self.db_path}. Build it with "
                "`python scripts/fetch_open_us_law.py --sample 100` "
                "(or --full) and retry."
            )

    def _connect(self) -> sqlite3.Connection:
        uri = self.db_path.resolve().as_uri() + "?mode=ro"
        conn = sqlite3.connect(uri, uri=True)
        conn.row_factory = sqlite3.Row
        return conn

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        hit = {col: row[col] for col in _SECTIONS_COLUMNS}
        hit["currency_note"] = _currency_note(hit)
        return hit

    def lookup_citation(self, citation: str) -> list[dict]:
        self._ensure_available()
        target = citation.strip().lower()
        sql = (
            f"SELECT {_SELECT_COLUMNS} FROM sections s "
            "WHERE lower(s.citation) = ? "
            "OR lower(s.citation_short) = ? "
            "OR lower(s.act_id) = ? "
            "ORDER BY s.id"
        )
        with self._connect() as conn:
            cur = conn.execute(sql, (target, target, target))
            rows = cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    def search(
        self,
        query: str,
        state: str | None = None,
        collection: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        self._ensure_available()
        limit = max(1, min(int(limit), 500))
        tokens = re.findall(r"\w+", query or "")
        if not tokens:
            return []
        match_expr = " ".join(f'"{t}"' for t in tokens)
        params: list[Any] = [match_expr]
        clauses: list[str] = []
        if state:
            clauses.append("lower(s.state) = ?")
            params.append(state.strip().lower())
        if collection:
            clauses.append("s.collection = ?")
            params.append(collection)
        where_extra = ("".join(" AND " + c for c in clauses)) if clauses else ""
        params.append(int(limit))
        sql = (
            "SELECT {_cols} FROM sections_fts f "
            "JOIN sections s ON s.id = f.rowid "
            "WHERE sections_fts MATCH ?{extra} "
            "ORDER BY bm25(sections_fts) "
            "LIMIT ?"
        ).format(_cols=_SELECT_COLUMNS, extra=where_extra)
        with self._connect() as conn:
            cur = conn.execute(sql, params)
            rows = cur.fetchall()
        return [self._row_to_dict(r) for r in rows]

    def stats(self) -> dict[str, str]:
        self._ensure_available()
        with self._connect() as conn:
            cur = conn.execute("SELECT key, value FROM manifest")
            rows = cur.fetchall()
        return {r["key"]: r["value"] for r in rows}


def _currency_note(hit: dict[str, Any]) -> str:
    status = (hit.get("act_status") or "").lower()
    source = hit.get("source_url") or "(no source_url recorded)"
    if status != "in_force":
        detail = (
            "unrefreshed snapshot capture"
            if status == "snapshot"
            else "recorded status is not 'in_force'"
        )
        return (
            f"act_status='{status}' — {detail}, good-law status unknown; "
            f"re-verify the current text at the official government source "
            f"(recorded provenance: {source}) before any use."
        )
    return (
        f"act_status='in_force' but currency is not guaranteed by the "
        f"Tier-2 layer; re-verify current text at the official government "
        f"source (recorded provenance: {source}) before filing."
    )


def format_result(hit: dict) -> str:
    text = hit.get("text") or ""
    snippet = text[:300] + ("…" if len(text) > 300 else "")
    lines = [
        f"Citation: {hit.get('citation')}",
        f"Display path: {hit.get('display_path')}",
        f"Act status: {hit.get('act_status')}",
        f"Source URL: {hit.get('source_url')}",
        "Text (first ~300 chars):",
        textwrap.indent(snippet, "  "),
        f"Currency note: {hit.get('currency_note')}",
    ]
    return "\n".join(lines)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="aibrain_usa.tier2_statutes",
        description=(
            "Tier-2 full-text lookup over the local SQLite FTS5 copy of "
            "vaquill/open-us-law (CC-BY-4.0, Vaquill AI). Read-only."
        ),
    )
    parser.add_argument("query", nargs="?", default=None, help="Free-text FTS5 query (sanitized).")
    parser.add_argument(
        "--citation", default=None, help="Exact lookup against citation / citation_short / act_id."
    )
    parser.add_argument("--state", default=None, help="Filter (lowercase, e.g. 'ca').")
    parser.add_argument(
        "--collection",
        default=None,
        help="Filter by collection (e.g. 'statutes', 'constitutions').",
    )
    parser.add_argument(
        "--limit", type=int, default=10, help="Maximum number of hits (default 10)."
    )
    parser.add_argument("--db", default=None, help="Override the default database path.")
    parser.add_argument("--stats", action="store_true", help="Print the build manifest and exit.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.query and not args.citation and not args.stats:
        parser.print_usage(sys.stderr)
        return 2

    t2 = Tier2Statutes(db_path=args.db)

    if not t2.is_available():
        sys.stderr.write(
            "Tier-2 database not found at "
            f"{t2.db_path}.\n"
            "Build it first:\n"
            "    python scripts/fetch_open_us_law.py --sample 100\n"
            "    python scripts/fetch_open_us_law.py --full\n"
        )
        return 3

    if args.stats:
        print(json.dumps(t2.stats(), indent=2, sort_keys=True))
        return 0

    if args.citation:
        hits = t2.lookup_citation(args.citation)
    else:
        hits = t2.search(
            args.query,
            state=args.state,
            collection=args.collection,
            limit=args.limit,
        )

    if not hits:
        print("No results.", file=sys.stderr)

    for hit in hits:
        print(format_result(hit))
        print("-" * 72)

    print()
    print(DISCLAIMER)
    return 0


if __name__ == "__main__":
    sys.exit(main())
