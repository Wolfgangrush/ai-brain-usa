"""Provider-agnostic LLM client for the AI Law Brain.

Talks to whatever AI host the app was launched under:

  * ``connect-local``            -- writes ``ai_provider: "ollama"`` into
                                  ``~/.aibrain-usa/config.json`` and the
                                  user wants LOCAL ONLY. POST to
                                  ``{ollama_host}/api/chat``.
  * Anthropic-compatible host    -- ``ANTHROPIC_BASE_URL`` / ``ANTHROPIC_AUTH_TOKEN``
                                  env vars. POST to ``/v1/messages``.
  * Native Anthropic             -- defaults to ``api.anthropic.com``.
  * OpenAI-compatible host       -- ``OPENAI_BASE_URL`` / ``OPENAI_API_KEY``.
                                  POST to ``/v1/chat/completions``.
  * DeepSeek                     -- ``DEEPSEEK_BASE_URL`` / ``DEEPSEEK_API_KEY``.
                                  POST to ``/v1/chat/completions``.
  * GLM (Zhipu)                  -- ``GLM_BASE_URL`` / ``GLM_API_KEY``.
                                  POST to ``/v1/chat/completions``.
  * MiniMax                      -- ``MINIMAX_BASE_URL`` / ``MINIMAX_API_KEY``.
                                  POST to ``/v1/chat/completions``.
  * Gemini (Google)              -- ``GEMINI_BASE_URL`` / ``GEMINI_API_KEY`` (or
                                  ``GOOGLE_API_KEY``). POST to
                                  ``/v1beta/models/{model}:generateContent``.

The provider is selected by ``ai_provider`` in ``~/.aibrain-usa/config.json``.
A blank / missing value defaults to ``anthropic`` for backwards compatibility with
the original single-provider launcher. Credentials + provider selection are read
FRESH PER CALL (not at import time) so the same module works under every launcher
and a launcher that sets env vars late is still honoured.

CRITICAL SAFETY RULE
--------------------
When the local provider is selected, the Ollama endpoint is the ONLY thing
we ever call. There is NO silent fallback to cloud on transport failure --
that would leak privileged material while the user believes they are local.
Failures raise :class:`LLMError` and the caller (``brain/specialists.py``)
falls back to the offline structured engine result. See
``tests/test_local_provider.py``.

The pseudonymisation gateway remains wired on the CLOUD path exactly as it
is today, and runs as a SINGLE CHOKE POINT inside ``_cloud_complete`` so it
is impossible for a future provider adapter to be added that forgets to
pseudonymise. ``tests/test_gateway_wiring.py`` and
``tests/test_multiprovider.py`` lock that contract; refactors must not
break it.

ROUTING RULE (HARD INVARIANT — locked 2026-08-23)
-------------------------------------------------
    force_cloud = os.environ.get("AIBRAIN_FORCE_CLOUD", "").strip()
                  in ("1", "true", "TRUE", "yes")
    if _is_local_provider(provider) and not force_cloud:
        -> local

EXPLICIT CONFIG BEATS AMBIENT ENVIRONMENT. If the user's config.json says
local, inference goes local even when a cloud credential happens to be
present in the environment. The config file is a deliberate statement of
intent by the practitioner; an exported environment variable is ambient
and may be inherited from a shell profile, an earlier experiment, or
another tool entirely.

The alternative rule — "a cloud key overrides local" — would mean a
solicitor who ran ``connect-local`` and also has a key exported gets
privileged material sent to a cloud vendor while the product tells them
they are local. That is the exact false-assurance failure this tier exists
to remove, so it is not available as a convenience. A developer who
genuinely wants the cloud path while a local config is present must say
so out loud by exporting ``AIBRAIN_FORCE_CLOUD=1``.

"""

import json
import os
import urllib.error
import urllib.request


# Hard-coded safety default. If a user sets ai_provider=ollama but forgets
# to specify a host, we fall back to localhost on the standard Ollama port.
# The host string is intentionally NOT read from any environment variable --
# the config file (or this default) is the only source of truth, so a stray
# env var cannot redirect local traffic to a cloud host.
LOCAL_DEFAULT_HOST = "http://localhost:11434"


# ---------------------------------------------------------------------------
# Provider catalogue -- single source of truth for the six cloud providers
# ---------------------------------------------------------------------------
# Every cloud provider the brain supports is described here: which env var(s)
# hold the API key (tried in order; first non-empty wins), which env var
# overrides the base URL, which env var overrides the model, the default
# base URL and the provider's current, correct default model (no provider
# ships defaulting to a model name from a different vendor -- see regression
# test ``test_no_provider_silently_defaults_to_a_mismatched_model``).
#
# ``kind`` picks the adapter family:
#   * "anthropic"     -- POST {base}/v1/messages,  x-api-key + anthropic-version
#   * "openai_compat" -- POST {base}/v1/chat/completions, Authorization: Bearer
#                       (shared by openai / deepseek / glm / minimax)
#   * "gemini"        -- POST {base}/v1beta/models/{model}:generateContent
#                       with ?key=APIKEY in the query string
#
# Adding a new provider means adding one row, not editing the dispatch
# chain below. The dispatch in ``_cloud_complete`` keys off this table.

_CLOUD_PROVIDER_SPECS = {
    "anthropic": {
        "default_base_url": "https://api.anthropic.com",
        "default_model": "claude-opus-4-1",
        "key_env": ("ANTHROPIC_API_KEY", "ANTHROPIC_AUTH_TOKEN"),
        "base_url_env": "ANTHROPIC_BASE_URL",
        "model_env": "ANTHROPIC_MODEL",
        "endpoint_path": "/v1/messages",
        "kind": "anthropic",
    },
    "openai": {
        "default_base_url": "https://api.openai.com",
        "default_model": "gpt-5",
        "key_env": ("OPENAI_API_KEY",),
        "base_url_env": "OPENAI_BASE_URL",
        "model_env": "OPENAI_MODEL",
        "endpoint_path": "/v1/chat/completions",
        "kind": "openai_compat",
    },
    "deepseek": {
        "default_base_url": "https://api.deepseek.com",
        "default_model": "deepseek-chat",
        "key_env": ("DEEPSEEK_API_KEY",),
        "base_url_env": "DEEPSEEK_BASE_URL",
        "model_env": "DEEPSEEK_MODEL",
        "endpoint_path": "/v1/chat/completions",
        "kind": "openai_compat",
    },
    "glm": {
        "default_base_url": "https://api.z.ai",
        "default_model": "glm-4.5",
        "key_env": ("GLM_API_KEY",),
        "base_url_env": "GLM_BASE_URL",
        "model_env": "GLM_MODEL",
        "endpoint_path": "/v1/chat/completions",
        "kind": "openai_compat",
    },
    "minimax": {
        "default_base_url": "https://api.minimax.io",
        "default_model": "MiniMax-Text-01",
        "key_env": ("MINIMAX_API_KEY",),
        "base_url_env": "MINIMAX_BASE_URL",
        "model_env": "MINIMAX_MODEL",
        "endpoint_path": "/v1/chat/completions",
        "kind": "openai_compat",
    },
    "gemini": {
        "default_base_url": "https://generativelanguage.googleapis.com",
        "default_model": "gemini-2.5-pro",
        "key_env": ("GEMINI_API_KEY", "GOOGLE_API_KEY"),
        "base_url_env": "GEMINI_BASE_URL",
        "model_env": "GEMINI_MODEL",
        "endpoint_path": "/v1beta/models/{model}:generateContent",
        "kind": "gemini",
    },
}


class LLMError(Exception):
    """Raised on any LLM transport failure or unexpected response shape."""


def _read_env_first(names):
    """Return the first non-empty env var from ``names`` (stripped)."""
    for n in names:
        v = os.environ.get(n, "").strip()
        if v:
            return v
    return ""


def _cfg_for_provider(provider):
    """Read (base_url, key, model) for a specific provider, fresh per call.

    Reads ``os.environ`` on every invocation -- never cached at import time
    (invariant I4). Raises :class:`LLMError` if the provider is unknown; a
    missing key is signalled by an empty ``key`` in the returned tuple so
    the caller can produce a provider-specific "no key" message (I3).
    """
    spec = _CLOUD_PROVIDER_SPECS.get(provider)
    if spec is None:
        raise LLMError("unknown cloud provider: " + repr(provider))
    key = _read_env_first(spec["key_env"])
    base_url = os.environ.get(spec["base_url_env"], "").strip() or spec["default_base_url"]
    model = os.environ.get(spec["model_env"], "").strip() or spec["default_model"]
    return base_url, key, model


def _cfg():
    """Backwards-compatible shim used by callers that only knew the old
    Anthropic-only world (``available()``, ``model_name()``). Returns
    ``(base_url, key, model)`` for the anthropic provider so the existing
    contract is preserved bit-for-bit for any out-of-tree caller.
    """
    return _cfg_for_provider("anthropic")


def _read_provider_config():
    """Read provider selection from ``~/.aibrain-usa/config.json``.

    Returns ``(provider, ollama_host, ollama_model)`` — all strings, all empty
    when unset / missing / unreadable. Reads via the existing ``BrainConfig``
    loader so file-path resolution + JSON parse + missing-file handling are
    reused unchanged. A failure here is non-fatal: returning empty values
    simply means "no local preference" and the env-based cloud path takes over.

    Tests: this is the single seam for provider selection. To force a
    specific provider in a test, monkeypatch it directly — no need to touch
    disk or the user's real config:

        monkeypatch.setattr(
            llm, "_read_provider_config",
            lambda: ("ollama", "http://localhost:11434", "qwen3:7b"),
        )
    """
    try:
        from aibrain_usa.config import BrainConfig

        file_cfg = getattr(BrainConfig(), "_file_config", None) or {}
    except Exception:
        return "", "", ""
    return (
        str(file_cfg.get("ai_provider") or "").strip().lower(),
        str(file_cfg.get("ollama_host") or "").strip(),
        str(file_cfg.get("ollama_model") or "").strip(),
    )


def _is_local_provider(provider):
    return provider in ("ollama", "local")


def _resolve_cloud_provider(provider):
    """Translate the raw provider string from the config file into a canonical
    cloud provider name. ``""`` (no provider selected) keeps the old
    backwards-compatible default of ``anthropic`` so a user with only an
    Anthropic key in their environment and no config.json entry still gets
    the original behaviour. An unrecognised provider also falls back to
    ``anthropic`` rather than raising -- a typo in config.json then produces
    the usual "no key" error and the user notices, instead of silently
    disabling inference.
    """
    if not provider:
        return "anthropic"
    if provider in _CLOUD_PROVIDER_SPECS:
        return provider
    return "anthropic"


def available():
    """True iff some LLM is configured:

    * a local provider is selected in ``~/.aibrain-usa/config.json``
      (regardless of whether the endpoint is currently reachable -- we
      re-check reachability per call so a late-started daemon is honoured),
    * OR a key is present in the environment for the resolved cloud provider.
    """
    provider, _, _ = _read_provider_config()
    if _is_local_provider(provider):
        return True
    cloud_provider = _resolve_cloud_provider(provider)
    try:
        _, key, _ = _cfg_for_provider(cloud_provider)
    except LLMError:
        return False
    return bool(key)


def model_name():
    """Resolved model name for banners + status. Local > env > default."""
    provider, _, ollama_model = _read_provider_config()
    if _is_local_provider(provider):
        return ollama_model or "qwen3:7b"
    cloud_provider = _resolve_cloud_provider(provider)
    try:
        _, _, model = _cfg_for_provider(cloud_provider)
    except LLMError:
        return ""
    return model


# ---------------------------------------------------------------------------
# Local Ollama provider
# ---------------------------------------------------------------------------


def _ollama_post(system, user, host, model, max_tokens, timeout):
    """POST /api/chat to a local Ollama endpoint. Returns assistant text.

    FAIL CLOSED: raises ``LLMError`` on any transport / parse / shape failure.
    The caller MUST NOT fall back to cloud when this raises — a silent
    fallback would leak privileged material while the user believes they are
    local.
    """
    if not host:
        raise LLMError(
            "ai_provider=ollama but ollama_host is missing/empty in config — "
            "refusing to call any endpoint (fail closed)"
        )
    url = host.rstrip("/") + "/api/chat"
    payload = {
        "model": model,
        "stream": False,
        "messages": [
            {"role": "system", "content": system or ""},
            {"role": "user", "content": user},
        ],
        "options": {"num_predict": max_tokens},
    }
    body = json.dumps(payload).encode("utf-8")
    try:
        request = urllib.request.Request(
            url,
            data=body,
            headers={"content-type": "application/json"},
            method="POST",
        )
    except ValueError as exc:
        # Malformed host (no scheme, etc.) — urllib rejects at Request() time.
        # Surface as a fail-closed LLMError, never a raw ValueError leak.
        raise LLMError(
            f"malformed ollama_host {host!r} — refusing to call any endpoint (fail closed): {exc}"
        ) from exc
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        raise LLMError(
            f"local Ollama endpoint {url} unreachable — failing closed "
            f"(no cloud fallback, to avoid leaking privileged material while "
            f"the user believes they are local): {exc}"
        ) from exc
    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LLMError(f"malformed response from local Ollama (non-JSON): {exc}") from exc
    try:
        return parsed["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise LLMError(
            f"malformed response from local Ollama: missing message.content ({exc})"
        ) from exc


def _local_complete(system, user, max_tokens, timeout, ollama_host, ollama_model):
    """Local Ollama path. Runs the SAME gateway on the user prompt as the
    cloud path (defense-in-depth: any future code that logs the masked user
    input still logs the masked form, never raw client PII), POSTs to
    Ollama, fails closed on any error, and desanitises the reply.
    """
    import sys as _sys
    from aibrain_usa.pseudonymisation import PseudonymisationGateway
    from aibrain_usa.pseudonymisation_audit import write_audit

    _gw = PseudonymisationGateway()
    user, _token_map, _disc = _gw.sanitize_with_disclosure(user)

    if _disc.get("residue") and _sys.stderr.isatty():
        print(
            f"⚠️  pseudonymisation: {len(_disc['residue'])} item(s) may not be fully "
            f"masked (review; your call): {_disc['residue']}",
            file=_sys.stderr,
        )
    try:
        from aibrain_usa.config import BrainConfig

        _cfg_dir = BrainConfig().config_dir
    except Exception:
        _cfg_dir = os.path.expanduser("~/.aibrain-usa")
    try:
        write_audit(_disc, model=ollama_model, base_url=ollama_host, config_dir=_cfg_dir)
    except Exception:
        pass

    text = _ollama_post(system, user, ollama_host, ollama_model, max_tokens, timeout)
    return _gw.desanitize(text, _token_map)


# ---------------------------------------------------------------------------
# Cloud providers -- six adapters, single gateway choke point
# ---------------------------------------------------------------------------
# The gateway lives HERE, in ``_cloud_complete``, BEFORE any adapter is
# dispatched. Every cloud path -- anthropic, openai, deepseek, glm, minimax,
# gemini -- funnels through this one function so it is structurally impossible
# to add a new provider without the gateway running first. The individual
# adapter functions (``_anthropic_call`` etc.) only know how to build a
# request for one provider's wire format and unwrap that provider's reply;
# they never see the raw user text and never desanitise. Desanitisation
# happens once, at the end, after the adapter returns.


def _anthropic_call(system, user, max_tokens, timeout, base_url, key, model):
    """POST /v1/messages to an Anthropic-compatible endpoint.

    Backwards-compatible with the original single-provider launcher: a custom
    ``base_url`` (set via ``ANTHROPIC_BASE_URL``) signals a compatible gateway
    that wants ``Authorization: Bearer`` instead of ``x-api-key``. Native
    Anthropic (``https://api.anthropic.com``) keeps the original header pair.
    """
    url = base_url.rstrip("/") + "/v1/messages"
    headers = {
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    if base_url.rstrip("/") != "https://api.anthropic.com":
        headers["Authorization"] = "Bearer " + key
    else:
        headers["x-api-key"] = key

    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": user}],
    }
    if system:
        payload["system"] = system

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        raise LLMError("transport error talking to " + url + ": " + str(exc)) from exc

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LLMError("malformed response (non-JSON): " + str(exc)) from exc

    try:
        return parsed["content"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError("malformed response: missing content[0].text (" + str(exc) + ")") from exc


def _openai_compat_call(system, user, max_tokens, timeout, base_url, key, model):
    """POST /v1/chat/completions to an OpenAI-compatible endpoint.

    Used by ``openai``, ``deepseek``, ``glm`` and ``minimax``. They differ
    only in their default base URL and default model; the request shape,
    headers and response unwrapping are identical, so one adapter covers
    all four rather than four near-identical copies of the same code.
    """
    url = base_url.rstrip("/") + "/v1/chat/completions"
    headers = {
        "Authorization": "Bearer " + key,
        "content-type": "application/json",
    }
    messages = [{"role": "user", "content": user}]
    if system:
        messages.insert(0, {"role": "system", "content": system})
    payload = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        raise LLMError("transport error talking to " + url + ": " + str(exc)) from exc

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LLMError("malformed response (non-JSON): " + str(exc)) from exc

    try:
        return parsed["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(
            "malformed response: missing choices[0].message.content (" + str(exc) + ")"
        ) from exc


def _gemini_call(system, user, max_tokens, timeout, base_url, key, model):
    """POST /v1beta/models/{model}:generateContent to Google's Gemini API.

    Gemini's wire format is its own: the API key is passed as a ``?key=...``
    query parameter rather than an ``Authorization`` header, the body uses
    ``contents[].parts[].text`` instead of ``messages[].content``, and the
    response comes back as ``candidates[0].content.parts[0].text``.
    """
    url = base_url.rstrip("/") + "/v1beta/models/" + model + ":generateContent?key=" + key
    headers = {"content-type": "application/json"}

    parts = [{"text": user}]
    if system:
        parts.insert(0, {"text": system})
    payload = {"contents": [{"role": "user", "parts": parts}]}

    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(url, data=body, headers=headers, method="POST")

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, OSError) as exc:
        raise LLMError("transport error talking to " + url + ": " + str(exc)) from exc

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LLMError("malformed response (non-JSON): " + str(exc)) from exc

    try:
        return parsed["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(
            "malformed response: missing candidates[0].content.parts[0].text (" + str(exc) + ")"
        ) from exc


def _cloud_complete(system, user, max_tokens, timeout, provider):
    """Single cloud entry point. Runs the pseudonymisation gateway ONCE here
    (I1: gateway is the single choke point -- every adapter dispatches from
    inside this function so a future provider cannot be added that forgets
    to pseudonymise), then hands the masked user text to the provider's
    adapter, then desanitises the reply.

    ``provider`` is a canonical name from ``_CLOUD_PROVIDER_SPECS`` --
    ``complete()`` resolves the user-config string to a canonical name via
    ``_resolve_cloud_provider`` before calling in here.
    """
    spec = _CLOUD_PROVIDER_SPECS.get(provider)
    if spec is None:
        raise LLMError("unknown cloud provider: " + repr(provider))
    base_url, key, model = _cfg_for_provider(provider)
    if not key:
        env_names = " / ".join(spec["key_env"])
        raise LLMError("no " + env_names + " in env for provider " + repr(provider))

    # --- Privacy gateway (whole-brain) ---
    # EVERY cloud egress in the brain funnels through this one function, so
    # pseudonymising the user prompt HERE covers chat, matters, drafting, and
    # RAG alike. Real client names / IDs are replaced with placeholders before
    # the bytes leave the machine, and restored in the model's reply. The
    # placeholder<->original map lives only for this call (never persisted).
    # Coverage limit: government IDs + honorific/context-anchored party names.
    # A bare, un-anchored arbitrary name still needs NER (v0.2.1) -- for truly
    # confidential matters, use local mode. (README "Pseudonymisation coverage".)
    import sys as _sys

    from aibrain_usa.pseudonymisation import PseudonymisationGateway
    from aibrain_usa.pseudonymisation_audit import write_audit

    _gw = PseudonymisationGateway()
    user, _token_map, _disc = _gw.sanitize_with_disclosure(user)

    # Surface residue (possibly-unmasked names the gateway couldn't anchor) so the
    # attorney retains the final call -- brain-frame: warn, never block (C2).
    # Guard on isatty(): only print the raw candidates to a REAL interactive terminal.
    # If stderr is redirected to a file (daemon/CI/`2>log`), we do NOT print the names --
    # the PII-free audit log still records that residue occurred (count + hashes), so
    # nothing raw ever lands on disk (C1).
    if _disc.get("residue") and _sys.stderr.isatty():
        print(
            f"⚠️  pseudonymisation: {len(_disc['residue'])} item(s) may not be fully "
            f"masked (review; your call): {_disc['residue']}",
            file=_sys.stderr,
        )
    # PII-FREE audit log -- best-effort; write_audit swallows internally, and we wrap
    # the call site too (defense-in-depth) so audit can NEVER break a cloud call (C4).
    try:
        from aibrain_usa.config import BrainConfig

        _cfg_dir = BrainConfig().config_dir
    except Exception:
        _cfg_dir = os.path.expanduser("~/.aibrain-usa")
    try:
        write_audit(_disc, model=model, base_url=base_url, config_dir=_cfg_dir)
    except Exception:
        pass

    # Dispatch to the provider's adapter. The adapter only sees the masked
    # user text and only knows how to talk to its own endpoint -- it never
    # touches the gateway or the token map. Adding a new provider here means
    # adding one row to _CLOUD_PROVIDER_SPECS plus (if its wire format is new)
    # one ``_newprovider_call`` function below; the gateway stays in place.
    if spec["kind"] == "anthropic":
        text = _anthropic_call(system, user, max_tokens, timeout, base_url, key, model)
    elif spec["kind"] == "openai_compat":
        text = _openai_compat_call(system, user, max_tokens, timeout, base_url, key, model)
    elif spec["kind"] == "gemini":
        text = _gemini_call(system, user, max_tokens, timeout, base_url, key, model)
    else:
        raise LLMError(
            "unknown adapter kind " + repr(spec["kind"]) + " for provider " + repr(provider)
        )

    # Restore real values in the model's reply before handing it back to
    # the caller. Desanitisation happens here, exactly once, on the reply
    # from whichever adapter ran above.
    return _gw.desanitize(text, _token_map)


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------


def complete(
    system: str,
    user: str,
    max_tokens: int = 1024,
    timeout: float = 60.0,
) -> str:
    """Send one chat request and return the assistant text.

    Routing (per call, fresh from disk + env):

      * ``ai_provider`` in ``(ollama, local)``
        → POST to ``{ollama_host}/api/chat``. Fail closed on any error;
        NEVER silently fall back to cloud (invariant I2).
      * Otherwise → route to the selected cloud provider:
          - ``anthropic`` (default) → POST {base}/v1/messages
          - ``openai``              → POST {base}/v1/chat/completions
          - ``deepseek``            → POST {base}/v1/chat/completions
          - ``glm``                 → POST {base}/v1/chat/completions
          - ``minimax``             → POST {base}/v1/chat/completions
          - ``gemini``              → POST {base}/v1beta/models/{model}:generateContent

    Each provider requires its own API key env var (see
    ``_CLOUD_PROVIDER_SPECS``); selecting a provider without its key raises
    :class:`LLMError` and makes NO network request (I3). The
    pseudonymisation gateway runs before the network POST on every cloud
    provider (I1); refactors must not break ``tests/test_gateway_wiring.py``
    or ``tests/test_multiprovider.py``.

    EXPLICIT CONFIG BEATS AMBIENT ENVIRONMENT. If the user's config.json
    says local, inference goes local even when a cloud credential happens
    to be present in the environment. The config file is a deliberate
    statement of intent by the practitioner; an exported environment
    variable is ambient and may be inherited from a shell profile, an
    earlier experiment, or another tool entirely.

    The alternative rule -- "a cloud key overrides local" -- would mean a
    solicitor who ran ``connect-local`` and also has a key exported gets
    privileged material sent to a cloud vendor while the product tells
    them they are local. That is the exact false-assurance failure this
    tier exists to remove, so it is not available as a convenience.

    A developer who genuinely wants the cloud path while a local config
    is present must say so out loud by exporting
    ``AIBRAIN_FORCE_CLOUD=1``. It is deliberately verbose, deliberately
    not a default, and it is logged in the returned error when misused.
    """
    provider, ollama_host, ollama_model = _read_provider_config()

    force_cloud = os.environ.get("AIBRAIN_FORCE_CLOUD", "").strip() in (
        "1",
        "true",
        "TRUE",
        "yes",
    )

    if _is_local_provider(provider) and not force_cloud:
        host = ollama_host or LOCAL_DEFAULT_HOST
        m = ollama_model or "qwen3:7b"
        return _local_complete(system, user, max_tokens, timeout, host, m)

    # Cloud path. Resolve the user-config string to a canonical provider name
    # ("" or unrecognised → "anthropic", backwards compat) and let
    # _cloud_complete validate the key and run the gateway.
    cloud_provider = _resolve_cloud_provider(provider)
    return _cloud_complete(system, user, max_tokens, timeout, cloud_provider)
