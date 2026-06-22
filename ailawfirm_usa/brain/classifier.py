"""
Brain classifier — rule-based intent detection for USA v0.1.

v0.1 strategy: simple keyword matching. Fast, deterministic, no LLM cost.
Order matters — first match wins.

PROVENANCE: TRAINED for US legal keyword set.
CITED:01-court-hierarchy.md, CITED:10-bar-rule-publicity-solicitation.md,
CITED:13-citation-format-primary.md, CITED:04-statute-data-protection.md
"""

from ailawfirm_usa.brain.intents import Intent

_RULES: list[tuple[list[str], Intent]] = [
    (["add to calendar", "calendar entry", "schedule for", "new calendar"], Intent.CALENDAR_ADD),
    (["calendar", "schedule", "docket", "hearing date", "conference call"], Intent.CALENDAR_QUERY),
    (
        [
            "citation",
            "bluebook",
            " u.s. ",
            " usc ",
            " cfr ",
            "scotus",
            "cite",
            " f.3d ",
            " f.supp ",
            " f.4th ",
            " s. ct. ",
        ],
        Intent.CITATION_LOOKUP,
    ),
    (
        [
            "court",
            "scotus",
            "circuit",
            "district court",
            "bankruptcy court",
            "appeals",
            "federal court",
            "state court",
            "supreme court of",
            "jurisdiction",
            "venue",
            "removal",
        ],
        Intent.COURT_QUERY,
    ),
    (
        [
            "draft",
            "drafting",
            "complaint",
            "answer",
            "motion",
            "brief",
            "memorandum",
            "pleading",
            "discovery request",
        ],
        Intent.DRAFTING_NEED,
    ),
    (
        [
            "deadline",
            "statute of limitations",
            "limitations period",
            "filing deadline",
            "service deadline",
            "answer due",
            "due date",
            "limitation period",
        ],
        Intent.DEADLINE_CHECK,
    ),
    (
        [
            "client said",
            "client called",
            "client wants",
            "client emailed",
            "client confirmed",
            "client asked",
        ],
        Intent.CLIENT_COMM,
    ),
    (
        [
            "aba",
            "model rule",
            "rule 7",
            "rule 5.5",
            "rule 1.6",
            "ccpa",
            "cpra",
            "ny shield",
            "cta",
            "fincen",
            "publicity",
            "solicit",
            "advertis",
            "ethics opinion 512",
            "ai ethics",
            "uda",
            "bsa",
            "money laundering",
            "corporate transparency",
            "dgcl",
            "conflict of interest",
            "confidentiality",
            "attorney-client privilege",
        ],
        Intent.COMPLIANCE_FLAG,
    ),
    (
        [
            "matter",
            "hearing",
            "filed",
            "served",
            "discovery",
            "deposition",
            "interrogatories",
            "subpoena",
        ],
        Intent.MATTER_UPDATE,
    ),
]


def classify(payload: str) -> Intent:
    """Classify user input into a single intent. First match wins."""
    p = payload.lower()
    for keywords, intent in _RULES:
        if any(k in p for k in keywords):
            return intent
    return Intent.UNKNOWN
