# Welcome, Counselor — your AI Brain starts here

You don't need to be a programmer. You need a laptop (Mac or Windows), an internet connection for setup, and 30 minutes. If you can copy-paste, you can run this.

> **Español:** [GETTING_STARTED_SPANISH.md](GETTING_STARTED_SPANISH.md)
> **中文:** [GETTING_STARTED_CHINESE.md](GETTING_STARTED_CHINESE.md)
> **Tagalog:** [GETTING_STARTED_TAGALOG.md](GETTING_STARTED_TAGALOG.md)
> **Tiếng Việt:** [GETTING_STARTED_VIETNAMESE.md](GETTING_STARTED_VIETNAMESE.md)
> **العربية:** [GETTING_STARTED_ARABIC.md](GETTING_STARTED_ARABIC.md)
> **Français:** [GETTING_STARTED_FRENCH.md](GETTING_STARTED_FRENCH.md)
> **Mac install:** [MAC_INSTALL.md](MAC_INSTALL.md)
> **Connecting an AI model:** [MODEL_SETUP.md](MODEL_SETUP.md)

---

## What this is, in one paragraph

A free tool that turns your laptop into a small private law office assistant. It remembers your matters (every case, every party, every order, every hearing date). It validates Bluebook citations. It tells you which federal court has jurisdiction over what. It flags ABA Model Rule 7 risks and CCPA compliance issues. It runs **on your own computer** — no cloud, no upload, no third party reads your client data. MIT licensed. You own everything you put into it.

## Why a US solo practitioner should care

BigLaw has armies of associates for cite-checking, matter management, and drafting. You have yourself and a laptop. This is your second brain.

- **You forget less.** Months-old matter context comes back instantly.
- **You miss fewer deadlines.** Hearing dates, filing deadlines, and statutes of limitations are tracked.
- **You stay ABA-compliant.** Built-in firewall flags Model Rule 7 publicity risks, MR 5.5 multijurisdictional practice issues, and MR 1.6 confidentiality concerns.
- **You save money.** Westlaw/PACER/LexisNexis subscriptions cost thousands per year. This is $0.
- **You stay private.** Client matters NEVER leave your laptop.
- **You can scale.** When you hire your first associate, switch from solo to firm mode — same tool, same data.

## What's inside

7 specialists living in your terminal:

1. **The Receptionist (brain)** — figures out what you need and routes to the right specialist.
2. **The Citation Clerk** — validates Bluebook citations (SCOTUS, F.3d, F.Supp.3d, U.S.C., C.F.R.).
3. **The Court Registrar** — knows federal courts. SCOTUS, 13 circuits, 94 districts, bankruptcy, tax.
4. **The Matter Manager** — holds your active case files (parties, hearings, orders, deadlines).
5. **The Drafting Assistant** — connects to wolfgang_rush drafting plugins (v0.2+).
6. **The Compliance Officer** — ABA MR 7, 5.5, 1.6, Formal Opinion 512 (AI ethics), CCPA/CPRA, FinCEN CTA.
7. **The Deadline Tracker** — statutes of limitations, filing deadlines, hearing dates (FRCP Rule 6 time computation).

## Your first 30 minutes

### Step 1 — Install Python (5 min)
- **Mac:** See [MAC_INSTALL.md](MAC_INSTALL.md)
- **Windows:** Use PowerShell, see [WINDOWS_INSTALL.md](WINDOWS_INSTALL.md)

### Step 2 — Install AI Brain USA
```bash
pip install git+https://github.com/Wolfgangrush/ai-law-firm-usa.git
```

### Step 3 — Connect an AI brain (10 min)

| Choice | Cost | Privacy |
|---|---|---|
| Ollama + local model | $0 forever | Best — nothing leaves your laptop |
| DeepSeek API | ~$5-15/month | Good — opt out of training data |
| Claude API / GPT-4 | ~$50-200/month | Strong — enterprise tier |

See [MODEL_SETUP.md](MODEL_SETUP.md) for exact setup.

### Step 4 — Your first interaction
```bash
ailawfirm_usa
```

```
═══════════════════════════════════════════════════════════════════
  AI Brain for USA Lawyers · v0.1.0

  Welcome · Bienvenido · 欢迎 · Mabuhay
  Chào mừng · أهلاً وسهلاً · Bienvenue
═══════════════════════════════════════════════════════════════════
  v0.1 = Federal-focused. State-specific modules in v0.2+.
  CURRENCY: ABA Opinion 512 · TCJA Sunset · NextGen Bar · UCC Art 12
═══════════════════════════════════════════════════════════════════
```

### Step 5 — Try these
```bash
ailawfirm_usa court "scotus"
ailawfirm_usa cite "347 U.S. 483 (1954)"
ailawfirm_usa cite "42 U.S.C. § 1983"
ailawfirm_usa calendar add --event-type hearing --title "Motion to Dismiss" --date 2026-06-15 --state NY
```

## Scope note

v0.1 is **Federal-focused.** It covers SCOTUS, federal circuit/district courts, FRCP/FRCrP/FRE, ABA Model Rules, and Bluebook citations. State-specific modules (CA CRC, NY CPLR, per-state bar rules) arrive in v0.2+. All 50 states are enumerated as placeholders. California, Texas, New York, Florida, Illinois, and Delaware have empty scaffolding ready to fill.

## Privacy

Everything runs locally. Your client matters, case files, and calendar data stay on your laptop. No cloud upload. No third-party access. No telemetry. The compliance agent's AI ethics flags reference ABA Formal Opinion 512 — but the flagging logic itself runs on your machine.

## Help

- [SCOPE.md](SCOPE.md) — exactly what's in scope for v0.1
- [KNOWLEDGE_PROVENANCE.md](KNOWLEDGE_PROVENANCE.md) — every claim traced to its research source
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to help
- [TRANSLATION_HELP_WANTED.md](TRANSLATION_HELP_WANTED.md) — improve the translations
