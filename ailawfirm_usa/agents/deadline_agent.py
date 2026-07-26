"""USA deadline agent — honest 50-state framing.

There is NO single federal statute of limitations in the United States.
This agent classifies the claim, surfaces the common range + the
controlling framework, and explicitly tells the caller to verify their
state. It NEVER fabricates a single authoritative computed deadline.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Any, Dict, Optional, Tuple

AGENT_NAME = "deadline_agent"
DEFAULT_NOTE = (
    "No single US limitation statute — each state sets its own; federal "
    "claims carry their own deadlines. UCC §2-725 (sale of goods, 4 years) "
    "is near-uniform. Tolling (minority, discovery rule, defendant absence) "
    "and shorter government-claim notice periods apply. Verify your state's "
    "statute of limitations."
)

_MONTHS = {
    "january": 1, "february": 2, "march": 3, "april": 4,
    "may": 5, "june": 6, "july": 7, "august": 8,
    "september": 9, "october": 10, "november": 11, "december": 12,
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "jun": 6, "jul": 7,
    "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}


def _classify(payload: str) -> Tuple[str, str, str]:
    """Return (category, period, article) per first-match-wins rules."""
    text = (payload or "").lower()

    # 1. Sale of goods / UCC / goods
    if re.search(r"\b(sale of goods|goods|uniform commercial code|UCC)\b", text):
        return (
            "Sale of goods (UCC)",
            "4 years",
            "UCC §2-725 (near-uniform across states)",
        )

    # 2. Personal injury / accident / injury
    if re.search(r"\b(personal injur\w*|accident|injury)\b", text):
        return (
            "Personal injury",
            "commonly 2 years (varies 1-6 by state)",
            "State statute of limitations — varies by state; verify your state",
        )

    # 3. Written contract
    if re.search(r"\b(written contract|contract in writing)\b", text):
        return (
            "Written contract",
            "commonly 4-6 years (up to 10 in some states)",
            "State statute of limitations — varies by state; verify your state",
        )

    # 4. Oral contract
    if re.search(r"\b(oral contract|verbal contract|oral agreement)\b", text):
        return (
            "Oral contract",
            "commonly 2-4 years (varies by state)",
            "State statute of limitations — varies by state; verify your state",
        )

    # 5. Contract / breach / debt (general)
    if re.search(r"\b(contract|breach|debt)\b", text):
        return (
            "Contract",
            "commonly 4-6 years (varies by state)",
            "State statute of limitations — varies by state; verify your state",
        )

    # 6. Tort / negligence / property / damage
    if re.search(r"\b(tort|negligence|property|damage)\b", text):
        return (
            "Tort / property damage",
            "commonly 2-3 years (varies by state)",
            "State statute of limitations — varies by state; verify your state",
        )

    # 7. Default
    return (
        "General civil claim",
        "varies by state",
        "No single federal statute of limitations — each state sets its own; verify your state",
    )


def _extract_start_date(payload: str) -> Optional[str]:
    """Best-effort extraction of a start date. Returns ISO-8601 or None.

    A start date, if found, is recorded for reference only. The agent
    still does NOT present a lone precise deadline as authoritative.
    """
    text = payload or ""

    # ISO: YYYY-MM-DD
    m = re.search(r"\b(\d{4})-(\d{2})-(\d{2})\b", text)
    if m:
        try:
            d = date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            return d.isoformat()
        except ValueError:
            pass

    # "12 January 2020" or "12 Jan 2020"
    m = re.search(r"\b(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})\b", text)
    if m:
        mon = m.group(2).lower()
        if mon in _MONTHS:
            try:
                d = date(int(m.group(3)), _MONTHS[mon], int(m.group(1)))
                return d.isoformat()
            except ValueError:
                pass

    # "January 12, 2020" or "Jan 12 2020"
    m = re.search(r"\b([A-Za-z]+)\s+(\d{1,2})(?:,)?\s+(\d{4})\b", text)
    if m:
        mon = m.group(1).lower()
        if mon in _MONTHS:
            try:
                d = date(int(m.group(3)), _MONTHS[mon], int(m.group(2)))
                return d.isoformat()
            except ValueError:
                pass

    return None


def handle(payload: str) -> Dict[str, Any]:
    """Classify a US limitation-of-action question.

    Never fabricates a single authoritative deadline. Always sets
    deadline=None and days_remaining=None; may record a start date if
    one is found in the text.
    """
    category, period, article = _classify(payload)
    start_date = _extract_start_date(payload)

    return {
        "agent": AGENT_NAME,
        "status": "ok",
        "category": category,
        "period": period,
        "article": article,
        "start_date": start_date,
        "deadline": None,
        "days_remaining": None,
        "note": DEFAULT_NOTE,
    }
