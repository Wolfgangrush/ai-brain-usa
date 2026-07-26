"""USA matter tracker — local JSON store.

Module-level `_STORE_PATH` points at `~/.ailawfirm_usa/matters.json`.
Pure stdlib. Never raises on a missing or corrupt store; handle()
always returns a dict that includes `agent == "matter_agent"`.
"""

from __future__ import annotations

import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

AGENT_NAME = "matter_agent"
_STORE_PATH: Path = Path(os.path.expanduser("~/.ailawfirm_usa/matters.json"))


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load() -> Dict[str, Dict[str, Any]]:
    try:
        if not _STORE_PATH.exists():
            return {}
        with _STORE_PATH.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, dict):
            return data
    except (OSError, json.JSONDecodeError):
        pass
    return {}


def _save(store: Dict[str, Dict[str, Any]]) -> None:
    try:
        _STORE_PATH.parent.mkdir(parents=True, exist_ok=True)
        tmp = _STORE_PATH.with_suffix(_STORE_PATH.suffix + ".tmp")
        with tmp.open("w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)
        tmp.replace(_STORE_PATH)
    except OSError:
        # Persistence is best-effort; handle() must never raise.
        pass


def _slugify(name: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", (name or "").strip()).strip("_").lower()
    return s or uuid.uuid4().hex


def _add_matter(text: str) -> Dict[str, Any]:
    m = re.search(r"(?:add|new)\s+matter\s+(.+)$", text.strip(), re.IGNORECASE)
    name = (m.group(1).strip() if m else "")
    if not name:
        name = f"Matter {datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}"

    key = _slugify(name)
    store = _load()
    now = _now_iso()
    existing = store.get(key, {})
    record = {
        "name": existing.get("name", name),
        "note": existing.get("note", ""),
        "updated": now,
    }
    store[key] = record
    _save(store)
    return {
        "agent": AGENT_NAME,
        "status": "ok",
        "action": "add",
        "matter": record["name"],
        "updated": now,
    }


def _list_matters() -> Dict[str, Any]:
    store = _load()
    names = [rec.get("name", key) for key, rec in store.items()]
    return {
        "agent": AGENT_NAME,
        "status": "ok",
        "action": "list",
        "matters": names,
        "count": len(names),
    }


def _lookup(text: str) -> Dict[str, Any]:
    m = re.search(
        r"(?:status\s+of|about|matter)\s+(.+)$", text.strip(), re.IGNORECASE
    )
    if not m:
        return {
            "agent": AGENT_NAME,
            "status": "ok",
            "action": "noop",
            "message": "No matter specified.",
        }
    query = m.group(1).strip()
    key = _slugify(query)
    store = _load()
    rec = store.get(key)
    if rec is None:
        # Fallback: case-insensitive substring match on display name.
        for k, r in store.items():
            if query.lower() in str(r.get("name", "")).lower():
                rec = r
                key = k
                break
    if rec is None:
        return {
            "agent": AGENT_NAME,
            "status": "ok",
            "action": "lookup",
            "query": query,
            "found": False,
        }
    return {
        "agent": AGENT_NAME,
        "status": "ok",
        "action": "lookup",
        "query": query,
        "found": True,
        "matter": rec.get("name", query),
        "note": rec.get("note", ""),
        "updated": rec.get("updated", ""),
    }


def handle(payload: str) -> Dict[str, Any]:
    text = (payload or "").strip()
    lower = text.lower()

    if re.search(r"^\s*(?:add|new)\s+matter\b", lower):
        return _add_matter(text)

    if re.search(r"^\s*(?:list|show|my)\s+matters?\s*$", lower):
        return _list_matters()

    if re.search(r"^\s*(?:status\s+of|about|matter)\b", lower):
        return _lookup(text)

    return {
        "agent": AGENT_NAME,
        "status": "ok",
        "action": "noop",
        "message": "Try: 'add matter <name>', 'list matters', or 'status of <name>'.",
    }
