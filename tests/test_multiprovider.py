"""Contract for the six-provider cloud layer (2026-08-25).

Authored by Opus as the firewall spec; the implementation in brain/llm.py must
satisfy every assertion here without weakening test_gateway_wiring.py or
test_local_provider.py.

PROVIDERS
---------
  local     ollama     POST {ollama_host}/api/chat                  (no key)
  cloud     anthropic  POST {base}/v1/messages                      ANTHROPIC_API_KEY
  cloud     openai     POST {base}/v1/chat/completions              OPENAI_API_KEY
  cloud     deepseek   POST {base}/v1/chat/completions              DEEPSEEK_API_KEY
  cloud     glm        POST {base}/v1/chat/completions              GLM_API_KEY
  cloud     minimax    POST {base}/v1/chat/completions              MINIMAX_API_KEY
  cloud     gemini     POST {base}/v1beta/models/{model}:generateContent   GEMINI_API_KEY

INVARIANTS THAT MAY NOT BE BROKEN
---------------------------------
  I1  The pseudonymisation gateway runs BEFORE the network POST on EVERY cloud
      provider. Not one of the five may bypass it. This is the property the
      published website rests on.
  I2  When a local provider is selected there is NO cloud fallback on any error.
  I3  A cloud provider selected with no key raises LLMError and makes NO request.
  I4  Credentials and provider selection are read fresh per call, never at import.
  I5  No test here makes a real network call.
"""

import json

import pytest

from aibrain_usa.brain import llm


CLOUD_PROVIDERS = ["anthropic", "openai", "deepseek", "glm", "minimax", "gemini"]

KEY_ENV = {
    "anthropic": "ANTHROPIC_API_KEY",
    "openai": "OPENAI_API_KEY",
    "deepseek": "DEEPSEEK_API_KEY",
    "glm": "GLM_API_KEY",
    "minimax": "MINIMAX_API_KEY",
    "gemini": "GEMINI_API_KEY",
}


class _FakeResp:
    def __init__(self, body):
        self._b = body.encode() if isinstance(body, str) else body

    def read(self):
        return self._b

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _reply_body(provider):
    """Minimal well-formed success body in each provider's own response shape."""
    if provider == "anthropic":
        return json.dumps({"content": [{"type": "text", "text": "ok"}]})
    if provider == "gemini":
        return json.dumps({"candidates": [{"content": {"parts": [{"text": "ok"}]}}]})
    return json.dumps({"choices": [{"message": {"content": "ok"}}]})


def _select(monkeypatch, provider):
    """Force provider selection through the single documented seam."""
    monkeypatch.setattr(llm, "_read_provider_config", lambda: (provider, "", ""), raising=False)


def _clear_keys(monkeypatch):
    for var in set(KEY_ENV.values()) | {"ANTHROPIC_AUTH_TOKEN", "GOOGLE_API_KEY"}:
        monkeypatch.delenv(var, raising=False)


# ---------------------------------------------------------------- I3: no key
@pytest.mark.parametrize("provider", CLOUD_PROVIDERS)
def test_missing_key_raises_and_makes_no_request(monkeypatch, provider):
    _clear_keys(monkeypatch)
    _select(monkeypatch, provider)

    called = []
    monkeypatch.setattr(llm.urllib.request, "urlopen", lambda *a, **k: called.append(1))

    with pytest.raises(llm.LLMError):
        llm.complete("sys", "user text", max_tokens=16, timeout=5)

    assert called == [], f"{provider}: a request was made despite having no key"


# ------------------------------------------------- I1: gateway on every cloud
@pytest.mark.parametrize("provider", CLOUD_PROVIDERS)
def test_gateway_runs_before_post_on_every_cloud_provider(monkeypatch, provider):
    _clear_keys(monkeypatch)
    monkeypatch.setenv(KEY_ENV[provider], "test-key-123")
    _select(monkeypatch, provider)

    sent = {}

    def _fake_urlopen(req, timeout=None):
        body = req.data.decode() if req.data else ""
        sent["url"] = req.full_url
        sent["body"] = body
        sent["headers"] = {k.lower(): v for k, v in req.headers.items()}
        return _FakeResp(_reply_body(provider))

    monkeypatch.setattr(llm.urllib.request, "urlopen", _fake_urlopen)

    secret = "my client Maria Gonzalez v. Rite Aid"
    llm.complete("sys", f"Prepare a note for {secret}", max_tokens=16, timeout=5)

    assert sent, f"{provider}: no request captured"
    assert "Maria Gonzalez" not in sent["body"], (
        f"{provider}: REAL CLIENT NAME REACHED THE WIRE — gateway bypassed"
    )
    assert "Rite Aid" not in sent["body"], (
        f"{provider}: REAL COUNTERPARTY REACHED THE WIRE — gateway bypassed"
    )


# ------------------------------------------------------- endpoint correctness
@pytest.mark.parametrize(
    "provider,fragment",
    [
        ("anthropic", "/v1/messages"),
        ("openai", "/v1/chat/completions"),
        ("deepseek", "/v1/chat/completions"),
        ("glm", "/v1/chat/completions"),
        ("minimax", "/v1/chat/completions"),
        ("gemini", ":generateContent"),
    ],
)
def test_provider_posts_to_its_own_endpoint(monkeypatch, provider, fragment):
    _clear_keys(monkeypatch)
    monkeypatch.setenv(KEY_ENV[provider], "test-key-123")
    _select(monkeypatch, provider)

    sent = {}

    def _fake_urlopen(req, timeout=None):
        sent["url"] = req.full_url
        return _FakeResp(_reply_body(provider))

    monkeypatch.setattr(llm.urllib.request, "urlopen", _fake_urlopen)
    llm.complete("sys", "hello", max_tokens=16, timeout=5)

    assert fragment in sent["url"], f"{provider}: posted to {sent['url']}"


# --------------------------------------------------------- response unwrapping
@pytest.mark.parametrize("provider", CLOUD_PROVIDERS)
def test_each_provider_response_shape_is_unwrapped(monkeypatch, provider):
    _clear_keys(monkeypatch)
    monkeypatch.setenv(KEY_ENV[provider], "test-key-123")
    _select(monkeypatch, provider)
    monkeypatch.setattr(
        llm.urllib.request,
        "urlopen",
        lambda req, timeout=None: _FakeResp(_reply_body(provider)),
    )

    out = llm.complete("sys", "hello", max_tokens=16, timeout=5)
    assert "ok" in out, f"{provider}: could not unwrap its own response shape"


# ------------------------------------------------------ I4: fresh credentials
def test_credentials_are_read_fresh_per_call(monkeypatch):
    _clear_keys(monkeypatch)
    _select(monkeypatch, "openai")
    monkeypatch.setattr(
        llm.urllib.request,
        "urlopen",
        lambda req, timeout=None: _FakeResp(_reply_body("openai")),
    )

    with pytest.raises(llm.LLMError):
        llm.complete("sys", "hello", max_tokens=16, timeout=5)

    monkeypatch.setenv("OPENAI_API_KEY", "late-key")
    assert "ok" in llm.complete("sys", "hello", max_tokens=16, timeout=5)


# ------------------------------------- no provider defaults to a foreign model
def test_no_provider_silently_defaults_to_a_mismatched_model(monkeypatch):
    """Regression: the whole family shipped defaulting to 'glm-5.2' while
    documenting itself as Anthropic-compatible, so an Anthropic key with no
    model set produced a guaranteed API error."""
    _clear_keys(monkeypatch)
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    _select(monkeypatch, "anthropic")

    sent = {}
    monkeypatch.setattr(
        llm.urllib.request,
        "urlopen",
        lambda req, timeout=None: (
            sent.update(body=json.loads(req.data.decode())),
            _FakeResp(_reply_body("anthropic")),
        )[1],
    )
    llm.complete("sys", "hello", max_tokens=16, timeout=5)

    model = sent["body"].get("model", "")
    assert "glm" not in model.lower(), f"anthropic provider sent model={model!r}"
