"""Tests for the local Ollama provider wired in brain/llm.complete().

Locks the four safety properties the new provider branch must hold:

  1. ai_provider=ollama in config -> request POSTs to {ollama_host}/api/chat
     (NOT to any cloud host).
  2. Endpoint unreachable -> raises LLMError; NO cloud fallback is attempted.
     A silent cloud fallback would leak privileged material while the user
     believes they are local — this is the single most important property.
  3. Unset config / explicit cloud credential -> existing cloud behaviour
     unchanged; pseudonymisation gateway still wired exactly as today.
  4. Malformed or missing ollama_host -> fails closed with a clear message;
     no HTTP request is made.

All HTTP is mocked; no test in this file makes a real network call.
"""

import json
import urllib.error

import pytest

from aibrain_usa.brain import llm


class _FakeResp:
    """Minimal urllib response double used across this suite."""

    def __init__(self, body):
        self._b = body.encode() if isinstance(body, str) else body

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _patch_provider(monkeypatch, *, provider="", host="", model=""):
    """Force a specific provider config + clear cloud env so the cloud path
    can't accidentally take over from underneath the test."""
    monkeypatch.setattr(llm, "_read_provider_config", lambda: (provider, host, model))
    monkeypatch.delenv("ANTHROPIC_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("ANTHROPIC_BASE_URL", raising=False)
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)


def _ollama_reply(content="ok"):
    """Build the JSON shape Ollama's /api/chat returns."""
    return json.dumps({"message": {"role": "assistant", "content": content}})


# ─────────────────────────────────────────────────────────────────────────
# Property 1: local routes to ollama, not to any cloud host
# ─────────────────────────────────────────────────────────────────────────


def test_local_provider_posts_to_ollama_host(monkeypatch):
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["url"] = req.full_url
        captured["body"] = req.data.decode("utf-8")
        captured["headers"] = dict(req.headers)
        return _FakeResp(_ollama_reply("Hello."))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    out = llm.complete("sys", "hi")
    assert captured["url"] == "http://localhost:11434/api/chat"
    assert "anthropic" not in captured["url"]
    assert "api.anthropic.com" not in captured["url"]
    assert "z.ai" not in captured["url"] and "minimax" not in captured["url"]
    payload = json.loads(captured["body"])
    assert payload["model"] == "qwen3:7b"
    assert payload["stream"] is False
    assert payload["messages"][-1]["role"] == "user"
    assert payload["messages"][-1]["content"] == "hi"
    assert out == "Hello."


def test_local_provider_accepts_alias_local(monkeypatch):
    """`ai_provider: local` is also accepted (alias for ollama)."""
    _patch_provider(monkeypatch, provider="local", host="http://localhost:11434", model="qwen3:7b")
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["url"] = req.full_url
        return _FakeResp(_ollama_reply())

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    llm.complete("sys", "hi")
    assert captured["url"] == "http://localhost:11434/api/chat"


def test_local_provider_uses_default_host_when_unset(monkeypatch):
    """If ollama_host is missing in config, fall back to http://localhost:11434."""
    _patch_provider(monkeypatch, provider="ollama", host="", model="qwen3:7b")
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["url"] = req.full_url
        return _FakeResp(_ollama_reply())

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    llm.complete("sys", "hi")
    assert captured["url"] == "http://localhost:11434/api/chat"


def test_local_provider_respects_custom_host_and_model(monkeypatch):
    """A non-default host (chamber desktop, friend's laptop) is honoured."""
    _patch_provider(
        monkeypatch,
        provider="ollama",
        host="http://chamber-pc.local:11434",
        model="llama3.3:8b",
    )
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["url"] = req.full_url
        captured["body"] = req.data.decode("utf-8")
        return _FakeResp(_ollama_reply())

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    llm.complete("sys", "hi")
    assert captured["url"] == "http://chamber-pc.local:11434/api/chat"
    assert json.loads(captured["body"])["model"] == "llama3.3:8b"


def test_local_provider_passes_system_prompt_separately(monkeypatch):
    """Ollama's /api/chat wants system + user as separate message objects."""
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["body"] = req.data.decode("utf-8")
        return _FakeResp(_ollama_reply())

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    llm.complete("you are a specialist", "user question")
    payload = json.loads(captured["body"])
    roles = [m["role"] for m in payload["messages"]]
    assert roles == ["system", "user"]
    assert payload["messages"][0]["content"] == "you are a specialist"


def test_local_provider_no_anthropic_auth_header(monkeypatch):
    """Local traffic must not carry an Authorization header — there's no key."""
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["headers"] = dict(req.headers)
        return _FakeResp(_ollama_reply())

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    llm.complete("sys", "hi")
    assert "authorization" not in {k.lower() for k in captured["headers"]}
    assert "x-api-key" not in {k.lower() for k in captured["headers"]}


# ─────────────────────────────────────────────────────────────────────────
# Property 2: fail closed, no cloud fallback
# ─────────────────────────────────────────────────────────────────────────


def test_local_endpoint_unreachable_fails_closed(monkeypatch):
    """If Ollama is down, raise LLMError; do NOT silently call cloud."""
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")
    cloud_called = []

    def fake_urlopen(req, *a, **k):
        if "anthropic" in req.full_url or "api.anthropic.com" in req.full_url:
            cloud_called.append(req.full_url)
        raise urllib.error.URLError("Connection refused")

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.LLMError) as exc_info:
        llm.complete("sys", "hi")
    msg = str(exc_info.value).lower()
    assert "unreachable" in msg or "failing closed" in msg
    assert "no cloud fallback" in str(exc_info.value).lower()
    assert cloud_called == [], f"FAIL-CLOSED VIOLATED: cloud was called: {cloud_called}"


def test_local_timeout_fails_closed(monkeypatch):
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")

    def fake_urlopen(req, *a, **k):
        raise TimeoutError("read timed out")

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.LLMError):
        llm.complete("sys", "hi")


def test_local_connection_refused_fails_closed(monkeypatch):
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")

    def fake_urlopen(req, *a, **k):
        raise ConnectionRefusedError("daemon not running")

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.LLMError):
        llm.complete("sys", "hi")


def test_local_malformed_response_fails_closed(monkeypatch):
    """If Ollama returns garbage JSON, raise LLMError; don't silently fall back."""
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")

    def fake_urlopen(req, *a, **k):
        return _FakeResp("not json at all")

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.LLMError):
        llm.complete("sys", "hi")


def test_local_missing_message_field_fails_closed(monkeypatch):
    """If Ollama returns well-formed JSON but wrong shape, raise LLMError."""
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")

    def fake_urlopen(req, *a, **k):
        return _FakeResp(json.dumps({"unexpected": "shape"}))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.LLMError) as exc_info:
        llm.complete("sys", "hi")
    assert "message.content" in str(exc_info.value)


# ─────────────────────────────────────────────────────────────────────────
# Property 3: cloud unchanged + gateway still wired
# ─────────────────────────────────────────────────────────────────────────


def test_no_provider_no_key_raises_existing_error(monkeypatch):
    """No config provider AND no env key -> the existing 'no key' error."""
    _patch_provider(monkeypatch)
    with pytest.raises(llm.LLMError) as exc_info:
        llm.complete("sys", "hi")
    assert "ANTHROPIC_AUTH_TOKEN" in str(exc_info.value) or "ANTHROPIC_API_KEY" in str(
        exc_info.value
    )


def test_cloud_key_overrides_local_provider(monkeypatch):
    """CORRECTED 2026-08-23 (Maitreyi/Opus). This test formerly asserted that a
    cloud key in the environment overrides an explicit ai_provider=ollama config.
    That routing was a false-privilege-assurance defect: a solicitor who ran
    connect-local, but who also had a key exported, had privileged material sent
    to a cloud vendor while the product reported local mode.

    The original justification was test convenience — keeping gateway-wiring tests
    green on a CI box with a stale ai_provider=ollama. Test convenience is not a
    reason to weaken production egress routing. CI states its intent explicitly
    with AIBRAIN_FORCE_CLOUD=1, which is what this test now does.
    """
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")
    monkeypatch.setenv("AIBRAIN_FORCE_CLOUD", "1")
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "test-cloud-key")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://example.test/anthropic")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["url"] = req.full_url
        return _FakeResp(json.dumps({"content": [{"text": "cloud reply"}]}))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    out = llm.complete("sys", "hi")
    assert captured["url"].startswith("https://example.test/anthropic")
    assert out == "cloud reply"


def test_cloud_path_runs_pseudonymisation_gateway(monkeypatch):
    """The cloud path MUST still run the gateway. This test exists so a
    refactor of the cloud branch can't silently drop the gateway — the
    canonical lock is tests/test_gateway_wiring.py; this is the belt to
    that suspenders, kept local to this file so the new provider's test
    coverage stands on its own."""
    _patch_provider(monkeypatch)  # ensure no local
    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "test-cloud-key")
    monkeypatch.setenv("ANTHROPIC_BASE_URL", "https://example.test/anthropic")
    monkeypatch.setenv("ANTHROPIC_MODEL", "test-model")
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["body"] = req.data.decode("utf-8")
        return _FakeResp(json.dumps({"content": [{"text": "Re [PERSON_1]."}]}))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    out = llm.complete("sys", "Draft for my client Maria Gonzalez.")
    assert "Maria Gonzalez" not in captured["body"]
    assert "[PERSON_1]" in captured["body"]
    assert "Maria Gonzalez" in out


def test_local_path_runs_pseudonymisation_gateway(monkeypatch):
    """The local path also runs the gateway so any future logging of the
    user input logs the masked form (defense-in-depth). Local data never
    leaves the machine, but keeping the gateway wired here keeps the
    whole-brain invariant uniform: every egress sees masked data."""
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")
    captured = {}

    def fake_urlopen(req, *a, **k):
        captured["body"] = req.data.decode("utf-8")
        return _FakeResp(_ollama_reply("Re [PERSON_1]."))

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    out = llm.complete("sys", "Draft for my client Maria Gonzalez.")
    assert "Maria Gonzalez" not in captured["body"]
    assert "Maria Gonzalez" in out


# ─────────────────────────────────────────────────────────────────────────
# Property 4: malformed / missing ollama_host fails closed
# ─────────────────────────────────────────────────────────────────────────


def test_missing_ollama_host_fails_closed_without_http(monkeypatch):
    """Provider=ollama but host is empty AND default is empty -> fail closed
    BEFORE any HTTP call is made."""
    _patch_provider(monkeypatch, provider="ollama", host="", model="qwen3:7b")
    monkeypatch.setattr(llm, "LOCAL_DEFAULT_HOST", "")  # disable the fallback
    http_calls = []

    def fake_urlopen(req, *a, **k):
        http_calls.append(req.full_url)
        return _FakeResp("{}")

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.LLMError) as exc_info:
        llm.complete("sys", "hi")
    msg = str(exc_info.value).lower()
    assert "ollama_host" in msg or "missing" in msg
    assert "fail" in msg or "refusing" in msg
    assert http_calls == [], f"FAIL-CLOSED VIOLATED: HTTP calls made: {http_calls}"


def test_unreachable_host_with_malformed_url_fails_closed(monkeypatch):
    """A syntactically-malformed host (no scheme) will be rejected by urllib
    at the urlopen level; we verify that's caught and re-raised as LLMError,
    not bubbled as a raw urllib exception."""
    _patch_provider(monkeypatch, provider="ollama", host="not-a-url-at-all", model="qwen3:7b")

    def fake_urlopen(req, *a, **k):
        raise urllib.error.URLError("no host given")

    monkeypatch.setattr(llm.urllib.request, "urlopen", fake_urlopen)
    with pytest.raises(llm.LLMError):
        llm.complete("sys", "hi")


# ─────────────────────────────────────────────────────────────────────────
# Helpers: available() + model_name() report the local provider correctly
# ─────────────────────────────────────────────────────────────────────────


def test_available_true_when_local_provider_selected(monkeypatch):
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="qwen3:7b")
    assert llm.available() is True


def test_model_name_reports_local_model(monkeypatch):
    _patch_provider(
        monkeypatch, provider="ollama", host="http://localhost:11434", model="llama3.3:8b"
    )
    assert llm.model_name() == "llama3.3:8b"


def test_model_name_falls_back_to_qwen3_default(monkeypatch):
    _patch_provider(monkeypatch, provider="ollama", host="http://localhost:11434", model="")
    assert llm.model_name() == "qwen3:7b"


# ── Added by Maitreyi (Opus) 2026-08-23 ─────────────────────────────────────
# Regression guard: EXPLICIT CONFIG BEATS AMBIENT ENVIRONMENT.
# The original generated routing was `_is_local_provider(provider) and not key`,
# which sent a user who had configured local — but who also had a cloud key
# exported — silently to the cloud. That is the false-privilege-assurance
# failure this whole tier exists to remove. These tests pin the corrected rule.


def test_local_config_wins_even_when_cloud_key_is_present(monkeypatch):
    """A solicitor who ran connect-local must go local even with a key exported."""
    import aibrain_usa.brain.llm as llm

    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "sk-ant-a-key-that-happens-to-exist")
    monkeypatch.delenv("AIBRAIN_FORCE_CLOUD", raising=False)
    monkeypatch.setattr(
        llm,
        "_read_provider_config",
        lambda: ("ollama", "http://localhost:11434", "qwen3:7b"),
    )

    called = {}

    def _fake_local(system, user, max_tokens, timeout, host, model):
        called["local"] = host
        return "local-answer"

    def _fake_cloud(*a, **k):
        called["cloud"] = True
        raise AssertionError("cloud path taken while config said local")

    monkeypatch.setattr(llm, "_local_complete", _fake_local)
    monkeypatch.setattr(llm, "_cloud_complete", _fake_cloud)

    assert llm.complete("sys", "user") == "local-answer"
    assert called["local"] == "http://localhost:11434"
    assert "cloud" not in called


def test_force_cloud_env_var_is_the_only_way_to_override_local(monkeypatch):
    """Escaping local mode must be an explicit, loudly-named act."""
    import aibrain_usa.brain.llm as llm

    monkeypatch.setenv("ANTHROPIC_AUTH_TOKEN", "sk-ant-key")
    monkeypatch.setenv("AIBRAIN_FORCE_CLOUD", "1")
    monkeypatch.setattr(
        llm,
        "_read_provider_config",
        lambda: ("ollama", "http://localhost:11434", "qwen3:7b"),
    )

    called = {}
    monkeypatch.setattr(
        llm,
        "_local_complete",
        lambda *a, **k: (_ for _ in ()).throw(AssertionError("local taken despite FORCE_CLOUD")),
    )

    def _fake_cloud(*a, **k):
        called["cloud"] = True
        return "cloud-answer"

    monkeypatch.setattr(llm, "_cloud_complete", _fake_cloud)

    assert llm.complete("sys", "user") == "cloud-answer"
    assert called["cloud"] is True
