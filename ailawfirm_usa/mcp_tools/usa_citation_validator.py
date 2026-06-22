"""
usa_citation_validator MCP tool — v0.1 (Bluebook 21st ed).

Validates and parses US legal citations in Bluebook format:
- SCOTUS cases: Name v. Name, 347 U.S. 483 (1954)
- Circuit cases: Name v. Name, 122 F.3d 1274 (9th Cir. 1997)
- District cases: Name v. Name, 111 F. Supp. 2d 111 (D. Mass. 2000)
- US Code: 42 U.S.C. § 1983 (2018)
- CFR regulations: 29 C.F.R. § 825.100 (2024)

PROVENANCE: CITED:13-citation-format-primary.md
"""

import re

_CASE_PATTERN = re.compile(
    r"^(?P<name>.+?\s+v\.\s+.+?),?\s+"
    r"(?P<vol>\d+)\s+"
    r"(?P<reporter>U\.S\.|S\.\s*Ct\.|F\.\d?d|F\.\s*Supp\.\s*\d?d?|F\.4th|P\.\d?d|A\.\d?d|So\.\s*\d?d|N\.E\.\d?d|N\.W\.\d?d|P\.\d?d)\s+"
    r"(?P<page>\d+)"
    r"(\s*\((?P<court>[^)]*?)\s*(?P<year>\d{4})\))?$"
)

_USC_PATTERN = re.compile(
    r"^(?P<title>\d+)\s+U\.S\.C\.\s+§+\s*(?P<section>[\d.()a-zA-Z\-]+)"
    r"(\s+\((?P<year>\d{4})\))?$"
)

_CFR_PATTERN = re.compile(
    r"^(?P<title>\d+)\s+C\.F\.R\.\s+§+\s*(?P<section>[\d.()a-zA-Z\-]+)"
    r"(\s+\((?P<year>\d{4})\))?$"
)

_CONST_PATTERN = re.compile(
    r"^U\.S\.\s+Const\.\s+art\.?\s*(?P<article>[IVX]+)"
    r"(,\s*§\s*(?P<section>\d+))?(\s*cl\.\s*(?P<clause>\d+))?$"
)

_REPORTER_FORMAL = {
    "U.S.": "United States Reports",
    "S. Ct.": "Supreme Court Reporter",
    "F.3d": "Federal Reporter, Third Series",
    "F.4th": "Federal Reporter, Fourth Series",
    "F. Supp. 2d": "Federal Supplement, Second Series",
    "F. Supp. 3d": "Federal Supplement, Third Series",
}


def usa_citation_validator(citation_string: str) -> dict:
    """Parse and validate a US legal citation (Bluebook 21st ed).

    Returns:
        dict with:
        - raw, format, valid, parse_notes
        - format-specific fields (volume, reporter, page, year, court, title, section)
    """
    if not isinstance(citation_string, str):
        return {
            "raw": str(citation_string),
            "format": "UNKNOWN",
            "valid": False,
            "parse_notes": "input was not a string",
        }

    s = citation_string.strip()

    # US Constitution
    m = _CONST_PATTERN.match(s)
    if m:
        return {
            "raw": s,
            "format": "CONSTITUTION",
            "valid": True,
            "parse_notes": "U.S. Constitution citation recognized",
            "article": m.group("article"),
            "section": m.group("section"),
            "clause": m.group("clause"),
        }

    # US Code
    m = _USC_PATTERN.match(s)
    if m:
        return {
            "raw": s,
            "format": "USC",
            "valid": True,
            "parse_notes": "U.S. Code citation recognized",
            "title_num": int(m.group("title")),
            "section": m.group("section"),
            "year": int(m.group("year")) if m.group("year") else None,
        }

    # CFR
    m = _CFR_PATTERN.match(s)
    if m:
        return {
            "raw": s,
            "format": "CFR",
            "valid": True,
            "parse_notes": "Code of Federal Regulations citation recognized",
            "title_num": int(m.group("title")),
            "section": m.group("section"),
            "year": int(m.group("year")) if m.group("year") else None,
        }

    # Case citation (SCOTUS / Circuit / District)
    m = _CASE_PATTERN.match(s)
    if m:
        reporter = m.group("reporter").strip()
        formal = _REPORTER_FORMAL.get(reporter, reporter)

        if reporter == "U.S.":
            fmt = "SCOTUS"
        elif reporter in ("S. Ct.",):
            fmt = "SCOTUS_SCT"
        elif reporter in ("F.4th", "F.3d", "F.2d", "F."):
            fmt = "FED_CIRCUIT"
        elif "Supp." in reporter:
            fmt = "FED_DISTRICT"
        else:
            fmt = "STATE_CASE"

        return {
            "raw": s,
            "format": fmt,
            "valid": True,
            "parse_notes": f"{formal} citation recognized",
            "volume": int(m.group("vol")),
            "reporter": reporter,
            "reporter_full": formal,
            "page": int(m.group("page")),
            "year": int(m.group("year")) if m.group("year") else None,
            "court": m.group("court").strip() if m.group("court") else None,
        }

    return {
        "raw": s,
        "format": "UNKNOWN",
        "valid": False,
        "parse_notes": "Could not parse as Bluebook case, USC, CFR, or Constitution citation",
    }
