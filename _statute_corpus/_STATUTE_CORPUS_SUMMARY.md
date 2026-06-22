# USA Statute Corpus — Summary

## What this corpus is

A federal-first authoritative-source compendium of 23 Tier-1 statute digests covering the procedural, constitutional, commercial, corporate, employment, and ethics backbones of U.S. legal practice. Each digest follows a uniform shape:

1. **Citation Block** — Bluebook citation form, official URL, and the public-law-citation form.
2. **Authority Tier** — uniformly Tier 1 in this corpus.
3. **Currency Block** — original enactment, major amendments, latest amendments / doctrinal currents.
4. **Scope of Digest** — sections covered and sections deferred (with reasons).
5. **Section-by-Section Digest** — for each anchor section: plain-English summary, verbatim statutory text, Bluebook citation format, practical-use note (anchored in named Supreme Court / circuit decisions where on point), STATUS verification flag.
6. **Drafting Hooks** — how the section threads into pleadings, motions, memos, agreements.
7. **Cross-references** — other federal statutes, rules, and ALI restatements that interact.
8. **Authority Sources** — official URLs for currency verification.

## Why these 23 (and not 50+)

The corpus is sized to cover the federal **backbone** that recurs across all 13 canonical litigation categories plus commercial and corporate backbone — without descending into specialised statutory regimes that belong to v0.3+ specialist annexes (tax code procedural detail · environmental NEPA/CERCLA · immigration INA · sectoral healthcare HIPAA covered-entity rules · sectoral financial GLBA / BSA / OFAC sanctions · trade Title 19 customs · ITC § 337). Those will be added as `_specialist_*` annexes when client demand or v0.3 scope authorises.

## What this corpus is NOT

- Not state-by-state procedural coverage. California CRC, New York CPLR, Texas TRCP — deferred to v0.3+.
- Not local-rules coverage for each U.S. District Court. Always consult a court's Local Rules.
- Not a citator — does not list every Supreme Court decision interpreting each section. Decisions are referenced only where they govern current doctrine.
- Not a substitute for primary-source verification. Every drafter using this corpus MUST verify current text at uscode.house.gov (federal statutes) / uscourts.gov (federal rules) / supremecourt.gov (SCOTUS Rules) / the enacting State's official code site (state statutes adopted in this corpus, viz., DGCL).
- Not legal advice. The corpus is a research and drafting aid for a qualified U.S.-licensed lawyer. Use under ABA Model Rule 1.1 (competence) and Rule 5.5 (jurisdictional licensure).

## Coverage of the 13 canonical litigation categories

| Category | Anchoring digest(s) |
|---|---|
| Appeals | s04 FRAP · s06 SCOTUS Rules |
| Injunctions / interim relief | s01 FRCP Rule 65 · s06 SCOTUS Rule 22 (stays) |
| Disclosure | s01 FRCP Rule 26 |
| Expert evidence | s02 FRE Rule 702 (Daubert) |
| Default judgment | s01 FRCP Rule 55 |
| Enforcement | s05 28 U.S.C. · s01 FRCP Rules 64-71 |
| Skeleton arguments / motion practice | s01 FRCP · s02 FRE · s04 FRAP |
| Counsel briefing | s23 ABA Model Rules 1.1, 1.3, 1.4 |
| Administrative review | s08 APA |
| Trial documentation | s01 FRCP · s02 FRE · s03 FRCrP |
| ADR | s12 FAA |
| Insolvency | s09 Title 11 |
| Tribunals beyond core civil | s08 APA · sectoral statutes (v0.3+) |

## Commercial backbone coverage

UCC (sales · secured transactions) · Antitrust (Sherman / Clayton / FTC / HSR) · FAA (domestic and New York Convention international) · CFAA (cyber / trade-secret-adjacent) · IP (Lanham / Copyright / Patent) · CISG (international sales).

## Corporate backbone coverage

DGCL (state-of-incorporation backbone for most U.S. public companies) · Securities Act 1933 + Exchange Act 1934 (federal disclosure and anti-fraud regime) · SOX (officer certifications · clawback · whistleblower) · Dodd-Frank (FSOC · Volcker · § 922 whistleblower bounty · § 954 expanded clawback · CFPB) · FCPA (anti-bribery + accounting provisions).

## Use with the firm's drafting agent

Each digest is loaded into the firm's drafting context window when the matter taxonomy maps to that statutory anchor. Citation format and verbatim statutory text are provided so the drafting agent can reproduce them in pleadings, motions, and memoranda without re-extraction errors. The STATUS: VERIFIED flag on each section indicates the editor verified the text against the official source at corpus compilation; downstream users must re-verify at the time of any filing.

## Update cadence

- **Annual sweep** — December 1 (federal rules amendment cycle) and during October Term updates.
- **Doctrinal recalibration** — within 30 days of any Supreme Court decision listed as a doctrinal current.
- **HSR / minimum-wage / FLSA threshold revisions** — within 7 days of FTC / DOL final publication.
- **CBDT-equivalent / SEC final-rule publications** — within 30 days for material provisions.

## Source canon

All digests cite primary sources at the United States Government Publishing Office, the Office of Law Revision Counsel, the Supreme Court of the United States, agency rulemaking dockets, and the relevant State's official code site (for DGCL). Persuasive secondary authority (CISG Advisory Council Opinions, ABA Formal Opinions) is identified as persuasive, not binding.

## File count

23 digests + this Summary + the Index = 25 files in `_statute_corpus/`.
