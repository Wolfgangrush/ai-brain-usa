# SCOPE.md — AI Brain USA v0.1

## In Scope (v0.1)

- Federal court hierarchy (SCOTUS, 13 circuits, 94 districts, bankruptcy, tax, federal claims)
- Bluebook 21st ed citation validation (SCOTUS, F.3d, F.Supp.3d, U.S.C., C.F.R.)
- ICS calendar sync with per-state timezone + DST (America/New_York default)
- ABA Model Rules compliance firewall (MR 7, 5.5, 1.6, Formal Opinion 512)
- CCPA/CPRA, NY SHIELD, FinCEN CTA regulatory flags
- 50-state enum + DC + territories
- 6 empty state placeholder subdirs (CA · TX · NY · FL · IL · DE)
- 7-language onboarding (EN · ES · ZH · TL · VI · AR · FR)
- Brain classifier with 10 intent classes
- 7 specialist agents (matter, citation, court, drafting, deadline, compliance, calendar)
- 3 MCP tools (court lookup, citation validator, calendar sync)

## Out of Scope (v0.1)

- Per-state procedural rules (CA CRC, NY CPLR, etc.) → v0.2+
- State-specific court hierarchies → v0.2+
- State bar rule variations (beyond ABA Model Rules) → v0.2+
- Local Rules (LR) for individual US District Courts → v0.3+
- Multi-user firm mode (auth, roles, billing, conflict-check) → v0.2+
- Full text of statutes (enums + stubs only in v0.1) → v0.2+
- Case law database / citator → v0.3+
- E-filing integration (CM/ECF, PACER) → v0.3+
- LLM-based intent classification (keyword-only in v0.1) → v0.2+
- Tribunal-specific detail (NTSB, FCC, FTC) → deferred
- Louisiana civil law specifics → v0.2+

## Architecture Decisions

Per ADR-001 (D1-D3), ADR-002 (D4-D7), and ADR-006 (Federal-first scope):
- One codebase per country, solo + firm combined
- Country = subfolder of parent workspace
- Federal scope only in v0.1; state encoding is v0.2+ work

## Known Gaps

- 50-state procedural variation requires ~50 additional research files
- Local Rules (LR) for each US District Court are not covered
- California Style Manual and NY Law Reports Style Guide (non-Bluebook citation variants) not supported
- No PACER/CM-ECF integration
- No Westlaw/LexisNexis citator
