"""Tests for usa_court_lookup MCP tool — USA v0.1."""

from ailawfirm_usa.mcp_tools.usa_court_lookup import usa_court_lookup, _fuzzy_match_court


def test_finds_scotus():
    result = usa_court_lookup("scotus")
    assert result["found"] is True
    assert result["tier"] == "apex"
    assert "Supreme Court" in result["display_name"]


def test_finds_ninth_circuit():
    result = usa_court_lookup("ninth circuit")
    assert result["found"] is True
    assert result["enum"] == "FED_CIRCUIT_9"


def test_finds_bankruptcy():
    result = usa_court_lookup("bankruptcy")
    assert result["found"] is True
    assert "Bankruptcy" in result["display_name"]


def test_finds_tax_court():
    result = usa_court_lookup("tax")
    assert result["found"] is True


def test_finds_federal_circuit():
    result = usa_court_lookup("federal circuit")
    assert result["found"] is True


def test_empty_query_returns_error():
    result = usa_court_lookup("")
    assert result["found"] is False
    assert "error" in result


def test_none_query_returns_error():
    result = usa_court_lookup(None)
    assert result["found"] is False


def test_bogus_query_not_found():
    result = usa_court_lookup("xyzzy court of neverland")
    assert result["found"] is False
    assert "hint" in result


def test_fuzzy_match_returns_none_for_empty():
    assert _fuzzy_match_court("") is None


def test_fuzzy_match_returns_none_for_nonsense():
    assert _fuzzy_match_court("xyzzy123") is None
