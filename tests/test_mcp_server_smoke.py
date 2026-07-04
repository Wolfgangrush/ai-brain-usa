"""Smoke test for MCP server — USA v0.1."""

from ailawfirm_usa.mcp_server import TOOL_TABLE, TOOL_SCHEMAS


def test_three_tools_registered():
    assert "usa_court_lookup" in TOOL_TABLE
    assert "usa_citation_validator" in TOOL_TABLE
    assert "usa_calendar_sync" in TOOL_TABLE
    assert len(TOOL_TABLE) == 3


def test_tool_schemas_match_tools():
    for name in TOOL_TABLE:
        assert name in TOOL_SCHEMAS, f"Missing schema for {name}"
