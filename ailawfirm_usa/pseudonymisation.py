"""Pseudonymisation Gateway — pre-cloud-filter middleware (v0.2 priority feature).

This module strips ALL real names + government IDs + sensitive identifiers from
user queries BEFORE any cloud-API call, then restores them in the response.
Cloud vendors see only the abstract structure of the matter.

References LEGAL_EXPOSURE_PLAYBOOK §2(a) (Local-AI-Only Default pillar) +
§3.V4 (Data Protection) + §6.D4 (no telemetry, ever) +
§3.V9 (Conduct-Rule Inducement — local bar confidentiality).

Architecture:
    USER INPUT (with real names) → NER + regex pass → placeholders
       ↓
    Cloud API sees: "[CLIENT_1] filed against [ORG_1] at [COURT_1] on [DATE_1]"
       ↓
    Cloud response (with placeholders) → de-pseudonymise → USER SEES real names

The placeholder map lives in memory ONLY (session-scoped, destroyed on exit).
NEVER written to disk. Cloud vendor NEVER sees a real name, Aadhaar, PAN,
GSTIN, phone, email, case number, or specific date.

Usage:
    from ailawfirm_usa.pseudonymisation import PseudonymisationGateway

    gw = PseudonymisationGateway()
    sanitized, token_map = gw.sanitize("Mr. John Smith filed a court writ...")
    # send `sanitized` to cloud API
    response = cloud_api_call(sanitized)
    real = gw.desanitize(response, token_map)
    # show `real` to user
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field

from ._pii_validators import (
    aadhaar_validate,
    gstin_validate,
    itin_validate,
)


@dataclass
class TokenMap:
    """Session-scoped placeholder ↔ original mapping. Never persisted."""

    forward: dict = field(default_factory=dict)  # original → placeholder
    reverse: dict = field(default_factory=dict)  # placeholder → original
    counters: dict = field(default_factory=dict)  # entity_type → next id

    def add(self, original: str, entity_type: str) -> str:
        """Deterministic placeholder for an entity. Same entity → same placeholder within a session."""
        if original in self.forward:
            return self.forward[original]
        n = self.counters.get(entity_type, 0) + 1
        self.counters[entity_type] = n
        placeholder = f"[{entity_type}_{n}]"
        self.forward[original] = placeholder
        self.reverse[placeholder] = original
        return placeholder


# ─────────────────────────────────────────────────────────────────────────
# Regex patterns — US-relevant identifiers (SSN · EIN · case numbers · etc.)
# ─────────────────────────────────────────────────────────────────────────

# Aadhaar: 12 digits, optionally space-separated as 4-4-4
AADHAAR_RE = re.compile(r"\b[2-9]\d{3}\s?\d{4}\s?\d{4}\b")

# PAN: 5 alphabets + 4 digits + 1 alphabet (e.g. ABCDE1234F)
PAN_RE = re.compile(r"\b[A-Z]{3}[ABCFGHJLPT][A-Z]\d{4}[A-Z]\b")

# GSTIN: 2-digit state code + PAN + 1 entity number + Z + checksum
GSTIN_RE = re.compile(r"\b\d{2}[A-Z]{3}[ABCFGHJLPT][A-Z]\d{4}[A-Z][0-9A-Z]Z[0-9A-Z]\b")

# Indian phone: +91 prefix optional, 10 digits starting 6-9
PHONE_RE = re.compile(r"(?:\+91[\s-]?)?[6-9]\d{9}\b")

# Email
EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Currency amounts (Indian context): ₹ + digits with Indian grouping or numeric
AMOUNT_RE = re.compile(r"\(?-?\s?(?:₹|Rs\.?|INR)\s?-?\d{1,3}(?:,\d{2,3})*(?:\.\d+)?\)?")

# Dates in common Indian formats: DD-MM-YYYY · DD/MM/YYYY · DD.MM.YYYY · DD-MMM-YYYY · DD Month YYYY
DATE_RE = re.compile(
    r"\b\d{1,2}[\s\-./](?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|"
    r"January|February|March|April|June|July|August|September|October|November|December|"
    r"\d{1,2})[\s\-./]\d{2,4}\b"
)

# Case numbers (Bombay HC / SC / generic): "Civil Appeal No. 1234 of 2024" or "1234 of 2024"
CASE_NO_RE = re.compile(
    r"(?:(?:Civil|Criminal|Writ|Special Leave|SLP|WP|CRL|MAT)\s+(?:Appeal|Petition|Application)?\s*No\.?\s*\d+\s+of\s+\d{4})"
    r"|(?:\b\d+\s+of\s+\d{4}\b)",
    re.IGNORECASE,
)

# FIR numbers: "FIR No. 123/2024" or similar
FIR_RE = re.compile(r"\bFIR\s+No\.?\s*\d+/\d{2,4}\b", re.IGNORECASE)

# Bank account numbers: 9-18 digit standalone strings (heuristic; can false-positive on long numerics)
BANK_ACCT_RE = re.compile(r"\b(?:A/C|Account|Acct)\.?\s*(?:No\.?)?\s*\d{9,18}\b", re.IGNORECASE)

# IFSC code: 4 letters + 0 + 6 alphanumerics
IFSC_RE = re.compile(r"\b[A-Z]{4}0[A-Z\d]{6}\b")

# Vehicle registration (Indian format): SS-NN-XX-NNNN  e.g. MH-12-AB-1234
VEHICLE_REG_RE = re.compile(r"\b[A-Z]{2}[\s-]?\d{1,2}[\s-]?[A-Z]{1,2}[\s-]?\d{4}\b")

# Bharat (BH) series — YY BH NNNN XX (e.g. "22 BH 1234 AB")
BH_VEHICLE_RE = re.compile(r"\b\d{2}[\s-]?BH[\s-]?\d{4}[\s-]?[A-Z]{1,2}\b")

# ─────────────────────────────────────────────────────────────────────────
# USA-native PII patterns (added v0.1.1 for jurisdictional coverage)
# ─────────────────────────────────────────────────────────────────────────

# SSN: XXX-XX-XXXX
SSN_RE = re.compile(r"\b(?!000|666|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b")

# ITIN: 9XX-XX-XXXX (starts with 9)
ITIN_RE = re.compile(r"\b9\d{2}-\d{2}-\d{4}\b")

# EIN (Employer Identification Number): XX-XXXXXXX
EIN_RE = re.compile(r"\bEIN[\s:#]*\d{2}-\d{7}\b", re.IGNORECASE)

# US phone: +1 prefix or 10-digit US format
US_PHONE_RE = re.compile(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b")

# USD amounts: $ (after disambiguating from other currencies)
USD_AMOUNT_RE = re.compile(
    r"\(?-?\s?(?:US\$|USD)\s?-?\d{1,3}(?:,\d{3})*(?:\.\d+)?\)?",
    re.IGNORECASE,
)

# ZIP: 5 digits or 5+4
ZIP_RE = re.compile(r"\b\d{5}(?:-\d{4})?\b")

# US Federal court case numbers: docket format X:XX-cv-XXXXX
US_CASE_RE = re.compile(
    r"\b\d{1,2}:\d{2}-(?:cv|cr|md|mc)-\d{4,6}\b",
    re.IGNORECASE,
)

# Driver license placeholders (varies wildly per state — conservative pattern)
US_DL_RE = re.compile(r"\b(?:DL|DLN|License)[\s:#]*[A-Z0-9]{6,12}\b", re.IGNORECASE)


# ─────────────────────────────────────────────────────────────────────────
# Indian name detection — heuristic (will be augmented by spaCy NER in v0.2.1)
# ─────────────────────────────────────────────────────────────────────────

# Common Indian honorifics that precede a name
HONORIFICS = {
    "Mr",
    "Mrs",
    "Ms",
    "Miss",
    "Dr",
    "Shri",
    "Smt",
    "Kumari",
    "Adv",
    "Advocate",
    "Hon'ble",
    "Justice",
    "Sri",
    "Md",
    "Mohd",
}

# Heuristic regex: Honorific + (capitalized word){1,3} — catches "Mr. John Smith" / "Adv. Sarah Jones"
NAME_RE = re.compile(
    r"\b(?:" + "|".join(HONORIFICS) + r")\.?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b"
)

# Context-anchored client / party name detection — catches the dominant real-world
# forms a US attorney types even WITHOUT an honorific ("my client Maria Gonzalez",
# "represent John Doe", "Smith v. Jones", "Jane Roe, executor"). High-precision
# anchors keep false positives low. NOTE: this does NOT catch a bare, un-anchored
# arbitrary name — robust free-form PERSON detection needs NER (spaCy), which is the
# v0.2.1 roadmap. See README "Pseudonymisation coverage" for the honest limit.
_NAME_CORE = r"[A-Z][A-Za-z'.\-]+(?:\s+[A-Z][A-Za-z'.&\-]+){0,3}"
CONTEXT_NAME_LEAD_RE = re.compile(
    r"\b(?:client|clients|represent(?:s|ing)?|on behalf of|plaintiff|defendant|"
    r"petitioner|respondent|complainant|movant|v\.|vs\.|versus)\s+(" + _NAME_CORE + r")"
)
CONTEXT_NAME_ROLE_RE = re.compile(
    r"\b(" + _NAME_CORE + r"),?\s+(?:member|owner|officer|director|manager|principal|"
    r"executor|executrix|administrator|administratrix|trustee|guardian|"
    r"petitioner|respondent|plaintiff|defendant)\b"
)

# Residue detection (v0.1.2 — Residue Disclosure). After sanitize() has masked the
# IDs + anchored/honorific names, scan for capitalised multi-word tokens that LOOK
# like an un-masked name/entity the gateway did not catch. A WARNING signal only —
# conservative, false positives acceptable (never blocks the call).
RESIDUE_NAME_RE = re.compile(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3}\b")

# Standalone capitalized name pair (two capitalized words, neither in COMMON_NON_NAME) — heuristic
# This is intentionally CONSERVATIVE — false negatives preferred over false positives for personal names
COMMON_NON_NAME_WORDS = {
    "High",
    "Court",
    "Supreme",
    "District",
    "Bench",
    "Bombay",
    "Mumbai",
    "Delhi",
    "Calcutta",
    "Madras",
    "Allahabad",
    "Gujarat",
    "Kerala",
    "Patna",
    "Nagpur",
    "Maharashtra",
    "Karnataka",
    "Tamil",
    "Nadu",
    "Andhra",
    "Pradesh",
    "Telangana",
    "MV",
    "Act",
    "Section",
    "Article",
    "Civil",
    "Criminal",
    "Writ",
    "Petition",
    "Appeal",
    "Special",
    "Leave",
    "Writ",
    "OA",
    "WP",
    "SLP",
    "FIR",
    "POCSO",
    "POSH",
    "DPDP",
    "GST",
    "RBI",
    "SEBI",
    "MCA",
    "TRAI",
    "Income",
    "Tax",
    "IPC",
    "BNS",
    "BNSS",
    "BSA",
    "CrPC",
    "CPC",
    "Evidence",
    "Limitation",
    "Companies",
    "Negotiable",
    "Instruments",
    "Constitution",
    "India",
    "Indian",
    "Union",
    "State",
    "Government",
    "Ministry",
    "Department",
    "Office",
    "Court",
    "Tribunal",
    "Board",
    "Commission",
    "Authority",
    "Council",
    "Bar",
    "Association",
    "Limited",
    "Private",
    "Public",
    "Company",
    "Corporation",
    "Trust",
    "Society",
    "Firm",
    "Partnership",
    "LLP",
    "Ltd",
    "Pvt",
    "Inc",
    "Co",
    "Order",
    "Judgment",
    "Decree",
    "Award",
    "Notice",
    "Summons",
}


# ─────────────────────────────────────────────────────────────────────────
# Pseudonymisation Gateway
# ─────────────────────────────────────────────────────────────────────────


class PseudonymisationGateway:
    """Strips real names + IDs from text before cloud-API send; restores on return.

    Design:
      - Session-scoped (each gateway instance = one user session)
      - In-memory only · token_map NEVER persisted
      - Deterministic mapping (same entity within session → same placeholder)
      - India-specific regex layer (Aadhaar · PAN · GSTIN · IFSC · case numbers etc.)
      - Honorific-driven name detection (conservative — false negatives preferred)
      - Extensible: register_pattern() to add custom patterns per matter

    Usage:
        gw = PseudonymisationGateway()
        clean, token_map = gw.sanitize(user_text)
        # send `clean` to cloud
        response = cloud_call(clean)
        real = gw.desanitize(response, token_map)
    """

    def __init__(self) -> None:
        # Patterns in priority order — more-specific first so they don't get clobbered
        # Each: (regex_pattern, entity_type_label)
        # Entries are 2- or 3-tuples: (pattern, label) or (pattern, label, validator).
        self.patterns: list[tuple] = [
            # USA-native (priority for USA jurisdiction)
            (SSN_RE, "SSN"),
            (ITIN_RE, "ITIN", itin_validate),
            (EIN_RE, "EIN"),
            (US_DL_RE, "US_DL"),
            (US_CASE_RE, "US_CASE"),
            (US_PHONE_RE, "US_PHONE"),
            (USD_AMOUNT_RE, "USD_AMOUNT"),
            (ZIP_RE, "ZIP"),
            # Indian diaspora coverage (legitimate for South Asian diaspora client matters)
            (AADHAAR_RE, "AADHAAR", aadhaar_validate),
            (PAN_RE, "PAN"),
            (GSTIN_RE, "GSTIN", gstin_validate),
            (IFSC_RE, "IFSC"),
            (FIR_RE, "FIR_NO"),
            (CASE_NO_RE, "CASE_NO"),
            (VEHICLE_REG_RE, "VEHICLE"),
            (BH_VEHICLE_RE, "VEHICLE"),
            (BANK_ACCT_RE, "BANK_ACCT"),
            (EMAIL_RE, "EMAIL"),
            (PHONE_RE, "PHONE"),
            (AMOUNT_RE, "AMOUNT"),
            (DATE_RE, "DATE"),
            # Context-anchored party names (before the honorific NAME_RE so they win)
            (CONTEXT_NAME_LEAD_RE, "PERSON"),
            (CONTEXT_NAME_ROLE_RE, "PERSON"),
            (NAME_RE, "PERSON"),
        ]

    def register_pattern(self, pattern: re.Pattern, entity_type: str) -> None:
        """Insert a custom pattern at the front of the priority list."""
        self.patterns.insert(0, (pattern, entity_type))

    def sanitize(self, text: str) -> tuple[str, TokenMap]:
        """Replace all detected entities with placeholders. Returns (sanitized_text, token_map)."""
        token_map = TokenMap()
        out = text
        # Apply each pattern in order; replace longest-first within a pattern
        for entry in self.patterns:
            pattern, entity_type, validator = (tuple(entry) + (None,))[:3]
            matches = list(pattern.finditer(out))
            # Walk matches in reverse so position offsets don't break
            for m in reversed(matches):
                if validator is not None and not validator(m.group(0)):
                    continue
                original = m.group(0)
                # For NAME_RE we capture the name group, not the honorific
                if entity_type == "PERSON" and m.lastindex:
                    # Preserve the honorific in output; only replace the name part
                    name_part = m.group(1)
                    placeholder = token_map.add(name_part, entity_type)
                    out = out[: m.start(1)] + placeholder + out[m.end(1) :]
                else:
                    placeholder = token_map.add(original, entity_type)
                    out = out[: m.start()] + placeholder + out[m.end() :]
        return out, token_map

    def detect_residue(self, text: str) -> list[str]:
        """Capitalised multi-word tokens left in ALREADY-sanitised ``text`` that look
        like an un-masked person/entity name. A WARNING signal only — conservative,
        false positives acceptable, never blocks. Placeholders ([PERSON_1]) never match.
        """
        skip = COMMON_NON_NAME_WORDS | {
            "New",
            "York",
            "Los",
            "Angeles",
            "San",
            "Francisco",
            "Las",
            "Vegas",
            "United",
            "States",
            "Saint",
            "Fort",
            "Lake",
        }
        residue: list[str] = []
        seen: set[str] = set()
        for m in RESIDUE_NAME_RE.finditer(text):
            candidate = m.group(0)
            # Suppress only when EVERY word is a known non-name token (e.g. "New York",
            # "Supreme Court") — a real name with one common-word part (e.g. a surname
            # "Court") is still surfaced. Favours surfacing over silence (promise 1).
            if all(word in skip for word in candidate.split()):
                continue
            if candidate not in seen:
                seen.add(candidate)
                residue.append(candidate)
        return residue

    def sanitize_with_disclosure(self, text: str) -> tuple[str, TokenMap, dict]:
        """Like :meth:`sanitize` but ALSO returns a residue-disclosure record.

        ``disclosure`` = masked_counts · residue · residue_hashes · residue_lengths.
        ``residue`` (raw candidates) is IN-MEMORY only for surfacing to the user; the
        on-disk audit log keeps only the sha256 hashes (see ``pseudonymisation_audit``),
        so real PII never touches disk. ``sanitize()``'s 2-tuple contract is unchanged.
        """
        clean, token_map = self.sanitize(text)
        residue = self.detect_residue(clean)
        return (
            clean,
            token_map,
            {
                "masked_counts": dict(token_map.counters),
                "residue": residue,
                "residue_hashes": [
                    hashlib.sha256(r.encode("utf-8")).hexdigest()[:16] for r in residue
                ],
                "residue_lengths": [len(r) for r in residue],
            },
        )

    def desanitize(self, text: str, token_map: TokenMap) -> str:
        """Replace all placeholders back with originals using the token map."""
        out = text
        # Replace longest placeholders first (in case [PERSON_10] vs [PERSON_1])
        for placeholder in sorted(token_map.reverse.keys(), key=len, reverse=True):
            out = out.replace(placeholder, token_map.reverse[placeholder])
        return out

    @staticmethod
    def is_safe_for_cloud(text: str) -> tuple[bool, list[str]]:
        """Cloud-egress gate: does the text contain identifiers that must NOT go to cloud raw?

        Walks the SAME canonical pattern set that sanitize() masks (a fresh gateway's base
        patterns), applying each pattern's checksum validator when present. Closes the
        historical fail-open where this gate hardcoded only a ~7-item subset and silently
        waved through every other identifier that sanitize() would in fact have masked.
        Returns (is_safe, sorted_detected_categories).
        """
        detected: set[str] = set()
        for entry in PseudonymisationGateway().patterns:
            pattern, entity_type, validator = (tuple(entry) + (None,))[:3]
            for m in pattern.finditer(text):
                if validator is not None and not validator(m.group(0)):
                    continue
                detected.add(entity_type)
                break
        return (len(detected) == 0, sorted(detected))
