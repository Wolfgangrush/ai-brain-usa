"""
Intent enum for the AI Brain USA brain layer.

PROVENANCE: STUB — v0.2+ will add LLM-based classification.
v0.1 uses rule-based keyword matching (see classifier.py).
"""

from enum import Enum


class Intent(Enum):
    """User request intents for the US legal-practice domain."""

    MATTER_UPDATE = "matter_update"
    CITATION_LOOKUP = "citation_lookup"
    COURT_QUERY = "court_query"
    DRAFTING_NEED = "drafting_need"
    DEADLINE_CHECK = "deadline_check"
    CLIENT_COMM = "client_comm"
    COMPLIANCE_FLAG = "compliance_flag"
    CALENDAR_QUERY = "calendar_query"
    CALENDAR_ADD = "calendar_add"
    UNKNOWN = "unknown"


AGENT_FOR_INTENT: dict[Intent, str] = {
    Intent.MATTER_UPDATE: "matter_agent",
    Intent.CITATION_LOOKUP: "citation_agent",
    Intent.COURT_QUERY: "court_agent",
    Intent.DRAFTING_NEED: "drafting_agent",
    Intent.DEADLINE_CHECK: "deadline_agent",
    Intent.CLIENT_COMM: "matter_agent",
    Intent.COMPLIANCE_FLAG: "compliance_agent",
    Intent.CALENDAR_QUERY: "calendar_agent",
    Intent.CALENDAR_ADD: "calendar_agent",
    Intent.UNKNOWN: "matter_agent",
}
