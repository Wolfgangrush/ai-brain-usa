# Data Breach Notification — Multi-State

## Source URLs
- [NCSL — State Security Breach Notification Laws](https://www.ncsl.org/technology-and-communication/security-breach-notification-laws)
- [California Civil Code § 1798.82](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=1798.82&lawCode=CIV)
- [New York SHIELD Act — Gen. Bus. Law § 899-bb](https://www.dfs.ny.gov/industry_guidance/cybersecurity)
- [HHS HIPAA Breach Notification Rule — 45 C.F.R. §§ 164.400-414](https://www.hhs.gov/hipaa/for-professionals/breach-notification/index.html)

## Last Verified
2026-05-29

## Authority Tier
Primary — state breach-notification statutes (all 50 states + DC + PR + USVI) + sectoral federal overlays (HIPAA, GLBA, SEC Item 1.05).

## Currency Warning
No federal omnibus breach law; state statutes vary materially on (a) definition of personal information (some include biometric / health insurance / passport / DNA), (b) notification timing (30/45/60 days from discovery, or "without unreasonable delay"), (c) AG/regulator notification thresholds (often 500+ residents), (d) credit monitoring offer (mandatory in some states), (e) substitute notice criteria.

## Template Type
Statutory Notice + Investigation Memo + AG Notification + Notifying-Letter Skeleton.

## Structural Skeleton
1. **Incident Response Memo** (internal) — timeline · scope · forensic findings · categories of PI affected · residents-by-state count.
2. **State-by-State Notification Matrix** — for each affected resident's state: trigger threshold met? timing rule? notice contents? AG notification? credit-monitoring obligation?
3. **Individual Notification Letter** — clear plain-language description of incident, types of info, what the entity is doing, what individuals can do, contact information, credit-monitoring offer where required.
4. **Attorney General Notification** — submission to applicable state AG offices (CA, NY, TX, FL, IL, MA, others) when threshold (typically 500+ residents) crossed; web-portals or email per state.
5. **Consumer Reporting Agency Notification** — if 1,000+ residents under most state laws (Equifax, Experian, TransUnion).
6. **Sectoral Notifications** — HHS Office for Civil Rights (HIPAA — 60 days, plus media if 500+ in a state); FTC Health Breach Notification Rule for non-HIPAA health apps; SEC Form 8-K Item 1.05 (4 business days from materiality determination); state insurance regulators (NY DFS Part 500 — 72 hours).
7. **Substitute Notice** elements where direct notice impossible: website posting + statewide media + email (where appropriate).
8. **Document Preservation Memo** — litigation hold tied to the incident.

## Drafting Conventions
- The earliest applicable state-law clock controls the schedule for that state's residents.
- Massachusetts requires affected resident's free credit monitoring (Mass. Gen. Laws ch. 93H § 3A) for breach of SSN.
- California requires submission of a sample notice to AG when notifying 500+ residents.
- HIPAA "low probability of compromise" risk assessment (45 C.F.R. § 164.402) is documented as the gating analysis if invoking that exception.
- SEC Item 1.05 4-business-day clock starts from "materiality" determination, not incident discovery.

## Fair-Use Excerpt
> "Any person or business that conducts business in California, and that owns or licenses computerized data that includes personal information, shall disclose any breach of the security of the system following discovery or notification of the breach in the security of the data to a resident of California… in the most expedient time possible and without unreasonable delay…" — Cal. Civ. Code § 1798.82(a).

## Practical Use for Solo Advocate / Small Firm
The single most-likely incident-response engagement for a privacy practice. Run intake within 24 hours of breach call; lock the state-by-state matrix on Day 2; first wave of notifications by Day 14 under tight-clock states; AG portals by Day 30.
