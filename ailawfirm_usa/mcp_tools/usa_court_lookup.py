"""
usa_court_lookup MCP tool — v0.1.

Resolves a US court name (fuzzy) to structured court info.
v0.1 covers Federal courts (SCOTUS · 5 circuits · sample districts · bankruptcy · tax).
State court detail deferred to v0.2+.

PROVENANCE: CITED:01-court-hierarchy.md
"""

from typing import Optional
from ailawfirm_usa.core.ontology import USCourt

_COURT_INFO: dict[USCourt, dict] = {
    USCourt.SCOTUS: {
        "name": "Supreme Court of the United States",
        "location": "Washington, D.C.",
        "tier": "apex",
        "jurisdiction_class": "original + appellate (certiorari) + constitutional",
        "procedural_code": "Supreme Court Rules 2023",
        "pecuniary_limit": None,
    },
    USCourt.FED_CIRCUIT_1: {
        "name": "U.S. Court of Appeals for the First Circuit",
        "location": "Boston, MA",
        "tier": "appellate",
        "jurisdiction_class": "appellate (ME, MA, NH, RI, PR)",
        "procedural_code": "FRAP + 1st Cir. Local Rules",
        "pecuniary_limit": None,
    },
    USCourt.FED_CIRCUIT_2: {
        "name": "U.S. Court of Appeals for the Second Circuit",
        "location": "New York, NY",
        "tier": "appellate",
        "jurisdiction_class": "appellate (CT, NY, VT)",
        "procedural_code": "FRAP + 2d Cir. Local Rules",
        "pecuniary_limit": None,
    },
    USCourt.FED_CIRCUIT_5: {
        "name": "U.S. Court of Appeals for the Fifth Circuit",
        "location": "New Orleans, LA",
        "tier": "appellate",
        "jurisdiction_class": "appellate (LA, MS, TX)",
        "procedural_code": "FRAP + 5th Cir. Local Rules",
        "pecuniary_limit": None,
    },
    USCourt.FED_CIRCUIT_9: {
        "name": "U.S. Court of Appeals for the Ninth Circuit",
        "location": "San Francisco, CA",
        "tier": "appellate",
        "jurisdiction_class": "appellate (CA, OR, WA, AZ, NV, ID, MT, AK, HI, GU, MP)",
        "procedural_code": "FRAP + 9th Cir. Local Rules",
        "pecuniary_limit": None,
    },
    USCourt.FED_CIRCUIT_FEDERAL: {
        "name": "U.S. Court of Appeals for the Federal Circuit",
        "location": "Washington, D.C.",
        "tier": "appellate",
        "jurisdiction_class": "appellate (patent, veterans, intl trade, federal claims — nationwide)",
        "procedural_code": "FRAP + Fed. Cir. Local Rules",
        "pecuniary_limit": None,
    },
    USCourt.FED_DISTRICT: {
        "name": "U.S. District Court (94 districts nationwide)",
        "location": "varies by district",
        "tier": "trial",
        "jurisdiction_class": "original — federal question + diversity of citizenship (>$75,000)",
        "procedural_code": "FRCP + Local Rules per district",
        "pecuniary_limit": "Diversity jurisdiction: >$75,000 (28 U.S.C. § 1332)",
    },
    USCourt.FED_BANKRUPTCY: {
        "name": "U.S. Bankruptcy Court",
        "location": "varies by district",
        "tier": "specialized_trial",
        "jurisdiction_class": "bankruptcy — 11 U.S.C. (Chapters 7, 11, 13)",
        "procedural_code": "FRBP + Local Bankruptcy Rules",
        "pecuniary_limit": None,
    },
    USCourt.FED_TAX: {
        "name": "U.S. Tax Court",
        "location": "Washington, D.C. (sessions nationwide)",
        "tier": "specialized_trial",
        "jurisdiction_class": "tax disputes — IRS deficiency determinations",
        "procedural_code": "Tax Court Rules of Practice and Procedure",
        "pecuniary_limit": None,
    },
    USCourt.FED_CLAIMS: {
        "name": "U.S. Court of Federal Claims",
        "location": "Washington, D.C.",
        "tier": "specialized_trial",
        "jurisdiction_class": "monetary claims against the United States",
        "procedural_code": "RCFC (Rules of the Court of Federal Claims)",
        "pecuniary_limit": None,
    },
}


def _fuzzy_match_court(query: str) -> Optional[USCourt]:
    q = query.lower().strip()
    if not q:
        return None
    for court in USCourt:
        name_lower = court.value.lower()
        enum_lower = court.name.lower()
        if q in name_lower or q in enum_lower:
            return court
    # partial matches — require specific legal keywords, not generic "court"
    generic_words = {"court", "of", "the", "for", "and", "state", "federal", "united", "states"}
    words = [w for w in q.split() if len(w) > 2 and w not in generic_words]
    if not words:
        return None
    for court in USCourt:
        name_lower = court.value.lower()
        if any(w in name_lower for w in words):
            return court
    return None


def usa_court_lookup(query: str) -> dict:
    """Look up a US court by name (fuzzy match).

    Args:
        query: court name fragment, e.g. "scotus", "ninth circuit", "bankruptcy", "tax"

    Returns:
        dict with court info or error
    """
    if not isinstance(query, str) or not query.strip():
        return {
            "query": str(query),
            "found": False,
            "error": "query must be a non-empty string",
        }

    court = _fuzzy_match_court(query)
    if court is None:
        return {
            "query": query,
            "found": False,
            "hint": "Try 'scotus', 'ninth circuit', 'bankruptcy', 'tax', 'federal circuit'",
        }

    info = _COURT_INFO.get(court, {})
    return {
        "query": query,
        "found": True,
        "enum": court.name,
        "display_name": court.value,
        **info,
    }
