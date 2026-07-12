"""
citation_agent — citation parsing + validation (v0.1.1).

v0.1.1: extracts a US Bluebook citation string from natural-language payload,
        then wraps the usa_citation_validator MCP tool.
v0.2+:  adds CourtListener / Google Scholar case-existence lookup.

PROVENANCE: TRAINED for citation formats (see KNOWLEDGE_PROVENANCE.md).
"""

import re
from ailawfirm_usa.mcp_tools.usa_citation_validator import usa_citation_validator


# Patterns to lift a US (Bluebook) citation out of a wrapping sentence.
# Order matters — try most-specific first. The validator understands U.S.,
# S. Ct., F.2d/3d/4th, F. Supp., U.S.C., C.F.R., and the U.S. Constitution.
_EXTRACTORS = [
    # Case reporters: "347 U.S. 483", "122 F.3d 1274", "111 F. Supp. 2d 111"
    re.compile(
        r"\b\d+\s+(?:U\.\s?S\.|S\.\s?Ct\.|F\.\s?\d?d|F\.4th|F\.\s?Supp\.\s?\d?d?|"
        r"L\.\s?Ed\.\s?\d?d?|P\.\s?\d?d|A\.\s?\d?d|So\.\s?\d?d|N\.E\.\s?\d?d|N\.W\.\s?\d?d)\s+\d+\b"
    ),
    # Statutes / regs: "42 U.S.C. § 1983", "29 C.F.R. § 825.100"
    re.compile(r"\b\d+\s+(?:U\.S\.C\.|C\.F\.R\.)\s+§+\s*[\d.()a-zA-Z\-]+"),
    # US Constitution
    re.compile(r"\bU\.S\.\s+Const\.\s+art\.?\s*[IVX]+[^.,;]*"),
    # Indian-diaspora reporters (kept LAST — only for South Asian diaspora matters)
    re.compile(r"\bAIR\s+\d{4}\s+[A-Z][A-Za-z]*\s+\d+\b"),
    re.compile(r"\(\d{4}\)\s+\d+\s+SCC\s+\d+"),
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
            "validate Heintz v. Jenkins, 514 U.S. 291" → extracts "514 U.S. 291" → validates.
    """
    cite = _extract_citation(payload)
    result = usa_citation_validator(cite)
    return {
        "agent": "citation_agent",
        "status": "v0.1.1 — NL-extracted citation, then validated",
        "extracted": cite,
        "result": result,
    }
