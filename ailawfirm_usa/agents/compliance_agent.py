"""
compliance_agent — USA regulatory firewall (v0.1).

Detects ABA Model Rule / CCPA / FinCEN / AI ethics keyword classes
and returns structured compliance flags.

PROVENANCE: CITED:10-bar-rule-publicity-solicitation.md,
CITED:04-statute-data-protection.md, CITED:23-ai-law-firm-regulatory-stance.md,
CITED:27-anti-money-laundering-obligations.md
"""

from ailawfirm_usa.core.ontology import USBarRule


def handle(payload: str) -> dict:
    p = payload.lower()
    flags = []

    if any(
        k in p
        for k in [
            "publicity",
            "solicit",
            "advertis",
            "client recruitment",
            "testimonial",
            "success rate",
        ]
    ):
        flags.append(
            {
                "rule": USBarRule.ABA_MR_7.value,
                "concern": "State bar variations apply · check your state's adoption of ABA MR 7",
                "research_ref": "10-bar-rule-publicity-solicitation.md",
            }
        )

    if any(
        k in p
        for k in [
            "ai ethics",
            "ai use",
            "ai tool",
            "generative ai",
            "chatgpt",
            "claude",
            "artificial intelligence",
        ]
    ):
        flags.append(
            {
                "rule": USBarRule.ABA_OPINION_512.value,
                "concern": "CURRENCY: state-specific AI opinions emerging monthly · verify your state",
                "research_ref": "23-ai-law-firm-regulatory-stance.md",
            }
        )

    if any(k in p for k in ["ccpa", "cpra", "california privacy", "consumer privacy"]):
        flags.append(
            {
                "rule": "CCPA 2018 + CPRA 2020 (California)",
                "concern": "California-specific · check if matter touches CA residents",
                "research_ref": "04-statute-data-protection.md",
            }
        )

    if any(k in p for k in ["ny shield", "new york data breach", "stop hacks"]):
        flags.append(
            {
                "rule": "NY SHIELD Act",
                "concern": "New York data breach notification requirements",
                "research_ref": "04-statute-data-protection.md",
            }
        )

    if any(
        k in p
        for k in [
            "bsa",
            "ctr",
            "fincen",
            "money laundering",
            "cta",
            "corporate transparency",
            "beneficial ownership",
        ]
    ):
        flags.append(
            {
                "rule": "BSA + Corporate Transparency Act — FinCEN reporting",
                "concern": "CURRENCY: CTA enforcement rolling out · BOI reporting deadlines vary",
                "research_ref": "27-anti-money-laundering-obligations.md",
            }
        )

    if any(
        k in p
        for k in ["multijurisdictional", "pro hac vice", "out of state", "unauthorized practice"]
    ):
        flags.append(
            {
                "rule": USBarRule.ABA_MR_5_5.value,
                "concern": "Multijurisdictional practice restrictions · pro hac vice may be required",
                "research_ref": "11-bar-rule-conflict-of-interest.md",
            }
        )

    if any(k in p for k in ["conflict", "adverse", "former client", "concurrent client"]):
        flags.append(
            {
                "rule": "ABA Model Rules 1.7-1.11 — conflict of interest",
                "concern": "Conflict check required before engagement",
                "research_ref": "11-bar-rule-conflict-of-interest.md",
            }
        )

    if any(k in p for k in ["confidential", "privilege", "attorney-client", "work product"]):
        flags.append(
            {
                "rule": USBarRule.ABA_MR_1_6.value,
                "concern": "Confidentiality obligations under ABA MR 1.6 · waiver risk",
                "research_ref": "12-bar-rule-confidentiality.md",
            }
        )

    if "uda" in p or "uniform digital assets" in p or "ucc article 12" in p:
        flags.append(
            {
                "rule": "UCC Article 12 (Digital Assets) — 2022 Amendments",
                "concern": "CURRENCY: state-by-state adoption · check your state's status",
                "research_ref": "05-statute-contract-law-overview.md",
            }
        )

    return {
        "agent": "compliance_agent",
        "status": "v0.1 — USA Federal+State firewall",
        "flags": flags,
        "note": "CURRENCY: ABA Opinion 512 + TCJA Sunset 2025 + UCC Article 12 tracked",
    }
