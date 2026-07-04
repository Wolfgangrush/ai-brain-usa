"""Tests for usa_citation_validator MCP tool — USA v0.1 (Bluebook 21st ed)."""

from ailawfirm_usa.mcp_tools.usa_citation_validator import usa_citation_validator


def test_scotus_case_brown():
    result = usa_citation_validator("Brown v. Board of Education, 347 U.S. 483 (1954)")
    assert result["valid"] is True
    assert result["format"] == "SCOTUS"
    assert result["volume"] == 347
    assert result["reporter"] == "U.S."
    assert result["page"] == 483


def test_circuit_case_f3d():
    result = usa_citation_validator("United States v. Caseres, 122 F.3d 1274 (9th Cir. 1997)")
    assert result["valid"] is True
    assert result["format"] == "FED_CIRCUIT"
    assert result["volume"] == 122
    assert "F.3d" in result["reporter"]


def test_district_case_fsupp3d():
    result = usa_citation_validator("Abbott v. United States, 111 F. Supp. 2d 111 (D. Mass. 2000)")
    assert result["valid"] is True
    assert result["format"] == "FED_DISTRICT"


def test_usc_citation():
    result = usa_citation_validator("42 U.S.C. § 1983")
    assert result["valid"] is True
    assert result["format"] == "USC"
    assert result["title_num"] == 42
    assert result["section"] == "1983"


def test_usc_citation_with_year():
    result = usa_citation_validator("42 U.S.C. § 1983 (2018)")
    assert result["valid"] is True
    assert result["year"] == 2018


def test_cfr_citation():
    result = usa_citation_validator("29 C.F.R. § 825.100 (2024)")
    assert result["valid"] is True
    assert result["format"] == "CFR"
    assert result["title_num"] == 29
    assert result["section"] == "825.100"


def test_constitution():
    result = usa_citation_validator("U.S. Const. art. III, § 1")
    assert result["valid"] is True
    assert result["format"] == "CONSTITUTION"
    assert result["article"] == "III"


def test_unknown_format():
    result = usa_citation_validator("this is not a citation")
    assert result["valid"] is False
    assert result["format"] == "UNKNOWN"


def test_non_string_input():
    result = usa_citation_validator(None)
    assert result["valid"] is False
    assert "not a string" in result["parse_notes"]


def test_empty_string():
    result = usa_citation_validator("")
    assert result["valid"] is False
