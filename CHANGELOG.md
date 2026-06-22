# Changelog

## [0.1.1] — 2026-06-05 · Dual-mode disclosure refinement

### Changed
- **README.md** — refined headline tagline, tier table HIPAA + DeepSeek + Claude/Gemini rows, "Why this exists" closing line, and "Privacy & Data Handling — what stays where" section to honestly disclose the dual-mode architecture (local-default · cloud-optional) and the role of the internalised Pseudonymisation Gateway as the structural privacy primitive when cloud mode is invoked. Tier table now explicitly notes that **HIPAA PHI in cloud mode requires both Gateway coverage of the specific PHI identifiers AND an executed Business Associate Agreement per 45 CFR §164.504(e)** — Gateway sanitisation alone does not discharge the BAA obligation.

  Prior wording overstated by treating local-only as architectural fact across all tiers; the architecture is in fact **local-default with cloud-optional + Gateway-sanitised cloud transmission**. The deep architecture docs ([MODEL_SETUP.md](MODEL_SETUP.md), [NO_PII_NO_DATA.md](NO_PII_NO_DATA.md), [pseudonymisation.py](ailawfirm_usa/pseudonymisation.py) source) were already honest about this; the headline-level wording has now been brought into line with them.

### Why this matters
A US solo attorney relying on the prior *"Your data stays on your machine"* line who configured a cloud-LLM provider for HIPAA-PHI work would have been misled about the federal-grade obligation surface. Gateway sanitisation reduces PHI exposure structurally but cloud-mode users handling Covered Entity matters retain the BAA obligation under 45 CFR §164.504(e) — the prior wording did not surface this. The refinement is honest disclosure; the Gateway as a privacy primitive is materially stronger than what most cloud-AI legal tools offer; the wedge for choosing this tool over commodity cloud AI is preserved.

### Unchanged
- All agents, drafting templates (89 federal-first + 23 Tier-1 statute digests), tests, getting-started guides, and the Pseudonymisation Gateway itself are unchanged. This is a documentation + privacy-disclosure-honesty refinement, not a behavioural change.

### Verification
- `grep -inE "Your data stays on your machine\\.|runs locally, and is honest"  README.md` — should return zero hits for the unqualified forms after this commit (qualified forms with "by default · cloud-optional · Gateway" framing are the replacement)
