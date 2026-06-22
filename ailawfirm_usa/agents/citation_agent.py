"""
citation_agent — citation parsing + validation (v0.1.1).

v0.1.1: extracts a citation string from natural-language payload, then
        wraps india_citation_validator MCP tool.
v0.2+:  adds Manupatra / SCC OnLine / IndianKanoon lookup.

PROVENANCE: TRAINED for citation formats (see KNOWLEDGE_PROVENANCE.md).
"""

import re
from ailawfirm_india.mcp_tools.citation_validator import india_citation_validator


# Patterns to lift a citation out of a wrapping sentence.
# Order matters — try most-specific first.
_EXTRACTORS = [
    re.compile(r"\bAIR\s+\d{4}\s+[A-Z][A-Za-z]*\s+\d+\b"),
    re.compile(r"\(\d{4}\)\s+\d+\s+SCC\s+\d+"),
    re.compile(r"\b\d{4}\s+SCC\s+OnLine\s+[A-Z][A-Za-z]*\s+\d+\b"),
]


def _extract_citation(text: str) -> str:
    """Pull the first citation-shaped substring out of text. If none, return text as-is."""
    if not text:
        return text
    for pat in _EXTRACTORS:
        m = pat.search(text)
        if m:
            return m.group(0)
    return text.strip()


def handle(payload: str) -> dict:
    """Extract a citation from the payload, then validate it.

    v0.1.1: now handles natural-language wrapping like
            "validate AIR 1973 SC 1461" → extracts "AIR 1973 SC 1461" → validates.
    """
    cite = _extract_citation(payload)
    result = india_citation_validator(cite)
    return {
        "agent": "citation_agent",
        "status": "v0.1.1 — NL-extracted citation, then validated",
        "extracted": cite,
        "result": result,
    }
