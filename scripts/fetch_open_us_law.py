"""Fetch the HuggingFace dataset ``vaquill/open-us-law`` into a local SQLite FTS5 database.

License/attribution
-------------------
Open US Law dataset by Vaquill AI
(https://huggingface.co/datasets/vaquill/open-us-law), CC-BY-4.0.

The fetched data is redistributed in this local SQLite database under the same
CC-BY-4.0 terms. Re-verify every result against the official government source
before relying on it — the recorded ``source_url`` is dataset provenance and
may be absent or point to a non-government mirror. ``act_status`` is
``"in_force"`` for refreshed rows; any other value (e.g. ``"snapshot"``,
``"repealed"``, ``"reserved"``, ``"transferred"``, ``"renumbered"``) carries
unknown good-law status. Tier-2 currency is not uniform.

Usage
-----
Sample mode (default; urllib only, no heavy deps)::

    python scripts/fetch_open_us_law.py --sample 100

Full mode (requires ``pip install huggingface_hub pyarrow``)::

    python scripts/fetch_open_us_law.py --full --dest /path/to/db.sqlite3
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
import urllib.request
from collections.abc import Iterable, Iterator
from datetime import datetime, timezone
from pathlib import Path

DATASET_ID = "vaquill/open-us-law"


def _allowed_roots() -> tuple[Path, ...]:
    """Roots a user-supplied path is permitted to resolve into.

    The user's own home directory, this repository, and the per-user temporary
    directory (building a throwaway database under ``tmp`` is ordinary usage and
    is not a privilege boundary). Everything else — /etc, /usr, /System, another
    user's home — is out of bounds for a dataset fetcher.
    """
    return (
        Path.home().resolve(),
        Path(__file__).resolve().parent.parent,
        Path(tempfile.gettempdir()).resolve(),
    )


def _safe_path(candidate, *, what: str) -> Path:
    """Resolve `candidate` and refuse it if it escapes the allowed roots.

    Resolution follows ``..`` and symlinks first, so ``/tmp/../etc/cron.d/x``
    and ``~/../../etc/x`` are both caught. The check runs BEFORE any filesystem
    call, so a refused path never leaves a directory or file behind.

    This script is documented for attorneys to run directly and is increasingly
    run by an agent on their behalf, so a malformed or attacker-influenced
    ``--dest`` / ``--cache-dir`` must not be able to create or replace anything
    outside the user's own space.
    """
    resolved = Path(candidate).expanduser().resolve()
    for root in _allowed_roots():
        if resolved == root or root in resolved.parents:
            return resolved
    permitted = " or ".join(str(root) for root in _allowed_roots())
    raise ValueError(
        f"{what} resolves outside the permitted area: {resolved}. Choose a path under {permitted}."
    )


SCHEMA_COLUMNS: list[str] = [
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

_INT_COLUMNS = frozenset({"word_count", "last_amended_year", "subsection_count", "year"})


def _column_defs() -> str:
    parts: list[str] = []
    for col in SCHEMA_COLUMNS:
        if col in _INT_COLUMNS:
            parts.append(f"{col} INTEGER")
        else:
            parts.append(f"{col} TEXT")
    return ",\n    ".join(parts)


def _normalize(value):
    if value is None:
        return None
    if isinstance(value, (list, dict)):
        return json.dumps(value)
    return value


def parse_first_rows(payload: dict) -> list[dict]:
    out: list[dict] = []
    rows = payload.get("rows") or []
    for entry in rows:
        if not isinstance(entry, dict):
            continue
        # /first-rows is a truncating preview API — a clipped statute text
        # must never be indexed as if complete
        if entry.get("truncated_cells"):
            continue
        row = entry.get("row") or {}
        if not isinstance(row, dict):
            row = {}
        normalized: dict = {}
        for col in SCHEMA_COLUMNS:
            normalized[col] = _normalize(row.get(col))
        out.append(normalized)
    return out


def _chunked(iterable: Iterable, size: int) -> Iterator[list]:
    chunk: list = []
    for item in iterable:
        chunk.append(item)
        if len(chunk) >= size:
            yield chunk
            chunk = []
    if chunk:
        yield chunk


def build_db(
    db_path,
    rows_by_collection: dict,
    mode: str,
    fetched_at: str,
    extra_manifest: dict | None = None,
) -> None:
    db_path = _safe_path(db_path, what="--dest")
    db_path.parent.mkdir(parents=True, exist_ok=True)

    ddl = (
        "CREATE TABLE sections (\n"
        "    id INTEGER PRIMARY KEY AUTOINCREMENT,\n"
        "    collection TEXT NOT NULL,\n"
        f"    {_column_defs()}\n"
        ");\n"
        "CREATE INDEX idx_sections_citation_lower ON sections(lower(citation));\n"
        "CREATE INDEX idx_sections_citation_short_lower "
        "ON sections(lower(citation_short));\n"
        "CREATE INDEX idx_sections_act_id_lower ON sections(lower(act_id));\n"
        "CREATE INDEX idx_sections_state ON sections(state);\n"
        "CREATE VIRTUAL TABLE sections_fts USING fts5(\n"
        "    citation, section_title, text,\n"
        "    content='sections', content_rowid='id'\n"
        ");\n"
        "CREATE TABLE manifest (\n"
        "    key TEXT PRIMARY KEY,\n"
        "    value TEXT\n"
        ");\n"
    )

    fd, tmp_str = tempfile.mkstemp(
        prefix=db_path.name + ".",
        suffix=".tmp",
        dir=str(db_path.parent),
    )
    os.close(fd)
    tmp_path = Path(tmp_str)

    try:
        conn = sqlite3.connect(tmp_path)
        try:
            conn.executescript(ddl)

            insert_cols = ["collection"] + SCHEMA_COLUMNS
            placeholders = ",".join("?" for _ in insert_cols)
            insert_sql = f"INSERT INTO sections ({','.join(insert_cols)}) VALUES ({placeholders})"

            counts: dict[str, int] = {}
            for collection, rows in rows_by_collection.items():
                count = 0
                for chunk in _chunked(rows, 5000):
                    batch: list[tuple] = []
                    for row in chunk:
                        if not isinstance(row, dict):
                            continue
                        values: list = [collection]
                        for col in SCHEMA_COLUMNS:
                            values.append(_normalize(row.get(col)))
                        batch.append(tuple(values))
                    if batch:
                        conn.executemany(insert_sql, batch)
                        count += len(batch)
                counts[collection] = count

            conn.execute(
                "INSERT INTO sections_fts(rowid, citation, section_title, text) "
                "SELECT id, citation, section_title, text FROM sections"
            )

            manifest_entries: list[tuple] = [
                ("dataset", DATASET_ID),
                ("license", "CC-BY-4.0"),
                ("mode", mode),
                ("fetched_at", fetched_at),
                (
                    "attribution",
                    "Open US Law dataset by Vaquill AI "
                    "(huggingface.co/datasets/vaquill/open-us-law), CC-BY-4.0",
                ),
            ]
            for coll, count in counts.items():
                manifest_entries.append((f"rows_{coll}", str(count)))
            for key, value in (extra_manifest or {}).items():
                manifest_entries.append((str(key), str(value)))

            conn.executemany(
                "INSERT INTO manifest (key, value) VALUES (?, ?)",
                manifest_entries,
            )
            conn.commit()

            # validate BEFORE os.replace — a bad build must never clobber
            # an existing good database
            total = sum(counts.values())
            if total == 0:
                raise RuntimeError(
                    "refusing to install an empty database (0 rows fetched); "
                    "existing database, if any, left untouched"
                )
            (integrity,) = conn.execute("PRAGMA quick_check").fetchone()
            if integrity != "ok":
                raise RuntimeError(f"integrity check failed on new build: {integrity}")
            (fts_count,) = conn.execute("SELECT count(*) FROM sections_fts").fetchone()
            if fts_count != total:
                raise RuntimeError(f"FTS index rows ({fts_count}) != sections rows ({total})")
        finally:
            conn.close()

        os.replace(tmp_path, db_path)
    except BaseException:
        if tmp_path.exists():
            try:
                tmp_path.unlink()
            except OSError:
                pass
        raise


def fetch_sample(n_per_collection: int = 100) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for config in ("statutes", "constitutions"):
        url = (
            "https://datasets-server.huggingface.co/first-rows"
            "?dataset=vaquill%2Fopen-us-law"
            f"&config={config}&split=train"
        )
        req = urllib.request.Request(url)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            raise RuntimeError(
                f"Failed to fetch sample for config {config!r} from {url}: {exc}"
            ) from exc
        rows = parse_first_rows(payload)
        out[config] = list(rows[:n_per_collection])
    return out


def _parquet_rows(parquet_path: Path) -> Iterator[dict]:
    import pyarrow.parquet as pq  # lazy

    pf = pq.ParquetFile(str(parquet_path))
    for batch in pf.iter_batches(batch_size=5000):
        cols = batch.column_names
        for i in range(len(batch)):
            row: dict = {}
            for col in SCHEMA_COLUMNS:
                if col in cols:
                    row[col] = _normalize(batch.column(col)[i].as_py())
                else:
                    row[col] = None
            yield row


def fetch_full(cache_dir=None) -> tuple[dict[str, Iterator[dict]], str]:
    # Validate arguments before anything else — a hostile --cache-dir must be
    # refused whether or not the optional dependencies happen to be installed.
    if cache_dir is None:
        cache_dir = Path.home() / ".cache" / "huggingface" / "vaquill_open_us_law"
    cache_dir = _safe_path(cache_dir, what="--cache-dir")

    try:
        import pyarrow.parquet  # noqa: F401
        from huggingface_hub import HfApi, snapshot_download
    except ImportError as exc:
        raise SystemExit(
            "full mode requires `pip install huggingface_hub pyarrow` "
            "(fetch-time only; the runtime layer stays stdlib)"
        ) from exc

    try:
        revision = HfApi().dataset_info(DATASET_ID).sha or "unknown"
    except Exception:
        revision = "unknown"

    cache_dir.mkdir(parents=True, exist_ok=True)

    snapshot_download(
        repo_id=DATASET_ID,
        repo_type="dataset",
        allow_patterns=["*.parquet"],
        local_dir=str(cache_dir),
    )

    parquet_files = sorted(cache_dir.rglob("*.parquet"))

    def _gen(files: list[Path]) -> Iterator[dict]:
        for f in files:
            yield from _parquet_rows(f)

    grouped: dict[str, list[Path]] = {"statutes": [], "constitutions": []}
    for f in parquet_files:
        if any("constitution" in p.lower() for p in f.parts):
            grouped["constitutions"].append(f)
        else:
            grouped["statutes"].append(f)

    return {coll: _gen(files) for coll, files in grouped.items()}, revision


def _default_dest() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "_statute_corpus" / "_tier2_open_us_law" / "open_us_law.sqlite3"


def _verify_db(db_path: Path) -> dict[str, str]:
    uri = Path(db_path).resolve().as_uri() + "?mode=ro"
    conn = sqlite3.connect(uri, uri=True)
    try:
        stats: dict[str, str] = {}
        cur = conn.execute("SELECT key, value FROM manifest")
        for key, value in cur.fetchall():
            stats[key] = value
        return stats
    finally:
        conn.close()


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(
        prog="fetch_open_us_law",
        description=(
            "Fetch vaquill/open-us-law into a local SQLite FTS5 database. "
            "Sample mode is stdlib-only; full mode requires "
            "huggingface_hub and pyarrow."
        ),
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--sample",
        type=int,
        nargs="?",
        const=100,
        default=None,
        help="Sample mode (urllib only); optional N per collection (default 100).",
    )
    group.add_argument(
        "--full",
        action="store_true",
        help="Full mode (requires pip install huggingface_hub pyarrow).",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=_default_dest(),
        help="Destination SQLite path.",
    )
    parser.add_argument(
        "--cache-dir",
        type=Path,
        default=None,
        help="Cache directory for parquet files (full mode only).",
    )

    args = parser.parse_args(argv)

    sample_n = 100
    if args.full:
        mode = "full"
    elif args.sample is not None:
        mode = "sample"
        sample_n = args.sample
    else:
        mode = "sample"

    fetched_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    dest: Path = _safe_path(args.dest, what="--dest")
    dest.parent.mkdir(parents=True, exist_ok=True)

    if mode == "sample":
        rows_by_collection = fetch_sample(n_per_collection=sample_n)
        revision = "first-rows-api (unpinned preview)"
    else:
        rows_by_collection, revision = fetch_full(cache_dir=args.cache_dir)

    build_db(
        dest,
        rows_by_collection,
        mode=mode,
        fetched_at=fetched_at,
        extra_manifest={"dataset_revision": revision},
    )

    stats = _verify_db(dest)
    print("Read-back manifest:")
    for key, value in stats.items():
        print(f"  {key} = {value}")

    total = sum(int(v) for k, v in stats.items() if k.startswith("rows_"))
    if total == 0:
        print("ERROR: total rows == 0", file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
