"""Acceptance tests (internal) for Residue Disclosure + Audit Log (v0.1.2).
The implementation must make ALL of these pass, plus the pre-existing suite.
Locks the two-promise reconciliation: residue is surfaced, but the on-disk audit log
contains NO raw PII (only sha256 hashes + counts)."""

import json
import re


from ailawfirm_usa.pseudonymisation import PseudonymisationGateway


# ── Feature A: detect_residue ────────────────────────────────────────────────
def test_detect_residue_flags_unanchored_name():
    gw = PseudonymisationGateway()
    # No honorific, no legal anchor -> current sanitize misses it -> must show as residue.
    clean, _ = gw.sanitize("Please also contact Sarah Bennett about the exhibits.")
    residue = gw.detect_residue(clean)
    assert any("Sarah Bennett" == r for r in residue), residue


def test_detect_residue_ignores_placeholders_and_common_words():
    gw = PseudonymisationGateway()
    text = "The [PERSON_1] matter is before the Supreme Court in New York."
    residue = gw.detect_residue(text)
    assert "[PERSON_1]" not in residue
    assert "Supreme Court" not in residue
    assert "New York" not in residue


# ── Feature B: sanitize_with_disclosure ──────────────────────────────────────
def test_sanitize_with_disclosure_shape():
    gw = PseudonymisationGateway()
    clean, tmap, disc = gw.sanitize_with_disclosure(
        "Draft for my client Maria Gonzalez; also contact Sarah Bennett."
    )
    assert "Maria Gonzalez" not in clean  # anchored name masked
    assert isinstance(disc["masked_counts"], dict)
    assert disc["masked_counts"].get("PERSON", 0) >= 1
    assert "Sarah Bennett" in disc["residue"]  # un-anchored name surfaced as residue
    # hashes are 16-char hex and are NOT the raw text
    for raw, h in zip(disc["residue"], disc["residue_hashes"]):
        assert re.fullmatch(r"[0-9a-f]{16}", h)
        assert raw != h


def test_sanitize_signature_unchanged_backcompat():
    gw = PseudonymisationGateway()
    out = gw.sanitize("Mr. John Smith filed.")  # must still be a 2-tuple
    assert isinstance(out, tuple) and len(out) == 2


# ── Feature C: write_audit (PII-FREE on disk) ────────────────────────────────
def test_write_audit_is_pii_free(tmp_path):
    from ailawfirm_usa.pseudonymisation_audit import write_audit

    disc = {
        "masked_counts": {"PERSON": 2, "SSN": 1},
        "residue": ["Sarah Bennett"],
        "residue_hashes": ["deadbeefdeadbeef"],
        "residue_lengths": [13],
    }
    path = write_audit(
        disc, model="glm-5.2", base_url="https://api.z.ai/api/anthropic", config_dir=str(tmp_path)
    )
    assert path is not None
    content = open(path).read()
    # CRITICAL: raw PII must NOT be on disk; only the hash.
    assert "Sarah Bennett" not in content
    assert "deadbeefdeadbeef" in content
    rec = json.loads(content.strip().splitlines()[-1])
    assert rec["masked_counts"]["PERSON"] == 2
    assert rec["residue_count"] == 1
    # host only, no full URL path / key
    assert rec["base_url_host"] == "api.z.ai"


def test_write_audit_swallows_io_errors():
    from ailawfirm_usa.pseudonymisation_audit import write_audit

    # An unwritable config dir must yield None, never raise.
    out = write_audit(
        {"masked_counts": {}, "residue": [], "residue_hashes": [], "residue_lengths": []},
        model="m",
        base_url="https://x.test",
        config_dir="/proc/nonexistent_ro_dir_xyz",
    )
    assert out is None


# ── Feature D: llm.complete wiring (mocked network) ──────────────────────────
class _FakeResp:
    def __init__(self, body):
        self._b = body.encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_llm_complete_audits_and_still_replies(monkeypatch, tmp_path):
    from ailawfirm_usa.brain import llm

    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://api.z.ai/api/anthropic")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "k")
    monkeypatch.setenv("ANTHROPIC_MODEL", "glm-5.2")
    monkeypatch.setenv("HOME", str(tmp_path))  # audit lands under tmp HOME
    seen = {}

    def fake_urlopen(request, *a, **k):
        seen["body"] = request.data.decode("utf-8")
        return _FakeResp(json.dumps({"content": [{"text": "Re [PERSON_1] and Sarah Bennett."}]}))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    out = llm.complete("sys", "Draft for my client Maria Gonzalez; contact Sarah Bennett.")
    assert "Maria Gonzalez" not in seen["body"]  # anchored name never hit the wire
    assert "Maria Gonzalez" in out  # restored in reply


# ── review hardening (2026-07-12): locks fixes #3 (ZIP) + #4 (residue skip) ──
def test_zip_code_is_now_masked():
    """finding #3: ZIP_RE was defined but unregistered — README claimed ZIP coverage."""
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("Serve the notice to the office at 90210 by Friday.")
    assert "90210" not in clean


def test_residue_surfaces_name_with_one_common_word():
    """finding #4: `all`-skip means a real name with one common-word part still surfaces."""
    gw = PseudonymisationGateway()
    # "Court" is a common non-name word; the person "Marcus Court" must still be flagged.
    residue = gw.detect_residue("Please add Marcus Court to the witness list.")
    assert "Marcus Court" in residue
    # but a pure place/institution stays suppressed
    assert "Supreme Court" not in gw.detect_residue("Argued before the Supreme Court today.")
