# DISCLAIMER — AI Brain · USA · Solo Edition

**Read this before installation or use.**

## What this tool is

AI Brain — USA · Solo is **open-source developer software** (MIT-licensed) published by wolfgang_rush. It is a **productivity aid for qualified legal professionals**. It is not a legal service. It does not perform autonomous legal reasoning. Every output it produces must be reviewed by an attorney admitted to practice in the relevant US jurisdiction before any client-facing use.

## Who may use this tool

AI Brain — USA is intended exclusively for:

- **Attorneys** admitted to practice in any US state or the District of Columbia
- **Attorneys** admitted to practice in any US federal court (district courts · circuit courts · Supreme Court · specialized courts · USPTO · BIA · etc.)
- **In-house counsel** employed by US entities and working on US-law matters
- **Paralegals** working under the direct supervision of an admitted attorney
- **Foreign Legal Consultants** registered with the appropriate state's foreign-legal-consultant rules (e.g. NY 22 NYCRR §521; CA Rule 9.44)

**If you are not a qualified legal professional, do not use this tool to produce client-facing legal work.**

The Unauthorized Practice of Law (UPL) is regulated by each US state. Strictest UPL enforcement jurisdictions include California, Texas, Florida, New York, Illinois, and the District of Columbia. Use of this tool by non-attorneys to perform legal work in those jurisdictions may constitute UPL.

## What this tool is NOT

This tool does NOT:

- Provide legal advice
- Provide legal opinions
- Represent any party in any matter
- Constitute the practice of law under any state UPL statute
- Replace the role of an admitted attorney
- Generate court-grade or production-ready legal documents without attorney review
- Operate as a service from any server controlled by the publisher

## Publisher's jurisdiction

The publisher (wolfgang_rush — Rushikesh R. Mahajan) is an Indian advocate admitted to practice at the High Courts of India, under the Advocates Act 1961. The publisher is NOT admitted to practice in any US jurisdiction. The publisher does NOT offer legal services in the United States. The publisher offers this tool as **open-source software**, published from India under the MIT license, for use by US-admitted attorneys in their own practice.

## ABA Model Rules of Professional Conduct (your obligations)

If you are admitted in a state that has adopted the ABA Model Rules (most states have, with variations), your use of this tool must comply with the applicable rules, in particular:

- **Rule 1.1** Competence — including technological competence (Comment 8)
- **Rule 1.6** Confidentiality of Information — especially Rule 1.6(c) requiring reasonable efforts to prevent unauthorized disclosure
- **Rule 5.3** Responsibilities Regarding Nonlawyer Assistance (including AI tools per recent state-bar opinions)
- **Rule 5.5** Unauthorized Practice of Law (re: multi-state practice)
- **Rule 7.1-7.3** Communications about services (re: marketing)

The tool's local-only default mode is designed to support Rule 1.6(c) confidentiality compliance. Cloud-mode use must consider Rule 1.6 implications carefully — many state bars have issued advisory opinions on AI tool use; consult your jurisdiction's current guidance.

## CCPA · CPRA · state privacy laws

California's CCPA (as amended by CPRA) imposes obligations on businesses that collect or process personal information of California residents. Other states (Virginia VCDPA · Colorado CPA · Connecticut CTDPA · Utah UCPA · Texas TDPSA · Oregon OCPA · Montana MCDPA · others) have similar laws.

The publisher is **not a business or service provider** under any of these laws — the publisher operates no server processing user input. See [NO_PII_NO_DATA.md](NO_PII_NO_DATA.md) for the complete zero-collection architecture.

If you use the tool to process personal information of clients, **you** are the business/controller for that processing. Your CCPA/state-privacy obligations apply (consumer rights · DSARs · sale/share opt-out · sensitive personal information handling · DPIAs · etc.). The tool does not transmit such data anywhere unless you have explicitly enabled cloud mode and used a cloud feature.

For client-confidential work, use the **local-only mode** (Ollama + Qwen3 or equivalent). See [MODEL_SETUP.md](MODEL_SETUP.md).

## HIPAA / sectoral law (if applicable to your practice)

If you handle Protected Health Information (PHI) as part of your practice, your HIPAA obligations apply. The publisher is not a Business Associate (operates no server processing PHI). If you opt into cloud mode and the cloud vendor does not have a HIPAA-compliant BAA with you, do NOT route PHI through cloud mode.

Similar sectoral analysis applies to GLBA (financial data), FERPA (education data), and COPPA (children's data) where relevant to your matters.

## FTC Act §5 / consumer protection

The publisher makes no claim that the tool guarantees legal outcomes, replaces human attorneys, or constitutes attorney services. All marketing language is honest about limitations.

## Output liability

The tool is provided AS-IS under the MIT license, without warranty of any kind, express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, and non-infringement. The publisher is not liable for tool output. **You** are the responsible operator. Every output must be reviewed by you before use. The publisher accepts no responsibility for outputs you choose to act upon without review.

## Statutory currency

US federal and state law evolves continuously. The tool's encoded knowledge has an AS-OF date documented in [KNOWLEDGE_PROVENANCE.md](KNOWLEDGE_PROVENANCE.md). The publisher makes reasonable efforts to keep the tool current but does NOT guarantee currency. Always verify any statutory provision, regulation, or case law against the official source (PACER · Westlaw · Lexis · official agency websites · government code repositories) before relying on it for client work.

Particularly volatile areas as of 2026:
- State AI regulation: Utah AI Policy Act (effective May 1, 2024) · Colorado AI Act SB24-205 (delayed to June 30, 2026 · federal litigation pending · replacement SB 189 in play) · Texas TRAIGA HB 149 (signed June 22, 2025 · effective Jan 1, 2026) · CA AB 2013 (signed 2024, AI transparency). **Note:** CA SB-1047 (AI safety bill) was VETOED by Governor Newsom on Sept 29, 2024 and is NOT law.
- State privacy laws (new states adopting frameworks regularly — VA · CO · CT · UT · TX · OR · MT · TN and counting)
- Federal AI executive orders and FTC enforcement
- DOJ enforcement priorities (antitrust · FCPA · digital assets)
- Federal Rules of Civil Procedure / Evidence amendments

## Cross-border practice

The publisher does not offer cross-border legal services. The act of publishing software from India for use in the US does NOT constitute the practice of law in any US jurisdiction by the publisher.

## Foreign judgment / enforcement

The publisher operates entirely from Indian soil with no assets in the United States. Any claim against the publisher must comply with Indian law on enforcement of foreign judgments (Section 13, Code of Civil Procedure 1908). US judgments are NOT directly enforceable in India under §13(b) (foreign court without competent jurisdiction over the publisher) and §13(f) (judgment may breach Indian public policy).

## DMCA + GitHub safe harbor

This repository is hosted on GitHub (a US-based service). Any copyright claim against repository content runs through GitHub's DMCA safe-harbor process (17 USC §512). The publisher reserves the right to file counter-notices under §512(g).

## Contact

For questions about this disclaimer or tool usage: GitHub Issues at the repo URL. The publisher does NOT accept legal-services engagement through this tool or its repository.

---

*This disclaimer references LEGAL_EXPOSURE_PLAYBOOK §3.V3 (UPL — US state-by-state), §3.V4 (Data Protection — CCPA + state laws), §3.V6 (Advertising — FTC), §3.V8 (Cross-border), §5 (Jurisdictional Positioning USA), §8 (Personal-Jurisdiction Shield). Playbook version: v0.1.*
