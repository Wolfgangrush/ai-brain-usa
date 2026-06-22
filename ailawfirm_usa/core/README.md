# core/ — Shared Domain Logic

Modules in `core/` are used by BOTH solo and firm modes:
- `ontology.py` — MatterType, IndianCourt, IndianStatute, BarCouncilRule enums + Matter and Citation dataclasses
- `courts/` — court hierarchy lookups, jurisdiction rules
- `citations/` — Indian citation format parsers (AIR, SCC, SCC OnLine)
- `statutes/` — DPDP, IT Act, CPC, BNSS, BNS, BSA, Contract Act, Evidence Act, BCI Rules (v0.2+ adds real text)

Anything that depends on the legal *jurisdiction* (India-specific facts) lives here.
Anything that depends on the *practice size* (solo vs firm) lives in `solo/` or `firm/`.
