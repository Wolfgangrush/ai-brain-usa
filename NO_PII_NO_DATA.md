# NO_PII_NO_DATA — Zero-Collection Architecture (USA)

**This document explains, in detail, why AI Brain — USA collects no personal information from you, and what that means under CCPA · CPRA · state privacy laws · HIPAA · GLBA · FERPA.**

## The short version

The publisher (wolfgang_rush) operates **zero infrastructure** that touches your data. There is no server. There is no telemetry. There is no analytics. There is no "anonymous usage improvement data." The tool runs entirely on your laptop.

## The architectural guarantee

AI Brain — USA is **local-first** software. Specifically:

**(1) The codebase contains zero telemetry.** Verify with `grep -ri "telemetry\|analytics\|tracking\|requests.post\|urlopen" ailawfirm_usa/` — should return only legitimate cloud-AI calls (user-initiated, routed direct to your chosen vendor).

**(2) The publisher operates no server.** No AI Brain USA API. No cloud service. No database. The publisher's only infrastructure is the GitHub repository.

**(3) Storage is on your laptop.** Your matter data, citation cache, calendar entries, configuration live under `~/.ailawfirm-usa/`. The publisher has no access to this folder.

**(4) Network calls are limited to:**
- Package installation (PyPI during `pip install`)
- User-initiated AI cloud calls (if you opt into cloud mode — direct to vendor, not through publisher)
- Optional update checks (v0.2+ if added — will be opt-in and check GitHub releases only)

## Cloud-mode (when you opt in)

If you choose to use cloud AI processing, your queries route **directly from your laptop to the AI vendor**. The publisher is not in the data path. The contract for cloud-mode usage is between **you** and the **AI vendor** under their terms of service.

For client-confidential work — and ESPECIALLY for HIPAA-PHI · GLBA-NPI · attorney-client privileged communications — do NOT use cloud mode unless you have a BAA / data-processing agreement with the cloud vendor that you have independently verified. Use the local-only mode. See [MODEL_SETUP.md](MODEL_SETUP.md).

## CCPA · CPRA · state privacy law analysis

Under California's CCPA (as amended by CPRA) and analogous state laws:

**The publisher is NOT a "business."** CCPA defines a "business" as an entity that collects personal information of California consumers and determines the purposes/means of processing (§1798.140(d)). The publisher collects no personal information.

**The publisher is NOT a "service provider."** A service provider processes personal information on behalf of a business pursuant to a written contract (§1798.140(ag)). The publisher processes no personal information for anyone.

**The publisher is NOT a "third party."** Third party status under CCPA presupposes data being sold/shared/processed. None occurs.

**The publisher is a software publisher.** Publishing open-source software is not "collecting personal information" under CCPA §1798.140(c). It is publication activity governed by federal copyright law (17 USC) and First Amendment principles, not state consumer-privacy law.

If you use the tool to process personal information of California consumers, **you** are the business under CCPA. Your obligations apply (consumer right-to-know · right-to-delete · right-to-correct · right-to-opt-out-of-sale-or-share · right-to-limit-use-of-sensitive-PI · DSAR handling within 45 days · DPIA for high-risk processing · notice at collection · privacy-policy posting · contracts with service providers · etc.).

Analogous analysis applies to:
- **Virginia VCDPA** — controller/processor framework similar to GDPR
- **Colorado CPA** — DPIAs required for high-risk processing
- **Connecticut CTDPA** — consumer rights similar to CCPA
- **Utah UCPA** — narrower obligations
- **Texas TDPSA** — broad consumer protection
- **Oregon OCPA · Montana MCDPA · Tennessee TIPA · other state laws** — all share the controller-not-collector distinction

## HIPAA (if applicable)

The publisher is NOT a Covered Entity, Business Associate, or Subcontractor under HIPAA. The publisher does not handle PHI on any server.

If your practice handles PHI and you enable cloud mode without a HIPAA-compliant BAA with the cloud vendor, you create HIPAA exposure. Do NOT enable cloud mode for PHI without an executed BAA with the vendor. Local-only mode (Ollama on your laptop) keeps PHI on a device you control.

## GLBA · FERPA · COPPA (if applicable)

The publisher is not a Financial Institution under GLBA, an Educational Agency under FERPA, or an Operator collecting children's data under COPPA. Sectoral obligations apply to YOU as the user; the tool's local-only mode supports compliance by keeping data on your device.

## Cross-border data transfer

If you opt into cloud mode and the cloud vendor processes data outside the US (or in a US data center subject to foreign access), the transfer is YOUR action. Your obligations under any applicable state cross-border rules apply.

## Verification path

You can independently verify zero-collection:

1. `grep -ri "telemetry\|analytics\|posthog\|mixpanel\|segment\|amplitude\|google-analytics\|datadog\|sentry" ailawfirm_usa/` — should return zero results.
2. `cat requirements.txt` — no analytics or telemetry libraries.
3. Run the tool offline — should work fully (cloud-AI calls will fail, which is expected and visible).
4. Inspect network traffic with `nettop` (macOS) / `nethogs` (Linux) / Resource Monitor (Windows) — should show traffic only to user-initiated cloud-AI endpoints if cloud mode is on.

## If this changes

If a future version adds telemetry, opt-in update checks, or any cloud touchpoint involving the publisher's infrastructure, that change will be:
- Announced in CHANGELOG
- Default OFF · user-opt-in only
- Documented in this file with the change date and specific data category

This file always represents the current state. If it differs from the code, the code is the truth — file an issue.

---

*This document references LEGAL_EXPOSURE_PLAYBOOK §2(b) (Zero Data Collection pillar), §3.V4 (Data Protection — US state laws + HIPAA + GLBA + FERPA), §3.V9 (Conduct-Rule Inducement — ABA Model Rule 1.6). Playbook version: v0.1.*
