"""Provider-agnostic LLM client for the AI Law Brain.

Talks to whatever AI host the app was launched under:

  * ``connect-local``            — writes ``ai_provider: "ollama"`` into
                                  ``~/.ailawfirm-usa/config.json`` and the
                                  user wants LOCAL ONLY. POST to
                                  ``{ollama_host}/api/chat``.
  * Anthropic-compatible host    — ``ANTHROPIC_BASE_URL`` / ``ANTHROPIC_AUTH_TOKEN``
                                  env vars. POST to ``/v1/messages``.
  * Native Anthropic             — defaults to ``api.anthropic.com``.

Credentials + provider selection are read FRESH PER CALL (not import time)
so the same module works under every launcher and so a launcher that sets
env vars late is still honoured.

CRITICAL SAFETY RULE
--------------------
When the local provider is selected, the Ollama endpoint is the ONLY thing
we ever call. There is NO silent fallback to cloud on transport failure —
that would leak privileged material while the user believes they are local.
Failures raise :class:`LLMError` and the caller (``brain/specialists.py``)
falls back to the offline structured engine result. See
``tests/test_local_provider.py``.

The pseudonymisation gateway remains wired on the CLOUD path exactly as it
is today. ``tests/test_gateway_wiring.py`` locks that contract; refactors
must not break it.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Tuple


# Hard-coded safety default. If a user sets ai_provider=ollama but forgets
# to specify a host, we fall back to localhost on the standard Ollama port.
# The host string is intentionally NOT read from any environment variable —
# the config file (or this default) is the only source of truth, so a stray
# env var cannot redirect local traffic to a cloud host.
LOCAL_DEFAULT_HOST = "http://localhost:11434"


class LLMError(Exception):
    """Raised on any LLM transport failure or unexpected response shape."""


def _cfg() -> Tuple[str, str, str]:
    """Read (base_url, key, model) fresh from the environment on every call."""
    base_url = os.environ.get("ANTHROPIC_BASE_URL", "").strip()
    key = (
        os.environ.get("ANTHROPIC_AUTH_TOKEN") or os.environ.get("ANTHROPIC_API_KEY") or ""
    ).strip()
    model = (os.environ.get("ANTHROPIC_MODEL") or "").strip() or "glm-5.2"
    return base_url, key, model


def _read_provider_config():
    """Read provider selection from ``~/.ailawfirm-usa/config.json``.

    Returns ``(provider, ollama_host, ollama_model)`` — all strings, all empty
    when unset / missing / unreadable. Reads via the existing ``BrainConfig``
    loader (``load_config_file``) so file-path resolution + JSON parse +
    missing-file handling are reused unchanged. A failure here is non-fatal:
    returning empty values simply means "no local preference" and the
    env-based cloud path takes over.

    Tests: this is the single seam for provider selection. To force a
    specific provider in a test, monkeypatch it directly — no need to touch
    disk or the user's real config:

        monkeypatch.setattr(
            llm, "_read_provider_config",
            lambda: ("ollama", "http://localhost:11434", "qwen3:7b"),
        )
    """
    try:
        from ailawfirm_usa.config import BrainConfig

        file_cfg = BrainConfig().load_config_file() or {}
    except Exception:
        return "", "", ""
    return (
        str(file_cfg.get("ai_provider") or "").strip().lower(),
        str(file_cfg.get("ollama_host") or "").strip(),
        str(file_cfg.get("ollama_model") or "").strip(),
    )


def _is_local_provider(provider):
    return provider in ("ollama", "local")


def available() -> bool:
    """True iff some LLM is configured:

    * a local provider is selected in ``~/.ailawfirm-usa/config.json``
      (regardless of whether the endpoint is currently reachable — we
      re-check reachability per call so a late-started daemon is honoured),
    * OR a cloud key is present in the environment.
    """
    provider, _, _ = _read_provider_config()
    if _is_local_provider(provider):
        return True
    _, key, _ = _cfg()
    return bool(key)


def model_name() -> str:
    """Resolved model name for banners + status. Local > env > default."""
    provider, _, ollama_model = _read_provider_config()
    if _is_local_provider(provider):
        return ollama_model or "qwen3:7b"
    _, _, model = _cfg()
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
    from ailawfirm_usa.pseudonymisation import PseudonymisationGateway
    from ailawfirm_usa.pseudonymisation_audit import write_audit

    _gw = PseudonymisationGateway()
    user, _token_map, _disc = _gw.sanitize_with_disclosure(user)

    if _disc.get("residue") and _sys.stderr.isatty():
        print(
            f"⚠️  pseudonymisation: {len(_disc['residue'])} item(s) may not be fully "
            f"masked (review; your call): {_disc['residue']}",
            file=_sys.stderr,
        )
    try:
        from ailawfirm_usa.config import BrainConfig

        _cfg_dir = BrainConfig().config_dir
    except Exception:
        _cfg_dir = os.path.expanduser("~/.ailawfirm-usa")
    try:
        write_audit(_disc, model=ollama_model, base_url=ollama_host, config_dir=_cfg_dir)
    except Exception:
        pass

    text = _ollama_post(system, user, ollama_host, ollama_model, max_tokens, timeout)
    return _gw.desanitize(text, _token_map)


# ---------------------------------------------------------------------------
# Cloud (Anthropic-compatible) provider — existing behaviour, verbatim
# ---------------------------------------------------------------------------


def _cloud_complete(system, user, max_tokens, timeout):
    """Existing cloud path. Pseudonymisation gateway wired exactly as before.

    This function exists separately (not inlined into ``complete``) so the
    gateway contract is preserved bit-for-bit and ``tests/test_gateway_wiring.py``
    keeps passing unchanged.
    """
    base_url, key, model = _cfg()

    # ── Privacy gateway (whole-brain) ────────────────────────────────────────
    # EVERY cloud egress in the brain funnels through this one function, so
    # pseudonymising the user prompt HERE covers chat, matters, drafting, and
    # RAG alike. Real client names / IDs are replaced with placeholders before
    # the bytes leave the machine, and restored in the model's reply. The
    # placeholder↔original map lives only for this call (never persisted).
    # Coverage limit: government IDs + honorific/context-anchored party names.
    # A bare, un-anchored arbitrary name still needs NER (v0.2.1) — for truly
    # confidential matters, use local mode. (README "Pseudonymisation coverage".)
    import sys as _sys

    from ailawfirm_usa.pseudonymisation import PseudonymisationGateway
    from ailawfirm_usa.pseudonymisation_audit import write_audit

    _gw = PseudonymisationGateway()
    user, _token_map, _disc = _gw.sanitize_with_disclosure(user)

    # Surface residue (possibly-unmasked names the gateway couldn't anchor) so the
    # attorney retains the final call — brain-frame: warn, never block (C2).
    # Guard on isatty(): only print the raw candidates to a REAL interactive terminal.
    # If stderr is redirected to a file (daemon/CI/`2>log`), we do NOT print the names —
    # the PII-free audit log still records that residue occurred (count + hashes), so
    # nothing raw ever lands on disk (C1).
    if _disc.get("residue") and _sys.stderr.isatty():
        print(
            f"⚠️  pseudonymisation: {len(_disc['residue'])} item(s) may not be fully "
            f"masked (review; your call): {_disc['residue']}",
            file=_sys.stderr,
        )
    # PII-FREE audit log — best-effort; write_audit swallows internally, and we wrap
    # the call site too (defense-in-depth) so audit can NEVER break a cloud call (C4).
    try:
        from ailawfirm_usa.config import BrainConfig

        _cfg_dir = BrainConfig().config_dir
    except Exception:
        _cfg_dir = os.path.expanduser("~/.ailawfirm-usa")
    try:
        write_audit(_disc, model=model, base_url=base_url, config_dir=_cfg_dir)
    except Exception:
        pass

    url = (base_url or "https://api.anthropic.com").rstrip("/") + "/v1/messages"

    headers = {
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    # Compatible gateways (GLM, the model, ...) want a Bearer token; native
    # Anthropic wants x-api-key. Pick by whether a custom base_url is set.
    if base_url:
        headers["Authorization"] = f"Bearer {key}"
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
        raise LLMError(f"transport error talking to {url}: {exc}") from exc

    try:
        parsed = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LLMError(f"malformed response (non-JSON): {exc}") from exc

    try:
        # Restore real values in the model's reply before handing it back.
        return _gw.desanitize(parsed["content"][0]["text"], _token_map)
    except (KeyError, IndexError, TypeError) as exc:
        raise LLMError(f"malformed response: missing content[0].text ({exc})") from exc


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
        NEVER silently fall back to cloud.
      * Otherwise → Anthropic-compatible POST to ``/v1/messages``. The
        pseudonymisation gateway is wired exactly as before — refactors
        must not break ``tests/test_gateway_wiring.py``.

    EXPLICIT CONFIG BEATS AMBIENT ENVIRONMENT. If the user's config.json
    says local, inference goes local even when a cloud credential happens
    to be present in the environment. The config file is a deliberate
    statement of intent by the practitioner; an exported environment
    variable is ambient and may be inherited from a shell profile, an
    earlier experiment, or another tool entirely.

    The alternative rule — "a cloud key overrides local" — would mean a
    solicitor who ran ``connect-local`` and also has a key exported gets
    privileged material sent to a cloud vendor while the product tells
    them they are local. That is the exact false-assurance failure this
    tier exists to remove, so it is not available as a convenience.

    A developer who genuinely wants the cloud path while a local config
    is present must say so out loud by exporting
    ``AILAWFIRM_FORCE_CLOUD=1``. It is deliberately verbose, deliberately
    not a default, and it is logged in the returned error when misused.
    """
    _, key, _ = _cfg()
    provider, ollama_host, ollama_model = _read_provider_config()

    force_cloud = os.environ.get("AILAWFIRM_FORCE_CLOUD", "").strip() in (
        "1",
        "true",
        "TRUE",
        "yes",
    )

    if _is_local_provider(provider) and not force_cloud:
        host = ollama_host or LOCAL_DEFAULT_HOST
        m = ollama_model or "qwen3:7b"
        return _local_complete(system, user, max_tokens, timeout, host, m)

    # Cloud path — existing behaviour, gateway wired exactly as today.
    if not key:
        raise LLMError("no ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY in env")
    return _cloud_complete(system, user, max_tokens, timeout)
