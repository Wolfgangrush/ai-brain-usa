"""Checksum / structural validators for the embedded pseudonymisation gateway.

Vendored to parity with pseudonymisation-gateway v0.5 (Wolfgangrush). A validator
is ``str -> bool``; the gateway tokenises a regex match only when it returns True.
This adds detector precision (rejecting shaped-but-invalid look-alikes) without
weakening recall.
"""

from __future__ import annotations

import re

_VERHOEFF_D = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 2, 3, 4, 0, 6, 7, 8, 9, 5),
    (2, 3, 4, 0, 1, 7, 8, 9, 5, 6),
    (3, 4, 0, 1, 2, 8, 9, 5, 6, 7),
    (4, 0, 1, 2, 3, 9, 5, 6, 7, 8),
    (5, 9, 8, 7, 6, 0, 4, 3, 2, 1),
    (6, 5, 9, 8, 7, 1, 0, 4, 3, 2),
    (7, 6, 5, 9, 8, 2, 1, 0, 4, 3),
    (8, 7, 6, 5, 9, 3, 2, 1, 0, 4),
    (9, 8, 7, 6, 5, 4, 3, 2, 1, 0),
)
_VERHOEFF_P = (
    (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    (1, 5, 7, 6, 2, 8, 3, 0, 9, 4),
    (5, 8, 0, 9, 1, 4, 3, 7, 6, 2),
    (8, 9, 1, 6, 0, 4, 3, 5, 2, 7),
    (9, 4, 5, 3, 1, 2, 6, 8, 7, 0),
    (4, 2, 8, 6, 5, 7, 3, 9, 0, 1),
    (2, 7, 9, 3, 8, 0, 6, 4, 1, 5),
    (7, 0, 4, 6, 9, 1, 3, 2, 5, 8),
)


def _verhoeff_ok(digits: str) -> bool:
    c = 0
    for i, ch in enumerate(reversed(digits)):
        c = _VERHOEFF_D[c][_VERHOEFF_P[i % 8][int(ch)]]
    return c == 0


def aadhaar_validate(s: str) -> bool:
    """12 digits, first digit 2-9, valid Verhoeff check digit."""
    digits = re.sub(r"\D", "", s)
    if len(digits) != 12 or digits[0] in "01":
        return False
    return _verhoeff_ok(digits)


_GSTIN_CODEPOINTS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
_GSTIN_STATE_CODES = set(range(1, 39)) | {97, 99}


def _gstin_check_digit(first14: str) -> str:
    factor, total, mod = 2, 0, len(_GSTIN_CODEPOINTS)
    for ch in reversed(first14):
        prod = factor * _GSTIN_CODEPOINTS.index(ch)
        factor = 1 if factor == 2 else 2
        total += prod // mod + prod % mod
    return _GSTIN_CODEPOINTS[(mod - (total % mod)) % mod]


def gstin_validate(s: str) -> bool:
    s = s.strip().upper()
    if len(s) != 15 or not s[:2].isdigit():
        return False
    if int(s[:2]) not in _GSTIN_STATE_CODES:
        return False
    return _gstin_check_digit(s[:14]) == s[14]


def iban_validate(s: str) -> bool:
    """ISO 13616 mod-97."""
    iban = re.sub(r"\s", "", s).upper()
    if not (5 <= len(iban) <= 34):
        return False
    if not (iban[:2].isalpha() and iban[2:4].isdigit() and iban[4:].isalnum()):
        return False
    rearranged = iban[4:] + iban[:4]
    digits = "".join(str(int(ch, 36)) if ch.isalpha() else ch for ch in rearranged)
    return int(digits) % 97 == 1


_NRIC_WEIGHTS = (2, 7, 6, 5, 4, 3, 2)
_NRIC_ST_LETTERS = "JZIHGFEDCBA"
_NRIC_FG_LETTERS = "XWUTRQPNMLK"


def nric_validate(s: str) -> bool:
    """Singapore NRIC/FIN weighted check letter (M-series accepted on structure)."""
    s = s.strip().upper()
    if len(s) != 9:
        return False
    prefix, digits, check = s[0], s[1:8], s[8]
    if not digits.isdigit() or not check.isalpha():
        return False
    if prefix == "M":
        return True
    if prefix not in "STFG":
        return False
    total = sum(int(d) * w for d, w in zip(digits, _NRIC_WEIGHTS))
    if prefix in "TG":
        total += 4
    table = _NRIC_ST_LETTERS if prefix in "ST" else _NRIC_FG_LETTERS
    return table[total % 11] == check


def itin_validate(s: str) -> bool:
    """US ITIN: starts with 9; group number 70-88, 90-92, 94-99."""
    digits = s.replace("-", "")
    if len(digits) != 9 or not digits.isdigit() or digits[0] != "9":
        return False
    group = int(digits[3:5])
    return 70 <= group <= 88 or 90 <= group <= 92 or 94 <= group <= 99
