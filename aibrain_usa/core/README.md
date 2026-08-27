# core/ — Shared Domain Logic

Modules in `core/` are used by BOTH solo and firm modes:
- `ontology.py` — MatterType, USCourt, USStatute, USBarRule enums + Matter and Citation dataclasses
- `courts/` — federal + state court hierarchy lookups, jurisdiction / venue rules
- `citations/` — US Bluebook citation parsers (U.S., S. Ct., F.2d/3d/4th, F. Supp., U.S.C., C.F.R.)
- `statutes/` — FRCP, FRE, 28 U.S.C., ABA Model Rules, DGCL, CCPA/CPRA, Title 11, UCC, et al. (v0.2+ adds real text)

Anything that depends on the legal *jurisdiction* (US federal + state facts) lives here.
Anything that depends on the *practice size* (solo vs firm) lives in `solo/` or `firm/`.
