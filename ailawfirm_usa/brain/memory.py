"""
ailawfirm_usa.brain.memory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Retrospective session memory for the terminal brain (AI Law Brain).

Logs every interaction locally as one JSON object per line so the brain can
recall across sessions ("what did we do last time?", "remind me…"). Local-only,
offline, no third-party dependencies, fail-soft on any IO / parse error.

Store:
    ~/.ailawfirm-usa/memory/sessions.jsonl   (append-only, one JSON per line)

Public API:
    log_interaction(query, response) -> None
    load_recent(n=5) -> list[dict]
    count() -> int
    recap(n=3) -> str

All functions are guaranteed never to raise — a missing directory, a corrupt
line, a permission error: everything degrades to a sensible empty default.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

# --------------------------------------------------------------------------- #
# storage locations
# --------------------------------------------------------------------------- #

MEMORY_DIR: Path = Path(os.path.expanduser("~/.ailawfirm-usa/memory/"))
SESSIONS_FILE: Path = MEMORY_DIR / "sessions.jsonl"


# --------------------------------------------------------------------------- #
# internal helpers (also fail-soft)
# --------------------------------------------------------------------------- #


def _ensure_dir() -> None:
    """Create the memory directory if missing. Never raises."""
    try:
        MEMORY_DIR.mkdir(parents=True, exist_ok=True)
    except Exception:
        # EACCES, ENOSPC, ENOTDIR, weird NFS — silently skip; callers will no-op.
        pass


def _now_iso() -> str:
    """UTC ISO-8601 timestamp with second precision and explicit +00:00 offset."""
    try:
        return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")
    except Exception:
        # Hard-coded sentinel — never blank, never misleading.
        return "1970-01-01T00:00:00+00:00"


def _clip(text: str, limit: int = 120) -> str:
    """Trim to ~limit chars with an ellipsis. Never raises."""
    try:
        if not isinstance(text, str):
            text = str(text)
    except Exception:
        return ""
    text = text.strip()
    if len(text) > limit:
        # Keep room for the ellipsis.
        text = text[: max(0, limit - 3)].rstrip() + "..."
    return text


def _summary_from_result(result: Any) -> str:
    """
    Pick the most human-friendly short label from the brain's result dict.

    Priority (per brain contract): doc_type -> category -> extracted -> status,
    with a final fallback to a short stringification. Empty string if nothing
    usable is found.
    """
    if not isinstance(result, dict):
        return ""
    # Preferred human-friendly keys, in priority order.
    for key in ("doc_type", "category", "extracted", "status", "summary", "message"):
        try:
            v = result.get(key)
        except Exception:
            v = None
        if isinstance(v, str) and v.strip():
            return _clip(v, 120)
    # Last resort: stringify the dict (clipped) so the recap is never blank.
    try:
        return _clip(str(result), 120)
    except Exception:
        return ""


def _safe_response(response: Any) -> Dict[str, Any]:
    """Coerce arbitrary input into a dict we can index without exploding."""
    if isinstance(response, dict):
        return response
    if response is None:
        return {}
    try:
        return {"result": response}
    except Exception:
        return {}


def _safe_query(query: Any) -> str:
    """Coerce arbitrary query input into a string. Empty string on total failure."""
    if isinstance(query, str):
        return query
    if query is None:
        return ""
    try:
        return str(query)
    except Exception:
        return ""


# --------------------------------------------------------------------------- #
# IO primitives (each one never raises)
# --------------------------------------------------------------------------- #


def _read_lines() -> List[str]:
    """Read all lines of the JSONL store. Empty list if missing/unreadable."""
    try:
        with open(SESSIONS_FILE, "r", encoding="utf-8") as fh:
            return fh.readlines()
    except Exception:
        # FileNotFoundError, PermissionError, IsADirectoryError, decoding issues —
        # all collapse to "no history" rather than blowing up the brain.
        return []


def _parse_line(line: str) -> Optional[Dict[str, Any]]:
    """Parse one JSONL line into a dict. None if anything is wrong."""
    if not isinstance(line, str) or not line.strip():
        return None
    try:
        obj = json.loads(line)
    except Exception:
        return None
    if not isinstance(obj, dict):
        return None
    return obj


# --------------------------------------------------------------------------- #
# public API
# --------------------------------------------------------------------------- #


def log_interaction(query: str, response: dict) -> None:
    """
    Append one JSONL line describing this brain interaction.

    Schema written:
        {
            "ts":      "2026-07-04T05:40:00+00:00",   # UTC ISO-8601
            "query":   "<the advocate's question, verbatim>",
            "intent":  "<response.get('intent', 'unknown')>",
            "agent":   "<response.get('agent',  '?'     )>",
            "ok":      <bool>,
            "summary": "<short human-friendly label, <= 120 chars>"
        }

    Never raises. On any IO failure, silently no-ops so a logging bug never
    blocks the actual brain from running.
    """
    try:
        q = _safe_query(query)
        r = _safe_response(response)

        try:
            intent = r.get("intent", "unknown")
        except Exception:
            intent = "unknown"
        if not isinstance(intent, str):
            try:
                intent = str(intent)
            except Exception:
                intent = "unknown"

        try:
            agent = r.get("agent", "?")
        except Exception:
            agent = "?"
        if not isinstance(agent, str):
            try:
                agent = str(agent)
            except Exception:
                agent = "?"

        try:
            ok_flag = bool(r.get("ok", True))
        except Exception:
            ok_flag = True

        try:
            result_payload = r.get("result")
        except Exception:
            result_payload = None
        summary = _summary_from_result(result_payload)

        record = {
            "ts": _now_iso(),
            "query": q,
            "intent": intent,
            "agent": agent,
            "ok": ok_flag,
            "summary": summary,
        }

        _ensure_dir()
        with open(SESSIONS_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        # Absolute last-resort safety net — logging must never break the brain.
        return None


def load_recent(n: int = 5) -> List[Dict[str, Any]]:
    """
    Return up to the last `n` valid logged interactions (most-recent last).

    Skips unparseable or non-dict lines silently. Returns [] if the file is
    missing or unreadable. Never raises.
    """
    try:
        n_int = int(n)
    except Exception:
        n_int = 5
    if n_int <= 0:
        return []

    lines = _read_lines()
    parsed: List[Dict[str, Any]] = []
    for line in lines:
        obj = _parse_line(line)
        if obj is not None:
            parsed.append(obj)

    return parsed[-n_int:]


def count() -> int:
    """
    Total number of *valid* logged interactions (skips corrupt lines).

    Returns 0 if the file is missing or unreadable. Never raises.
    """
    lines = _read_lines()
    total = 0
    for line in lines:
        if _parse_line(line) is not None:
            total += 1
    return total


def recap(n: int = 3) -> str:
    """
    Human-readable multi-line summary of the last `n` interactions.

    Format:
        Last <n> interactions:
          - [<UTC timestamp>] <intent> -> <agent> : <summary>
          - ...

    If there is no recorded history, returns exactly:
        "No past sessions yet — this is a fresh start."

    Never raises.
    """
    try:
        n_int = int(n)
    except Exception:
        n_int = 3
    if n_int <= 0:
        n_int = 3

    try:
        recent = load_recent(n_int)
    except Exception:
        recent = []

    if not recent:
        return "No past sessions yet — this is a fresh start."

    label = "interaction" if len(recent) == 1 else "interactions"
    lines: List[str] = [f"Last {len(recent)} {label}:"]

    for item in recent:
        if not isinstance(item, dict):
            continue
        ts = item.get("ts", "?")
        if not isinstance(ts, str):
            try:
                ts = str(ts)
            except Exception:
                ts = "?"
        intent = item.get("intent", "unknown")
        if not isinstance(intent, str):
            intent = "unknown"
        agent = item.get("agent", "?")
        if not isinstance(agent, str):
            agent = "?"
        summary = item.get("summary", "")
        if not isinstance(summary, str):
            summary = ""

        row = f"  - [{ts}] {intent} -> {agent}"
        if summary:
            row += f" : {summary}"
        lines.append(row)

    return "\n".join(lines)
