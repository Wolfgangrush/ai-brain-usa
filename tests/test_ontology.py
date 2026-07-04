"""Tests for ontology module — USA v0.1."""

from ailawfirm_usa.core.ontology import (
    USState,
    MatterType,
    USCourt,
    USStatute,
    USBarRule,
    Matter,
    Citation,
)


def test_all_50_states_plus_dc():
    state_count = len(
        [s for s in USState if s not in (USState.PR, USState.VI, USState.GU, USState.OTHER)]
    )
    assert state_count >= 51, f"Expected 50 states + DC (51), got {state_count}"


def test_state_enum_has_ca_tx_ny_fl_il_de():
    for code in ["CA", "TX", "NY", "FL", "IL", "DE"]:
        state = USState[code]
        assert state is not None


def test_matter_type_has_federal_civil():
    assert MatterType.FEDERAL_CIVIL.value == "Federal Civil Action"


def test_matter_type_has_bankruptcy_chapters():
    assert MatterType.FEDERAL_BANKRUPTCY_7.value == "Chapter 7 Bankruptcy"
    assert MatterType.FEDERAL_BANKRUPTCY_11.value == "Chapter 11 Bankruptcy"
    assert MatterType.FEDERAL_BANKRUPTCY_13.value == "Chapter 13 Bankruptcy"


def test_matter_type_has_antitrust():
    assert MatterType.FEDERAL_ANTITRUST.value == "Antitrust Action"


def test_us_court_has_scotus():
    assert USCourt.SCOTUS.value == "Supreme Court of the United States"


def test_us_court_has_all_13_circuits():
    circuit_names = [c.name for c in USCourt if c.name.startswith("FED_CIRCUIT_")]
    assert len(circuit_names) == 13  # 12 regional (1-11 + DC) + Federal Circuit


def test_us_court_has_bankruptcy():
    assert USCourt.FED_BANKRUPTCY.value == "U.S. Bankruptcy Court"


def test_us_statute_includes_frcp():
    assert USStatute.FRCP.value == "Federal Rules of Civil Procedure"


def test_us_statute_includes_ccpa():
    assert "California Consumer Privacy Act" in USStatute.CCPA_CPRA.value


def test_us_statute_includes_cta_with_currency_warning():
    assert "CURRENCY" in USStatute.CTA.value


def test_us_bar_rule_includes_mr_7():
    assert "Rule 7" in USBarRule.ABA_MR_7.value
    assert "publicity" in USBarRule.ABA_MR_7.value.lower()


def test_us_bar_rule_includes_opinion_512():
    assert "512" in USBarRule.ABA_OPINION_512.value
    assert "AI" in USBarRule.ABA_OPINION_512.value


def test_no_duplicate_matter_type_values():
    values = [m.value for m in MatterType]
    assert len(values) == len(set(values)), "Duplicate MatterType values"


def test_no_duplicate_court_values():
    values = [c.value for c in USCourt]
    assert len(values) == len(set(values)), "Duplicate USCourt values"


def test_no_duplicate_statute_values():
    values = [s.value for s in USStatute]
    assert len(values) == len(set(values)), "Duplicate USStatute values"


def test_matter_dataclass_minimal():
    m = Matter(
        matter_id="FED-SDNY-2026-001",
        matter_type=MatterType.FEDERAL_CIVIL,
        court=USCourt.FED_DISTRICT,
        short_title="Smith v. Jones",
    )
    assert m.matter_id == "FED-SDNY-2026-001"
    assert m.matter_type == MatterType.FEDERAL_CIVIL
    assert m.court == USCourt.FED_DISTRICT
    assert m.parties_plaintiff == []
    assert m.statutes_invoked == []


def test_matter_with_state():
    m = Matter(
        matter_id="CA-SF-2026-002",
        matter_type=MatterType.STATE_CIVIL,
        court=USCourt.STATE_TRIAL,
        state=USState.CA,
        short_title="Doe v. Roe",
    )
    assert m.state == USState.CA


def test_citation_dataclass_minimal():
    c = Citation(raw="347 U.S. 483 (1954)", format="SCOTUS")
    assert c.raw == "347 U.S. 483 (1954)"
    assert c.format == "SCOTUS"
    assert c.valid is False  # default
