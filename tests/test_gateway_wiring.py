"""Regression tests for the whole-brain pseudonymisation wiring (2026-07-12).

Locks two things that were broken:
  1. Context-anchored party names ("my client X", "X v. Y", "X, executor") are
     masked even without an honorific.
  2. brain/llm.complete() actually runs the gateway BEFORE the network POST, so a
     real client name never reaches the wire.
"""

import json

from ailawfirm_usa.pseudonymisation import PseudonymisationGateway
from ailawfirm_usa.brain import llm


def test_context_anchored_client_name_is_masked():
    gw = PseudonymisationGateway()
    clean, tmap = gw.sanitize("Draft a demand letter for my client Maria Gonzalez v. Rite Aid.")
    assert "Maria Gonzalez" not in clean
    assert "Rite Aid" not in clean
    assert (
        gw.desanitize(clean, tmap)
        == "Draft a demand letter for my client Maria Gonzalez v. Rite Aid."
    )


def test_role_anchored_name_is_masked():
    gw = PseudonymisationGateway()
    clean, _ = gw.sanitize("NDA with Whitfield Media LLC (Daniel Whitfield, member).")
    assert "Daniel Whitfield" not in clean


class _FakeResp:
    def __init__(self, body):
        self._b = body.encode()

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def test_llm_complete_sanitises_before_wire(monkeypatch):
    """The raw client name must NOT appear in the bytes POSTed to the cloud."""
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://example.test/anthropic")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "test-key")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")
    captured = {}

    def fake_urlopen(request, *a, **k):
        captured["body"] = request.data.decode("utf-8")
        # echo a placeholder-safe reply so desanitize round-trips
        return _FakeResp(json.dumps({"content": [{"text": "Reply re [PERSON_1]."}]}))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    out = llm.complete("system prompt", "Draft for my client Maria Gonzalez a demand letter.")
    assert "Maria Gonzalez" not in captured["body"]  # did NOT reach the wire
    assert "[PERSON_1]" in captured["body"]  # was pseudonymised
    assert "Maria Gonzalez" in out  # restored in the reply to the user
