# Mabuhay, abogado — magsisimula ang iyong AI Brain dito

Hindi mo kailangang maging programmer. Kailangan mo ng laptop (Mac o Windows), internet para sa pag-install, at 30 minuto. Kung kaya mong mag-copy-paste, kaya mong patakbuhin ito.

> **English:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

## Ano ito, sa isang talata

Isang libreng tool na ginagawang maliit na pribadong law office assistant ang iyong laptop. Naaalala nito ang iyong mga kaso (bawat case file, bawat partido, bawat order, bawat hearing date). Vina-validate nito ang Bluebook citations. Sinasabi nito kung aling federal court ang may hurisdiksyon. Tina-flag nito ang ABA Model Rule 7 na mga panganib at CCPA compliance issues. Tumatakbo ito **sa sarili mong computer** — walang cloud, walang upload, walang third party na nagbabasa ng client data mo. MIT licensed. Pagmamay-ari mo ang lahat ng inilagay mo rito.

## Bakit dapat mong alalahanin bilang US solo practitioner

Ang BigLaw ay may mga hukbo ng associates para sa cite-checking, matter management, at drafting. Ikaw ay may sarili mo at isang laptop. Ito ang iyong pangalawang utak.

- **Mas kaunti ang nakakalimutan.** Buwan nang lumang konteksto ng kaso ay bumabalik agad.
- **Mas kaunti ang na-mi-miss na deadline.** Ang hearing dates, filing deadlines, at statutes of limitations ay sinusubaybayan.
- **Nanatili kang ABA-compliant.** Ang built-in na firewall ay nagfa-flag ng Model Rule 7 publicity risks, MR 5.5 multijurisdictional practice issues, at MR 1.6 confidentiality concerns.
- **Nakatitipid ka ng pera.** Ang Westlaw/PACER/LexisNexis ay nagkakahalaga ng libo-libo bawat taon. Ito ay $0.
- **Nanatiling pribado ang data mo.** Ang client matters ay HINDI umaalis sa iyong laptop.
- **Pwede kang mag-scale.** Kapag nag-hire ka ng unang associate, lumipat mula solo patungong firm mode — parehong tool, parehong data.

## Ano ang nasa loob

7 espesyalista na nakatira sa iyong terminal:

1. **Ang Receptionist (utak)** — inaalam kung ano ang kailangan mo at niruruta sa tamang espesyalista.
2. **Ang Citation Clerk** — nagva-validate ng Bluebook citations (SCOTUS, F.3d, F.Supp.3d, U.S.C., C.F.R.).
3. **Ang Court Registrar** — alam ang federal courts. SCOTUS, 13 circuits, 94 districts, bankruptcy, tax.
4. **Ang Matter Manager** — hawak ang iyong aktibong case files (mga partido, hearing, order, deadline).
5. **Ang Drafting Assistant** — kumokonekta sa wolfgang_rush drafting plugins (v0.2+).
6. **Ang Compliance Officer** — ABA MR 7, 5.5, 1.6, Formal Opinion 512 (AI ethics), CCPA/CPRA, FinCEN CTA.
7. **Ang Deadline Tracker** — statutes of limitations, filing deadlines, hearing dates (FRCP Rule 6 time computation).

## Mabilis na pag-install

```bash
pip install git+https://github.com/Wolfgangrush/ai-law-firm-usa.git
ailawfirm_usa
```

## Subukan

```bash
ailawfirm_usa court "scotus"
ailawfirm_usa cite "347 U.S. 483 (1954)"
ailawfirm_usa cite "42 U.S.C. § 1983"
```

## Sakop

Ang v0.1 ay **nakatutok sa Federal.** Sinasaklaw nito ang SCOTUS, federal circuit/district courts, FRCP/FRCrP/FRE, ABA Model Rules, at Bluebook citations. Ang state-specific modules (CA CRC, NY CPLR, per-state bar rules) ay darating sa v0.2+. Lahat ng 50 estado ay naka-enumerate bilang mga placeholder.

## Pagkapribado

Lahat ay tumatakbo nang lokal. Ang iyong client matters, case files, at calendar data ay nananatili sa iyong laptop. Walang cloud upload. Walang third-party access. Walang telemetry.
