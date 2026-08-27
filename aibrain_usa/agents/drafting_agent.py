"""USA drafting agent — FRCP document-type router.

Classifies an intake into a US federal civil document type and points
the caller at the `draft-with-docx` skill. No local template files
exist in this package; the skill is expected to be invoked with the
case folder and the operative court's local rules.
"""

from __future__ import annotations

import re
from typing import Any, Dict

AGENT_NAME = "drafting_agent"
SUGGESTED_SKILL = "draft-with-docx"
NEXT_STEP = (
    "Invoke draft-with-docx with the case folder; "
    "confirm the local rules of the operative federal/state court."
)
NOTE = (
    "US federal civil drafting is governed by the Federal Rules of Civil "
    "Procedure (FRCP). Local rules of the operative court may add or "
    "modify requirements (page limits, ECF formatting, caption form). "
    "This package does not ship templates; use the draft-with-docx skill."
)


def _classify(payload: str) -> str:
    text = (payload or "").lower()

    # Complaint / third-party complaint
    if re.search(r"\b(third[- ]party complaint|complaint)\b", text):
        return "Complaint"

    # Answer / counterclaim / cross-claim
    if re.search(r"\b(counterclaim|cross[- ]claim|answer)\b", text):
        return "Answer / Counterclaim"

    # Motion to dismiss / FRCP 12(b)(6)
    if re.search(r"\b(motion to dismiss|12\(b\)\(6\))\b", text):
        return "Motion to Dismiss (FRCP 12(b)(6))"

    # Summary judgment / Rule 56
    if re.search(r"\b(summary judgment|rule 56|frcp 56)\b", text):
        return "Motion for Summary Judgment (FRCP 56)"

    # Generic motion / compel / in limine
    if re.search(r"\b(in limine|compel|motion)\b", text):
        return "Motion"

    # Memorandum / brief
    if re.search(r"\b(memorandum|brief)\b", text):
        return "Memorandum of Law / Brief"

    # Discovery / interrogator* / deposition
    if re.search(r"\b(interrogator\w*|deposition|discovery)\b", text):
        return "Discovery"

    # Demand letter
    if re.search(r"\b(demand letter)\b", text):
        return "Demand Letter"

    # Default — any unrecognised or non-US drafting request falls through here.
    return "General filing (confirm doc type)"


def handle(payload: str) -> Dict[str, Any]:
    doc_type = _classify(payload)
    return {
        "agent": AGENT_NAME,
        "status": "ok",
        "doc_type": doc_type,
        "suggested_skill": SUGGESTED_SKILL,
        "next_step": NEXT_STEP,
        "note": NOTE,
    }
