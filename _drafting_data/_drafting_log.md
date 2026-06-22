# USA Drafting Corpus — Build Log

## v0.2 Knowledge Layer — Drafting Corpus Phase 2

**Shipped:** 2026-05-29.
**Files added:** 89 templates + INDEX + SUMMARY + this log = 92 files.
**Build discipline:** Direct-author per locked wolfgang_rush AI Brain v0.2 overseer-workflow override (gemini/cmd delegation set aside; Claude direct-author proven on EU + SG + UK + AU + DIFC).

## Coverage scope

All 13 canonical litigation categories + commercial backbone + corporate backbone, federal-first per v0.1 SCOPE.md. State procedural rules deferred to v0.3+; Delaware General Corporation Law included as corporate practice anchor given Delaware's outsize role in U.S. corporate law.

## Numbering pattern

Inherited from EU / SG / UK / AU / DIFC. Federal-procedure orientation given the U.S. federal-first scope.

## Authority anchoring

Every template cites federal primary sources (USC / FRCP / FRE / FRCrP / FRAP / SCOTUS Rules / CFR) plus doctrinal currents through Supreme Court decisions (2024-2026 emphasized). Where Delaware law is anchor (corporate templates), DGCL and Court of Chancery doctrine cited.

## Verified primary-source URLs

Embedded in each template. All URLs to:
- uscode.house.gov (USC)
- law.cornell.edu (cross-reference)
- uscourts.gov (Federal Rules)
- supremecourt.gov (SCOTUS Rules)
- ecfr.gov (CFR)
- delcode.delaware.gov (Delaware Code)
- sec.gov (SEC rules and forms)
- ftc.gov (FTC rules and merger guidelines)
- eeoc.gov (EEOC)
- dol.gov (DOL FLSA + ERISA)
- justice.gov (DOJ FCPA + Antitrust)
- hhs.gov (HHS HIPAA)

## Build sequencing

1. Phase 1 — `_statute_corpus/` 23 digests + INDEX + SUMMARY (shipped 2026-05-29 commit `96a1e9f`).
2. Phase 2 — `_drafting_data/` 89 templates + INDEX + SUMMARY + LOG (this batch, 2026-05-29).
3. Phase 3 — README update + Family Status flip across all 6 firm READMEs + leak grep + push.

## Quality controls

- Leak check (canonical grep) before commit: zero leaks confirmed.
- No autonomous scope-shrink: all 13 litigation categories + commercial + corporate covered.
- No fabrication: all citations to verifiable federal statutes / rules / SCOTUS decisions current as of 2026.
- No hallucination of doctrine: where currency is uncertain (e.g., post-*Loper Bright* circuit-court applications, pending Eighth Circuit cert decisions), templates flag the uncertainty in Currency Warning section.
