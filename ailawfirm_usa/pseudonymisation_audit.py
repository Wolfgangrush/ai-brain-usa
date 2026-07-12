"""PII-FREE pseudonymisation audit log (v0.1.2).

Every cloud egress via ``brain.llm.complete()`` appends one JSONL record describing
what was masked AND how much residue was left. The on-disk record NEVER contains raw
client PII — only sha256-16 hashes + counts + the model/host. This reconciles the two
README promises: residue is *surfaced* to the attorney (in-memory) AND *audit-logged*
(on disk) WITHOUT ever writing a real name to disk.

    <config_dir>/audit/pseudonymisation-YYYY-MM.log     (one JSON line per egress)

Best-effort: ALL IO errors are swallowed and returned as ``None`` — the audit must
NEVER block or break a cloud call.
"""

from __future__ import annotations

import datetime as _dt
import json
import os
from typing import Optional
from urllib.parse import urlparse


def write_audit(
    disclosure: dict,
    model: str,
    base_url: str,
    config_dir: Optional[str] = None,
) -> Optional[str]:
    """Append one PII-FREE audit record. Returns the log path, or ``None`` on any error.

    ``config_dir`` is the firm's config directory (default ``~/.ailawfirm-usa``); the
    log lands in ``<config_dir>/audit/``.
    """
    try:
        base = config_dir or os.path.expanduser("~/.ailawfirm-usa")
        audit_dir = os.path.join(base, "audit")
        os.makedirs(audit_dir, exist_ok=True)
        month = _dt.datetime.now(_dt.timezone.utc).strftime("%Y-%m")
        path = os.path.join(audit_dir, f"pseudonymisation-{month}.log")

        host = ""
        if base_url:
            try:
                host = urlparse(base_url).hostname or ""
            except Exception:
                host = ""

        record = {
            "ts": _dt.datetime.now(_dt.timezone.utc).isoformat(),
            "model": model,
            "base_url_host": host,  # HOST ONLY — no path, no key
            "masked_counts": disclosure.get("masked_counts", {}),
            "residue_count": len(disclosure.get("residue", [])),
            # ONLY hashes reach disk — raw candidate names are dropped here (C1).
            "residue_hashes": disclosure.get("residue_hashes", []),
            "residue_lengths": disclosure.get("residue_lengths", []),
        }
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record) + "\n")
        return path
    except Exception:
        return None
