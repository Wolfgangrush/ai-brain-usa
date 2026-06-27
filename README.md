<div align="center">

<img src="docs/banner.png" width="820"/>

**A federal-focused, local-first practice brain for US attorneys.**

Visit the live site: [wolfgangrush.github.io](https://wolfgangrush.github.io)

</div>

<div align="center">

[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
![Local-first](https://img.shields.io/badge/Local--first-yes-blue.svg)
![Focus: US Federal Law](https://img.shields.io/badge/Focus-US%20Federal%20Law-1f6feb.svg)

</div>


# 🇺🇸 AI Brain for USA Lawyers

> **Free practice OS for every US solo attorney, in-house counsel, and supervised paralegal. Federal-focused with state scaffolding. Terminal-native. Local-first by default (Ollama + Qwen3 — nothing leaves your laptop). Cloud-LLM optional with the [Pseudonymisation Gateway](https://github.com/Wolfgangrush/pseudonymisation-gateway) sanitising PII before any prompt leaves the machine.**

**For licensed attorneys only.** Intended for attorneys admitted in any US state, the District of Columbia, any US federal court, in-house counsel of US entities, registered Foreign Legal Consultants, and paralegals working under direct attorney supervision. **If you are not a licensed attorney, do not use this tool to produce client-facing legal work.** State UPL rules apply — strictest enforcement in CA · TX · FL · NY · IL · DC. Read [DISCLAIMER.md](DISCLAIMER.md) before installation.

**Version:** 0.1.1 · **License:** MIT · **Publisher:** [wolfgang_rush](https://github.com/Wolfgangrush) — an Indian advocate (High Courts of India, India). NOT admitted in any US jurisdiction. This is a software publication for US-admitted attorneys. · **Engine:** Built on a local memory architecture

> 📌 **v0.1 scope: FEDERAL.** State-specific procedural modules ship in v0.2+. State enums scaffolding (50 states + DC + territories) is present in v0.1 as placeholders. See [SCOPE.md](SCOPE.md).

> ⚠️ **AI can make mistakes. Always verify the output.**
>
> This software generates assistive drafts and suggestions only. Every legal claim, citation, statute reference, procedural step, deadline calculation, and ground of relief must be independently verified by a qualified human practitioner before filing, advising a client, or relying on the output. The publisher accepts no liability for outputs used without verification.

> 🛡️ **Privacy primitive: PII pseudonymisation** via [pseudonymisation-gateway](https://github.com/Wolfgangrush/pseudonymisation-gateway) (wolfgang_rush · MIT). This firm uses the `usa` jurisdiction module + Indian-diaspora overlay for cross-jurisdiction PII coverage. Open-source · zero runtime deps · session-scoped · in-memory only · never writes PII to disk.


> 🛡️ **Pseudonymisation coverage (v0.1.1):** The privacy gateway pseudonymises PII before any cloud-API call; any residue the scanner can't fully resolve is surfaced to you and audit-logged — you retain the final call (v0.3 honest-disclosure). Covers USA-native identifiers (SSN · ITIN · EIN · US phone · USD amounts · driver-license placeholders · federal court docket numbers) and Indian-diaspora identifiers (Aadhaar · PAN · GSTIN · IFSC · Indian phone — USA has substantial South Asian diaspora). Generic patterns (email · names with honorifics · dates · ZIP codes) work cross-jurisdiction. State-specific identifier formats (varies wildly per state) are scoped for v0.2.

> **🧠 AI Brain that LEARNS.** Every session makes the next one smarter. Two built-in Claude Code skills power this: `/retrospective` saves what the firm learned at session end — every jurisdiction, statute, argument pattern, and procedural rule you touched is logged so the firm's knowledge compounds. `/wake` loads that accumulated context the next time you start, so you never begin from zero. The firm is your second brain, and it gets sharper with every case.

---

## 🌐 Choose your language

| Script | Language | Audience | Guide |
|---|---|---|---|
| 🇺🇸 | **English** | All US jurisdictions · authoritative | [GETTING_STARTED.md](GETTING_STARTED.md) |
| 🇪🇸 | **Español (Spanish)** | Hispanic / Latino bar (largest minority in US legal services) | [GETTING_STARTED_SPANISH.md](GETTING_STARTED_SPANISH.md) |
| 🇨🇳 | **中文 简体 (Simplified Chinese)** | Chinese-American legal community | [GETTING_STARTED_CHINESE.md](GETTING_STARTED_CHINESE.md) |
| 🇵🇭 | **Tagalog** | Filipino-American legal community | [GETTING_STARTED_TAGALOG.md](GETTING_STARTED_TAGALOG.md) |
| 🇻🇳 | **Tiếng Việt (Vietnamese)** | Vietnamese-American legal community | [GETTING_STARTED_VIETNAMESE.md](GETTING_STARTED_VIETNAMESE.md) |
| 🌍 | **العربية (Arabic)** | Arabic-speaking bar (Lebanese-American, Syrian-American, others) | [GETTING_STARTED_ARABIC.md](GETTING_STARTED_ARABIC.md) — RTL |
| 🇫🇷 | **Français (French)** | Francophone bar (Louisiana civil-law tradition · Haitian-American) | [GETTING_STARTED_FRENCH.md](GETTING_STARTED_FRENCH.md) |

> 🙏 **Honest note:** Six of these guides were AI-assisted. **Native-speaker PRs warmly welcome** via [TRANSLATION_HELP_WANTED.md](TRANSLATION_HELP_WANTED.md).

---

## 💛 Why this exists

> The US solo attorney market faces specific pressures the BigLaw model doesn't see:
> - **Solo practice dominates US private practice** — ~49% of US lawyers in private practice are solo practitioners (ABA Profile of the Legal Profession 2023)
> - **State UPL enforcement is active** and varies wildly across jurisdictions — strictest enforcement profiles in CA · TX · FL · NY · IL · DC
> - **Multi-state practice complexity** — single matters span state + federal + tribal jurisdictions
> - **ABA Formal Opinion 512 (July 29, 2024)** on generative AI tools imposes Rule 1.1 technological-competence + Rule 1.6 confidentiality + Rule 5.3 supervision obligations
> - **State AI regulation cascade** — Utah AI Policy Act (effective May 1, 2024) · Colorado AI Act SB24-205 (delayed to June 30, 2026 · subject to federal litigation · replacement SB 189 in play) · Texas TRAIGA HB 149 (signed June 22, 2025 · effective Jan 1, 2026) · CA AB 2013 (generative AI transparency · signed 2024) — creating compliance complexity for solo practice (note: CA SB-1047 was VETOED by Governor Newsom on Sept 29, 2024)

BigLaw firms have legal-operations teams of 50+. Solo attorneys don't. We built this so a US solo practitioner — whether civil-rights litigator in Mississippi or M&A solo in Manhattan — can have a second brain that costs **$0 forever**, runs locally by default (Ollama + Qwen3), and supports ABA Model Rule 1.6 confidentiality at the architecture layer — either by absence of transmission (local mode) or by Pseudonymisation Gateway sanitisation (cloud mode). Honest about its limitations throughout.

---

## 🧠 What's inside — specialists who live in your terminal

| # | Specialist | What they do for you |
|---|---|---|
| 🧠 | **The Receptionist (brain)** | Listens to what you say. Figures out who you need. Calls the right specialist. You never memorize commands. |
| 📂 | **The Matter Manager** | Holds every active matter — parties, prayers, hearings, orders, draft state. Walk into court · context comes back instantly. |
| 📜 | **The Citation Clerk** | Parses Bluebook citations — Supreme Court (`410 U.S. 113`) · Circuit (`543 F.3d 100 (9th Cir. 2008)`) · District (`123 F.Supp.3d 456 (S.D.N.Y. 2020)`) · USC (`42 U.S.C. § 1983`) · CFR (`29 C.F.R. § 825.100`). |
| 🏛️ | **The Court Registrar** | Knows the federal court hierarchy: SCOTUS · 13 Circuit Courts · 94 District Courts · Bankruptcy Courts · Tax Court · Court of Federal Claims · plus 50-state enum scaffolding (v0.2+ adds per-state depth). |
| ✍️ | **The Drafting Assistant** | **89 federal-first drafting templates** across all 13 canonical litigation categories + commercial backbone + corporate backbone — pleadings (complaint · answer · counterclaim · third-party · amended · derivative · class · removal), motions (12(b)(6) · Rule 56 · Rule 65 TRO/PI · 12(b)(3)(C) · Rule 29 · 1447 · FAA), discovery (Rule 26 · 33 · 34 · 36 · 30 · privilege log · ESI protocol), appeals + enforcement (FRAP 3 · 28 · 35 · SCOTUS Rule 14 cert · writ · garnishment · charging order), insolvency (Title 11 Ch 7 / 11 / 13 + proof of claim + relief from stay), tribunals (Tax Court · BIA · ALJ · SSA · APA judicial review), commercial (MSA · SaaS · supply · distribution · franchise · loan · UCC-9 security · CISG), corporate (DE certificate + bylaws · merger · Series Seed · Form D · § 220 demand), regulatory (CCPA/CPRA · multi-state breach · 8-K Item 1.05 cyber · HIPAA BAA · NIST AI RMF · state AI acts · FCPA). Plus **23 Tier-1 statute digests** (FRCP · FRE · FRCrP · FRAP · 28 USC · SCOTUS Rules · Constitution · APA post-*Loper Bright* · Title 11 · UCC · antitrust · FAA · CFAA · IP · Securities Acts · SOX · Dodd-Frank · DGCL · FCPA · Title VII et al. · ERISA/FLSA · CISG · ABA Model Rules). Each template carries Source URLs · Last Verified · Currency Warning · Structural Skeleton · Drafting Conventions · Fair-Use Excerpt · Practical-Use note. Doctrinal currency anchored through 2024-2026 SCOTUS (*Loper Bright* · *Corner Post* · *Bostock/Muldrow* · *Helix v. Hewitt* · *Spizzirri* · *Harrington v. Purdue Pharma* · *Tornetta v. Musk* · *CFPB v. CFSA*). |
| 🛡️ | **The Compliance Officer** | Watches your firm website, LinkedIn, marketing for **ABA Model Rule 7 (advertising)** + **Rule 5.5 (UPL)** + **Rule 1.6 (confidentiality)** + **ABA Formal Opinion 512 (AI use)** firewall risks BEFORE you publish. Also flags CCPA / state-privacy gaps. |
| 📅 | **The Calendar Sync** | ICS feed sync to iPhone Calendar / Google Calendar / Outlook — no third-party API, no data processor. code-aliased summary line (lock-screen safe) · full matter detail in event body. Timezone America/New_York default (configurable per state). |

---

## 🚀 Install in 30 minutes

### Step 1 — Pick your operating system

| OS | Guide |
|---|---|
| 🍎 **Mac** | [MAC_INSTALL.md](MAC_INSTALL.md) — Terminal, common gotchas |
| 🪟 **Windows** | PowerShell · standard pip install |
| 🐧 **Linux** | Same commands as Mac |

### Step 2 — Install Python (one-time) + the tool

```bash
pip install git+https://github.com/Wolfgangrush/ai-law-firm-usa.git
```

### Step 3 — Connect an AI brain (ONE COMMAND)

```bash
ailawfirm-usa connect-local
```

This single command:
1. Detects if Ollama is installed; if not, prints platform-specific install instructions
2. Detects your laptop's RAM
3. Recommends and downloads the right Qwen3 model (14b for 16GB+ · 7b for 8GB · 1.7b for older laptops)
4. Writes config so all subsequent calls route to local Ollama
5. Runs a smoke test to confirm local connectivity

After this, **no queries leave your laptop**.

Three honest model options — see [MODEL_SETUP.md](MODEL_SETUP.md):

| Choice | Cost | Privacy | Best for |
|---|---|---|---|
| 🥇 **Local Ollama + Qwen3** | $0 forever | 🟢 Perfect — nothing leaves your laptop | **Client matters · ABA Rule 1.6 confidentiality · HIPAA-PHI · privileged communications · use this tier when zero cross-border data flow is required** |
| 🥈 **DeepSeek API** | ~$2-5/mo | ⚠️ Pseudonymisation Gateway sanitises party names + SSN/ITIN/EIN before transmission, BUT China-routed transmission of even pseudonymised data for US client matter raises ABA Rule 1.6 + state-AG questions | Non-client work · public-law research · templates |
| 🥉 **Claude / Gemini API** | ~$25-80/mo | 🟢 Strong (enterprise privacy default-ON) — Gateway sanitises before transmission; vendor BAA available | Heavy daily users with executed BAA + state-privacy DPA + clear state-bar opinion on cloud AI use. **⚠️ HIPAA PHI in cloud mode** requires (a) Gateway coverage of the specific PHI identifiers in your matter AND (b) executed Business Associate Agreement with the vendor per 45 CFR §164.504(e) — Gateway sanitisation alone does not discharge the BAA obligation |

### Step 4 — Run

```bash
ailawfirm-usa
```

Sample commands:

```
> tell me about the Ninth Circuit's en banc procedure
> validate 410 U.S. 113 (1973)
> check this firm slogan: "Aggressive injury lawyer · best in California"
> what's the statute of limitations for a Section 1983 claim in NY?
> add motion-hearing MAT-2026-014 SDNY Courtroom 14C 2026-06-09 10:00 ET
> sync calendar
```

---

## 🔒 Privacy & Data Handling — what stays where

**Architecture — three pieces decide your privacy posture:**

**(1) Local-only state.** Your matters, drafts, audit logs, calendar entries, and configuration live in `~/.ailawfirm_usa/`. Never uploaded by the tool. Never synced to a third-party cloud by the tool. No telemetry. No "anonymous usage statistics." The publisher operates zero infrastructure and cannot access this folder. Verifiable via `grep -ri "telemetry\|analytics\|requests.post\|urlopen" ailawfirm_usa/` — should return only user-initiated cloud-LLM calls.

**(2) LLM backend — you choose.** The default `connect-local` command configures Ollama + Qwen3 to run the language model on your laptop (truly nothing leaves). If you opt into a cloud-LLM tier (DeepSeek / Claude / Gemini) for quality reasons, see the tier table above for cost + privacy trade-offs.

**(3) Pseudonymisation Gateway — always-on for cloud mode.** When you configure a cloud-LLM provider in `~/.ailawfirm_usa/config.json`, the internalised `PseudonymisationGateway` (source: `ailawfirm_usa/pseudonymisation.py`) automatically substitutes real names, government IDs (SSN · ITIN · EIN · Aadhaar for Indian-diaspora matters), contact identifiers (phone · email), and case references (federal docket numbers) with deterministic placeholders BEFORE the prompt leaves your machine. The placeholder ↔ original map lives in memory only (never written to disk; destroyed when the gateway goes out of scope). Cloud vendors see only the abstract structure of the matter; the user sees real values restored in the response.

**HIPAA-PHI matters in cloud mode** additionally require an executed Business Associate Agreement with the vendor per 45 CFR §164.504(e). Gateway sanitisation reduces but does not eliminate Covered Entity obligations — verify the Gateway's coverage of the specific PHI identifiers in your matter AND have the BAA in place before invoking cloud mode for PHI work.

The wedge: every other cloud-AI legal tool sends raw client PII to the LLM by default. wolfgang_rush AI Brain — USA ships Ollama-first AND ships the Gateway as the privacy primitive that closes the gap when you choose cloud mode for quality reasons.

### What goes to the API provider during each query

Each time the firm reasons about a matter, the following are sent to your chosen API provider:
- Your prompt (the question or instruction)
- Relevant context the firm pulls from your local matter folder (current draft state, recent orders, citations being verified)

Your full matter history, audit logs, and unrelated cases are NOT sent. The firm sends the minimum context needed to answer the current question.

### What API providers contractually guarantee

| Provider | Trains on your data? | Retention | Source |
|---|---|---|---|
| **Claude API** (Anthropic) | ❌ No — Commercial Services data is not used for training | ~30 days for safety/abuse review (Zero Data Retention available on enterprise contract) | [Anthropic Privacy Policy](https://www.anthropic.com/legal/privacy) · [Commercial Terms](https://www.anthropic.com/legal/commercial-terms) |
| **OpenAI API** (GPT-4) | ❌ No — API data not used for training since March 2023 | ~30 days for abuse review (ZDR available) | [OpenAI API Data Usage Policies](https://openai.com/policies/api-data-usage-policies) |
| **Gemini API (paid via Vertex AI)** | ❌ No — paid-tier API data not used for training | Per Google Cloud contract | [Vertex AI data governance](https://cloud.google.com/vertex-ai/docs/general/data-governance) |
| **Gemini Free Tier** | ⚠️ **YES — Google AI uses free-tier prompts to improve products** | — | [Google AI Studio terms](https://ai.google.dev/gemini-api/terms) — **DO NOT use free-tier Gemini for confidential client matters.** |
| **DeepSeek V4 Pro API** | ❌ No — per DeepSeek API terms, inputs/outputs not used for model training | Retention policy less documented than OpenAI/Anthropic; verify for matter sensitivity | [DeepSeek API ToS](https://platform.deepseek.com/api-docs/legal) · **Note:** provider is China-based; consider jurisdictional data-residency requirements |

### What that does NOT mean — solicitor's residual risk

Even though API data is not used for training:

1. **Data IS in transit** during each query — it passes through the provider's infrastructure
2. **Brief logging retention** (typically 30 days) means the provider holds the data for that window
3. **Lawful access requests** — a subpoena, lawful intercept warrant, CCPA data-subject access request, or provider security incident could expose data during the retention window
4. **Provider-side breach risk** — however small, it exists

This is fundamentally different from local-LLM mode (where no data leaves your machine, ever, period). The `connect-local` command already configures Ollama + Qwen3 as the v0.1 default — attorneys handling confidential, privileged, or special-category data should stay in local-LLM mode for that work. The cloud-LLM tier exists for non-confidential research, public-law analysis, and template scaffolding where contractual no-training is a sufficient safeguard.

### Solicitor's decision

If your matter is:
- **General commercial / corporate / contract drafting** → Claude / OpenAI / paid Gemini API are appropriate. Contractual no-training protections are strong. Audit logs are local.
- **Legal-privileged client communication / privileged litigation strategy** → Evaluate against your jurisdiction's professional conduct rules. Most regulators permit reasoned use of cloud-AI with disclosure to the client. (See USA (state Bar associations) guidance.) Document the choice in your audit log.
- **HIPAA / GLBA / FERPA / state-privacy special-category data** → Stay in `connect-local` (Ollama + Qwen3) mode. Do not opt into any cloud-LLM tier for these matters; do not use free-tier Gemini.
- **State secrets / classified material / under-seal court orders** → Stay in `connect-local` (Ollama + Qwen3) mode. For physically air-gapped networks where the pip-install / model-download / auto-update paths are also prohibited, await the v0.3+ signed offline-install bundle below.

The firm's audit log captures every API call (timestamp, agent, prompt-summary, output-summary) at `~/.ailawfirm_usa/audit_logs/`. Logs never leave your machine. They are your professional-conduct compliance trail.

### v0.3+ roadmap

> What v0.1 already ships: (a) local-LLM default via `connect-local` (Ollama + Qwen3 — nothing leaves your laptop in local mode), (b) configurable cloud-LLM tier covering Claude / OpenAI / paid Gemini / DeepSeek, (c) Pseudonymisation Gateway sanitising PII before any cloud-LLM call, and (d) no first-party telemetry. The items below extend the floor — they are not a future replacement for what is already shipped.

- **Signed offline-install bundle** — the `pip install` path currently touches PyPI and the Ollama model registry; v0.3+ ships a signed offline-installable archive with the Qwen3 model pre-bundled, removing the last network-touch point even at install time. For attorneys on physically air-gapped networks (sealed-matter rooms, security-cleared environments).
- **In-firm LLM tenant adapter** — drop-in config for Azure OpenAI / private Vertex / on-prem vLLM endpoints. Distinct from the today-shipped public-API cloud-LLM tier; targets attorneys whose firm already provisions LLM infrastructure under its own BAA / DPA.
- **Expanded local-model surface** — Llama 3.3 70B / Qwen 2.5 72B / DeepSeek V4 Pro (open-weights via Ollama), for attorneys with larger laptops who want better-than-Qwen3-14b local reasoning.

Tracked at: [drafting-agents-core issues](https://github.com/Wolfgangrush/drafting-agents-core/issues).

---

**No agenda · no telemetry · no cloud-default · MIT licensed · $0 forever.**

**USA (state Bar associations) Rule compliance built into the tool's audit + transparency-gate architecture.** Attorney remains professionally responsible for every output. The firm is a force-multiplier, not a substitute for judgment.

---

## 📁 Where your data lives

```
~/.ailawfirm-usa/                    ← Mac/Linux
C:\Users\YourName\.ailawfirm-usa\    ← Windows
├── palace/                          ← all matter/client/citation memory (ChromaDB)
├── config.json                      ← your settings (AI provider · state · timezone · prefs)
├── calendars/                       ← generated .ics feeds for iPhone/Outlook subscribe
└── people_map.json                  ← optional client alias system (lock-screen safety)
```

Copy this folder to a USB drive · OneDrive · iCloud Drive · Dropbox = complete backup of your practice in 5 seconds.

---

## 🔄 How to update your firm

When a new version of AI Brain — USA is published, you pull it in with **one command**. Your matter data + your project-root `CLAUDE.md` are **never touched** — only the firm's installed code, skills, and prompts refresh.

### Path 1 — Plain terminal

```
ailawfirm-usa update
```

Under the hood this runs `pip install --upgrade git+https://github.com/Wolfgangrush/ai-law-firm-usa.git`. After it finishes, restart any open `ailawfirm-usa` session so the new skills + prompts load.

### Path 2 — Inside Claude Code

Type:

```
/update
```

Claude runs the same command for you and reports the result.

### Path 3 — Inside Gemini CLI

Type:

```
/update
```

Same outcome — Gemini calls `ailawfirm-usa update` for you.

### When to update

- **The publisher tells you** a new version is out → update.
- **Monthly hygiene** → update once a month so you stay current on skills + bug fixes.
- **After hitting a bug** → first thing to try is updating, in case it is already fixed upstream.

### What does NOT update (by design)

- Your matter folders (`~/Desktop/<your-firm>/<matter>/...`)
- Your project-root `CLAUDE.md` (your customisations always win)
- Your `~/.ailawfirm-usa/` config + palace data
- Your chosen AI model setup (Ollama · DeepSeek · Claude · Gemini)

Only the firm's installed Python code, skills, and template files refresh. Your practice is unaffected.

### One catch — existing users + new template rules

If a new version updates the template `CLAUDE.md` (the firm's standing rules), your project-root `CLAUDE.md` is preserved because your customisations always win. To see what changed in the template after an update:

```
diff CLAUDE.md "$(python3 -c 'import ailawfirm_usa, os; print(os.path.join(os.path.dirname(ailawfirm_usa.__file__), "templates/CLAUDE.md"))')"
```

Review the diff and merge what you want into your own `CLAUDE.md`.

---

## 🛤️ Roadmap (honest)

> 🙏 **Honest note on timelines:** Solo-author OSS · ships as time permits · v0.2 / v0.3 / v0.4+ targets are indicative, not committed dates. Open an issue if a specific feature on a specific timeline matters to your work.



- **v0.1.0** *(shipped)* — bootstrap: architecture, brain layer, 6 specialist agents (4 live · 2 stubs) — calendar functionality delivered via the calendar MCP tool rather than as a standalone agent — 3 working MCP tools (court · citation · calendar), 7-language onboarding, connect-local one-command CLI, state-enum scaffolding (50 states + DC + territories as placeholders), Federal-focused v0.1, LEGAL_EXPOSURE_PLAYBOOK v0.1 compliance
- **v0.2 — knowledge layer** *(shipped 2026-05-29)* — **23 Tier-1 federal-first statute digests** in `_statute_corpus/` (FRCP · FRE · FRCrP · FRAP · 28 USC · SCOTUS Rules · Constitution + Bill of Rights · APA post-*Loper Bright* · Title 11 Bankruptcy Code · UCC Arts 1/2/9 · Sherman+Clayton+FTC antitrust · FAA · CFAA · IP consolidated (Lanham/Copyright/Patent) · Securities Act 1933 + Exchange Act 1934 · SOX · Dodd-Frank · DGCL · FCPA · Title VII+ADA+ADEA+FMLA+PWFA · ERISA+FLSA · CISG · ABA Model Rules) plus **89 federal-first drafting templates** in `_drafting_data/` covering all 13 canonical litigation categories + commercial backbone + corporate backbone. Doctrinal currency anchored through 2024-2026 SCOTUS.
- **v0.1.1 — Pseudonymisation Gateway** *(shipped 2026-05-29)* — internalised at `ailawfirm_usa/pseudonymisation.py`; sanitises PII before any cloud-LLM call. Standalone source at [pseudonymisation-gateway](https://github.com/Wolfgangrush/pseudonymisation-gateway).
- **v0.2 — frontend / UX layer** *(in progress)* — matter dashboard · citation deep-parse · ABA Formal Opinion 512 compliance dashboard · state-procedural modules for CA · TX · NY · FL · IL · DE (6-state launch wave)
- **v0.3** *(following milestone)* — **firm mode** for multi-attorney practices · role/permission · matter assignment · conflict-check · trust-account compliance (state IOLTA rules) · ABA Model Rule 5.1 supervisory framework · per-state procedural depth wave 2 · sectoral specialist annexes (tax code procedural · environmental NEPA/CERCLA · immigration INA · HIPAA covered-entity rules · GLBA/BSA/OFAC sanctions · trade Title 19 · ITC § 337)
- **v0.4+** — CourtListener / Justia / PACER cross-reference · 50-state procedural depth wave 3 · Apple EventKit native · CalDAV bidirectional sync · multi-state matter handling (federal + state + tribal)

Six sister jurisdictions on the same architecture: 🇮🇳 India · 🇸🇬 Singapore · 🇬🇧 UK · 🇦🇺 Australia · 🇦🇪 Dubai-DIFC · 🇪🇺 EU — each as its own MIT-licensed repo.

---

## 🌐 Family Status (honest · cross-firm)

The wolfgang_rush AI Brain family ships across 7 jurisdictions. Honest status of the v0.2 legal-knowledge layer (statute corpus + drafting data) per firm:

| Firm | Statute corpus | Drafting corpus | Shared agents | GitHub |
|------|---|---|---|---|
| 🇮🇳 **India** | Native knowledge base · maintainer-curated | wolfgang_rush plugins (14 Indian-litigation plugins · separate stack) | Not applicable — Indian-specific | ✅ LIVE |
| 🇪🇺 **EU** | ✅ 11 statutes · 8/8 Tier-1 | ✅ **56 templates** · litigation + commercial complete (v0.2 closed 2026-05-28) | ✅ Migrated | ✅ LIVE |
| 🇦🇺 **Australia** | ✅ 13 Tier-1 statute digests + 39 research files | ✅ **79 templates** · litigation + commercial + tribunal complete (v0.2 closed 2026-05-28) | ✅ Migrated | ✅ LIVE |
| 🇦🇪 **Dubai-DIFC** | ✅ 24 statute digests · dual-track (15 DIFC + 9 Mainland UAE Federal) · v0.2 closed 2026-05-29 | ✅ **81 templates** · dual-track DIFC + Mainland · litigation + commercial + tribunal complete (v0.2 closed 2026-05-28) | ✅ Migrated | ✅ LIVE |
| 🇸🇬 **Singapore** | ✅ 17 statute digests Tier-1 | ✅ **55 templates + 6 scaffolds** · litigation + commercial + regulatory complete (v0.2 closed 2026-05-28) | ✅ Migrated | ✅ LIVE |
| 🇬🇧 **UK** | ✅ 10 statute digests Tier-1 | ✅ **107 templates** · litigation + commercial + Tier-3 specialist + procedural anchors complete (v0.2 closed 2026-05-28) | ✅ Migrated | ✅ LIVE |
| 🇺🇸 **USA** | ✅ 23 federal-first Tier-1 statute digests | ✅ **89 templates** · all 13 litigation categories + commercial + corporate complete (v0.2 closed 2026-05-29) | ✅ Migrated | ✅ LIVE |

**Plus:**
- **AI Startup Firm — India v0.1** (legal-ops brain for founders)
- **GC In-House Brain** (multi-jurisdictional, 8 modules — 3 live · 5 shipping v0.2+)

Both share the same `drafting-agents-core` architecture pattern.

All firms migrated to the central [drafting-agents-core](https://github.com/Wolfgangrush/drafting-agents-core) agent library on 2026-05-20 (Path B-Lite) — single source of truth for the agent layer; jurisdictional knowledge stays per-firm.

---

## 📚 Documentation

| File | What it covers |
|---|---|
| [GETTING_STARTED.md](GETTING_STARTED.md) + 6 language variants | Layman-friendly 30-minute tour |
| [MAC_INSTALL.md](MAC_INSTALL.md) | Mac-specific install with common gotchas |
| [DISCLAIMER.md](DISCLAIMER.md) | Full legal disclaimer · ABA Model Rules · state UPL · CCPA + state-privacy · HIPAA · cross-border · DMCA + GitHub safe harbor |
| [NO_PII_NO_DATA.md](NO_PII_NO_DATA.md) | Zero-collection architecture · CCPA controller analysis · HIPAA · GLBA · FERPA · COPPA |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting · CVE policy · coordinated disclosure |
| [MODEL_SETUP.md](MODEL_SETUP.md) | Honest privacy table · local vs cloud · third-party CLI tool warning |
| [SCOPE.md](SCOPE.md) | v0.1 Federal scope · v0.2+ per-state · falsification rules |
| [KNOWLEDGE_PROVENANCE.md](KNOWLEDGE_PROVENANCE.md) | Every domain claim's source (CITED:<research-file>) |
| [TRANSLATION_HELP_WANTED.md](TRANSLATION_HELP_WANTED.md) | Community call for native-speaker translation PRs |

---

## 🙏 Credits

- **Engine — all architectural credit:** a local memory architecture — a local memory architecture.
- **Publisher:** [wolfgang_rush](https://github.com/Wolfgangrush) — an Indian advocate (High Courts of India, India). MIT-licensed legal-tech publisher.
- **Inspired by:** every US solo attorney who's worked late on a federal motion-to-dismiss reply brief due Monday 9 AM.

---

## ⚠️ Disclaimer

This tool helps you organize your practice. It does **NOT** give legal advice. It does **NOT** replace your professional judgment. It does **NOT** solicit work on your behalf. ABA Rule 7 advertising firewall is built in but **YOU** remain responsible for compliance with all state bar conduct rules, ABA Model Rules adopted by your state, state UPL statutes, federal sectoral law (HIPAA · GLBA · FERPA · COPPA), CCPA + state-privacy laws, and any state-bar advisory opinions on AI tool use.

The publisher is not admitted in any US jurisdiction. The publisher does not offer legal services in the United States. This is a software publication under the MIT License.

Ships AS-IS without warranty. See [LICENSE](LICENSE).

---

## 📞 Support

- **Issues / bugs:** https://github.com/Wolfgangrush/ai-law-firm-usa/issues
- **Translation help:** [TRANSLATION_HELP_WANTED.md](TRANSLATION_HELP_WANTED.md) (Spanish · Chinese · Tagalog · Vietnamese · Arabic · French PRs welcome)
- **State-specific feature request?** Open an issue with `[state-CA]` / `[state-NY]` / etc. label
- **Federal feature request?** Open an issue with `[federal]` label

---

`Let's begin. Comencemos. 让我们开始. Magsimula tayo. Hãy bắt đầu. لنبدأ. Commençons.` 🙏
