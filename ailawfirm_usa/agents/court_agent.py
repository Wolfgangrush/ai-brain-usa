"""
court_agent — court info + jurisdiction (v0.1.1).

v0.1.1: strips natural-language preamble ("tell me about", "what is", etc.)
        from the payload before passing to usa_court_lookup.
v0.2+:  adds cause-list scraping + bench-tracking + pecuniary lookup.

PROVENANCE: TRAINED for court info (see KNOWLEDGE_PROVENANCE.md).
"""

import re
from ailawfirm_usa.mcp_tools.usa_court_lookup import usa_court_lookup


# Common preamble phrases users wrap their question in.
_PREAMBLE_RE = re.compile(
    r"^(tell me about|what is|what's|describe|info on|info about|details on|details about|"
    r"show me|lookup|look up|find|locate|please)\s+(the\s+)?",
    re.IGNORECASE,
)
_TRAILING_RE = re.compile(r"\s*(please|kindly|thanks|thank you)\s*[.?!]*\s*$", re.IGNORECASE)


def _strip_preamble(text: str) -> str:
    if not text:
        return text
    cleaned = _PREAMBLE_RE.sub("", text.strip())
    cleaned = _TRAILING_RE.sub("", cleaned)
    return cleaned.strip().rstrip("?.!")


def handle(payload: str) -> dict:
    """Strip NL preamble, then look up court (fuzzy match handles the rest).

    v0.1.1: handles wrappings like "tell me about the Ninth Circuit" →
            extracts "Ninth Circuit" → fuzzy-matches.
    """
    cleaned = _strip_preamble(payload)
    result = usa_court_lookup(cleaned)
    return {
        "agent": "court_agent",
        "status": "v0.1.1 — preamble-stripped lookup",
        "extracted": cleaned,
        "result": result,
    }
