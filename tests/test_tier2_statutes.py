"""Acceptance tests for the Tier-2 Open US Law statutory layer.

Authored by the orchestrator (Opus firewall discipline) — the implementation
must satisfy these tests; the tests are never edited to fit the implementation.

Architecture under test:
  Tier-1 = curated ``_statute_corpus`` digests (STATUS: VERIFIED, hand-shaped).
  Tier-2 = ``vaquill/open-us-law`` full-text lookup (CC-BY-4.0), fetched into
           a local SQLite FTS5 database by ``scripts/fetch_open_us_law.py`` and
           queried by ``ailawfirm_usa.tier2_statutes`` (stdlib only at runtime).
"""

import importlib.util
import sys
from pathlib import Path

import pytest

from ailawfirm_usa import tier2_statutes
from ailawfirm_usa.tier2_statutes import DISCLAIMER, Tier2Statutes

REPO_ROOT = Path(__file__).resolve().parent.parent

_spec = importlib.util.spec_from_file_location(
    "fetch_open_us_law", REPO_ROOT / "scripts" / "fetch_open_us_law.py"
)
fetcher = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fetcher)

SCHEMA_COLUMNS = [
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


def _row(**over):
    base = {
        "act_id": "STATE_AK_T11_C11.76_S11.76.115",
        "citation": "Alaska Stat. § 11.76.115",
        "citation_short": "Alaska Stat. § 11.76.115",
        "state": "ak",
        "jurisdiction": "US",
        "document_type": "statute",
        "title_number": "11",
        "title_name": "AK Code",
        "chapter": "11.76",
        "chapter_name": None,
        "section_number": "11.76.115",
        "section_title": "Misconduct involving confidential information",
        "breadcrumb": "[]",
        "display_path": "AK Code / Title 11 / Chapter 11.76 / Section 11.76.115",
        "act_status": "in_force",
        "text": "A person commits the crime of misconduct involving "
        "confidential information in the second degree.",
        "word_count": 15,
        "source_url": "https://www.akleg.gov/basis/statutes.asp?title=11#11.76.115",
        "last_amended_year": 2019,
        "subsection_count": 4,
        "cross_references_usc": "[]",
        "cross_references_cfr": "[]",
        "public_laws_referenced": "[]",
        "year": 2026,
    }
    base.update(over)
    return base


FIXTURE_ROWS = {
    "statutes": [
        _row(),
        _row(
            act_id="STATE_CA_CIV_S1798.100",
            citation="Cal. Civ. Code § 1798.100",
            citation_short="Cal. Civ. Code § 1798.100",
            state="ca",
            title_number="1798",
            section_number="1798.100",
            section_title="General duties of businesses that collect personal information",
            text="A business that collects a consumer's personal information "
            "shall, at or before the point of collection, inform "
            "consumers of the purposes.",
            source_url="https://leginfo.legislature.ca.gov/faces/codes"
            "_displaySection.xhtml?sectionNum=1798.100",
        ),
        _row(
            act_id="STATE_TX_OCC_S2301.001",
            citation="Tex. Occ. Code § 2301.001",
            citation_short="Tex. Occ. Code § 2301.001",
            state="tx",
            act_status="snapshot",
            section_number="2301.001",
            section_title="Short title of the motor vehicle chapter",
            text="This chapter may be cited as the Texas Motor Vehicle Commission Code.",
            source_url="https://statutes.capitol.texas.gov/Docs/OC/htm/OC.2301.htm",
            last_amended_year=None,
        ),
    ],
    "constitutions": [
        _row(
            act_id="CONST_US_AMD_4",
            citation="U.S. Const. amend. IV",
            citation_short="U.S. Const. amend. IV",
            state="us",
            document_type="constitution",
            section_number="IV",
            section_title="Search and seizure",
            text="The right of the people to be secure in their persons, "
            "houses, papers, and effects, against unreasonable searches "
            "and seizures, shall not be violated.",
            source_url="https://constitution.congress.gov/constitution/amendment-4/",
        ),
    ],
}


@pytest.fixture(scope="module")
def db_path(tmp_path_factory):
    path = tmp_path_factory.mktemp("tier2") / "open_us_law.sqlite3"
    fetcher.build_db(
        path,
        FIXTURE_ROWS,
        mode="test",
        fetched_at="2026-08-05T03:30:00Z",
    )
    return path


@pytest.fixture(scope="module")
def tier2(db_path):
    return Tier2Statutes(db_path=db_path)


class TestFetcherContract:
    def test_schema_columns_pinned(self):
        assert set(fetcher.SCHEMA_COLUMNS) == set(SCHEMA_COLUMNS)

    def test_parse_first_rows(self):
        payload = {
            "features": [{"name": c} for c in SCHEMA_COLUMNS],
            "rows": [{"row_idx": 0, "row": _row(), "truncated_cells": []}],
        }
        rows = fetcher.parse_first_rows(payload)
        assert len(rows) == 1
        assert set(rows[0].keys()) == set(SCHEMA_COLUMNS)
        assert rows[0]["citation"] == "Alaska Stat. § 11.76.115"

    def test_parse_first_rows_fills_missing_keys(self):
        partial = {k: v for k, v in _row().items() if k not in ("year", "chapter")}
        payload = {"rows": [{"row": partial}]}
        rows = fetcher.parse_first_rows(payload)
        assert rows[0]["year"] is None
        assert rows[0]["chapter"] is None

    def test_build_db_atomic_and_manifest(self, db_path, tier2):
        assert db_path.exists()
        stats = tier2.stats()
        assert stats["dataset"] == "vaquill/open-us-law"
        assert stats["license"] == "CC-BY-4.0"
        assert stats["mode"] == "test"
        assert stats["fetched_at"] == "2026-08-05T03:30:00Z"
        assert int(stats["rows_statutes"]) == 3
        assert int(stats["rows_constitutions"]) == 1
        assert "vaquill" in stats["attribution"].lower()


class TestTier2Statutes:
    def test_is_available(self, tier2):
        assert tier2.is_available() is True

    def test_is_available_false_when_db_missing(self, tmp_path):
        t = Tier2Statutes(db_path=tmp_path / "nope.sqlite3")
        assert t.is_available() is False

    def test_lookup_citation_exact(self, tier2):
        hits = tier2.lookup_citation("Cal. Civ. Code § 1798.100")
        assert len(hits) == 1
        hit = hits[0]
        assert hit["state"] == "ca"
        assert "personal information" in hit["text"]
        assert hit["source_url"].startswith("https://leginfo.legislature.ca.gov")

    def test_lookup_citation_case_insensitive(self, tier2):
        hits = tier2.lookup_citation("cal. civ. code § 1798.100")
        assert len(hits) == 1
        assert hits[0]["act_id"] == "STATE_CA_CIV_S1798.100"

    def test_lookup_by_act_id(self, tier2):
        hits = tier2.lookup_citation("CONST_US_AMD_4")
        assert len(hits) == 1
        assert hits[0]["document_type"] == "constitution"

    def test_search_fts(self, tier2):
        hits = tier2.search("confidential information")
        assert hits
        assert hits[0]["act_id"] == "STATE_AK_T11_C11.76_S11.76.115"

    def test_search_state_filter(self, tier2):
        hits = tier2.search("information", state="ca")
        assert hits
        assert all(h["state"] == "ca" for h in hits)

    def test_search_collection_filter(self, tier2):
        hits = tier2.search("searches and seizures", collection="constitutions")
        assert hits
        assert all(h["document_type"] == "constitution" for h in hits)

    def test_search_limit(self, tier2):
        assert len(tier2.search("the", limit=2)) <= 2

    def test_search_no_hits_returns_empty(self, tier2):
        assert tier2.search("zzqqxx nonexistent phrase") == []

    def test_search_handles_fts_special_chars(self, tier2):
        # must not raise on FTS5 operators / quotes in user input
        assert isinstance(tier2.search('confidential "informa* OR NEAR('), list)


class TestCurrencyDiscipline:
    """The load-bearing caveat: Tier-2 currency is NOT uniform and Tier-1's
    STATUS: VERIFIED discipline does not transfer. Every result must say so."""

    def test_every_result_carries_currency_note_and_source(self, tier2):
        for hit in tier2.search("information") + tier2.lookup_citation("U.S. Const. amend. IV"):
            assert hit["currency_note"]
            assert hit["source_url"]

    def test_snapshot_status_gets_stronger_warning(self, tier2):
        hits = tier2.lookup_citation("Tex. Occ. Code § 2301.001")
        assert len(hits) == 1
        note = hits[0]["currency_note"].lower()
        assert "snapshot" in note
        assert "verif" in note  # re-verify / verification wording

    def test_in_force_still_requires_reverify(self, tier2):
        hits = tier2.lookup_citation("Alaska Stat. § 11.76.115")
        assert "verif" in hits[0]["currency_note"].lower()

    def test_module_disclaimer(self):
        low = DISCLAIMER.lower()
        assert "cc-by-4.0" in low
        assert "vaquill" in low
        assert "verif" in low


class TestRuntimeIsolation:
    def test_tier2_runtime_is_stdlib_only(self):
        # the runtime module must never drag in fetch-time heavy deps
        assert "pyarrow" not in sys.modules
        assert "huggingface_hub" not in sys.modules
        assert "datasets" not in sys.modules

    def test_missing_db_query_raises_clean_error(self, tmp_path):
        t = Tier2Statutes(db_path=tmp_path / "absent.sqlite3")
        with pytest.raises(tier2_statutes.Tier2Unavailable):
            t.search("anything")
