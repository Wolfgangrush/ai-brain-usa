"""Provider-agnostic LLM client for the AI Law Brain.

Talks to whatever Anthropic-compatible host the app was launched under:

  * ``claude-glm``       — exports ANTHROPIC_BASE_URL pointing at Z.ai GLM 5.2.
  * ``claude-minimax``   — exports ANTHROPIC_BASE_URL pointing at the model.
  * Native Anthropic     — exports nothing (defaults to api.anthropic.com).

Credentials are read from the environment **at call time** (not import time),
so the same module works under every launcher and so a launcher that sets
env vars late is still honoured.
"""

import json
import os
import urllib.error
import urllib.request
from typing import Tuple


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


def available() -> bool:
    """True iff a key is present in the environment.

    Callers use this to decide whether to hit the LLM or fall back to offline
    logic (rule tables, cached answers, ``"unknown — no brain key"`` strings).
    """
    _, key, _ = _cfg()
    return bool(key)


def model_name() -> str:
    """Resolved model name from the environment. Handy for banners / status."""
    _, _, model = _cfg()
    return model


def complete(
    system: str,
    user: str,
    max_tokens: int = 1024,
    timeout: float = 60.0,
) -> str:
    """Send one ``/v1/messages`` request and return the assistant text.

    Returns the first ``content[0].text`` block. Raises :class:`LLMError` on
    missing config, transport failure, or a malformed response payload.
    """
    base_url, key, model = _cfg()
    if not key:
        raise LLMError("no ANTHROPIC_AUTH_TOKEN / ANTHROPIC_API_KEY in env")

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
