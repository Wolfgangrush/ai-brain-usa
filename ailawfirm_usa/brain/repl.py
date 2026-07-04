"""ailawfirm_usa.brain.repl — terminal front door for the brain.

A small, dependency-free Read–Eval–Print Loop that talks to the brain's
:class:`ailawfirm_usa.brain.router.think` function. The user types a
line, the brain classifies + routes it to the matching specialist agent,
and a readable answer is printed back to the terminal.

Public API
----------
- :func:`render`     — turn one ``think()`` response into a readable
  multi-line terminal string.
- :func:`run_ask`    — one-shot: classify + render a single query and
  return a process exit code.
- :func:`run_chat`   — interactive REPL loop.

The REPL is intentionally tiny: pure Python 3.9+ standard library, no
network, no API keys, no third-party imports. It is the front door of
the brain — it classifies, routes, and renders, but it never reads or
writes brain state on its own. All authority lives in ``router.think``.
"""

from __future__ import annotations

import json
import sys
from typing import Any, Dict, List, Tuple

from ailawfirm_usa.brain.router import think
from ailawfirm_usa.brain import memory

# ---------------------------------------------------------------------------
# Terminal niceties
# ---------------------------------------------------------------------------
#
# ANSI colour is only enabled when stdout is a real terminal. The REPL must
# stay readable when piped or redirected (e.g. ``echo '...' | python -m ...``).
_USE_COLOR = bool(sys.stdout.isatty())

_BOLD = "\x1b[1m"
_DIM = "\x1b[2m"
_RED = "\x1b[31m"
_CYAN = "\x1b[36m"
_RESET = "\x1b[0m"


def _c(code: str, text: str) -> str:
    """Apply an ANSI colour code to ``text`` only when stdout is a tty."""
    if not _USE_COLOR:
        return text
    return f"{code}{text}{_RESET}"


# Agent emoji map — purely cosmetic. Unknown agent names fall back to a
# neutral brain glyph so the header is never blank.
_AGENT_EMOJI = {
    "matter_agent": "📂",
    "citation_agent": "📚",
    "court_agent": "⚖️",
    "drafting_agent": "✍️",
    "deadline_agent": "🗓️",
    "compliance_agent": "🛡️",
    "router": "🧠",
}


def _agent_label(agent: str) -> str:
    """Return ``"<emoji> <agent>"`` for known agents, else ``"🧠 <agent>"``."""
    emoji = _AGENT_EMOJI.get(agent, "🧠")
    return f"{emoji} {agent}"


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------


def _format_value(value: Any) -> str:
    """Render a value for the terminal.

    Scalars are stringified. Dicts and lists are rendered as compact
    indented JSON (``indent=2``) so the structure is visible but the
    lines do not run off the screen.
    """
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=2, ensure_ascii=False, sort_keys=False)
    if value is None:
        return "null"
    return str(value)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def render(response: Dict[str, Any]) -> str:
    """Render one ``think()`` response as a readable multi-line string.

    Layout::

        🧠 <agent>  ·  intent: <intent>
        key          : value
        longer_key   : {
          "nested": "value"
        }

    The redundant ``"agent"`` key inside ``response["result"]`` is
    skipped because the agent is already named in the header. Nested
    dicts/lists are rendered as compact indented JSON.

    If ``response["ok"]`` is ``False`` the error is rendered with a
    ⚠️ prefix and the header metadata (intent, agent) is dimmed.
    """
    if not isinstance(response, dict):
        return _c(_RED, f"⚠️  malformed router response: {response!r}")

    if not response.get("ok", False):
        # Error path — make it impossible to miss.
        lines: List[str] = [
            _c(_RED, f"⚠️  {response.get('error', 'unknown error')}")
        ]
        intent = response.get("intent")
        agent = response.get("agent")
        if intent:
            lines.append(_c(_DIM, f"   intent: {intent}"))
        if agent and agent != "router":
            lines.append(_c(_DIM, f"   agent:  {agent}"))
        return "\n".join(lines)

    agent = response.get("agent", "router")
    intent = response.get("intent", "unknown")
    result = response.get("result")
    if not isinstance(result, dict) or not result:
        result = {k: v for k, v in response.items()
                  if k not in ("ok", "intent", "agent", "answer", "query")}

    header = (
        _c(_BOLD, _agent_label(agent))
        + _c(_DIM, f"  ·  intent: {intent}")
    )
    out: List[str] = [header]

    # AI specialist answer — present only when a host LLM (GLM/Claude/…) backed the
    # response. This is the buttery-smooth answer; the structured result follows as grounding.
    ai = response.get("answer")
    if ai:
        out.append("")
        out.append(str(ai).strip())
        out.append("")
        out.append(_c(_DIM, "  — grounding (local engine) —"))

    if not result:
        if ai:
            return "\n".join(out[:-1])  # drop the dangling grounding label
        out.append(_c(_DIM, "(no result)"))
        return "\n".join(out)

    # Drop the redundant "agent" key — it's already in the header.
    items: List[Tuple[str, Any]] = [
        (k, v) for k, v in result.items() if k != "agent"
    ]

    if not items:
        out.append(_c(_DIM, "(empty result)"))
        return "\n".join(out)

    width = max(len(str(k)) for k, _ in items)
    for key, value in items:
        key_str = _c(_CYAN, str(key).ljust(width))
        rendered = _format_value(value)
        # First line goes on the same line as the key; subsequent lines
        # are indented to align under the value column.
        lines = rendered.splitlines() or [""]
        out.append(f"{key_str}: {lines[0]}")
        for cont in lines[1:]:
            out.append(f"{' ' * (width + 2)}{cont}")

    return "\n".join(out)


def run_ask(query: str) -> int:
    """One-shot: classify ``query`` via ``think()`` and print the result.

    Returns ``0`` on a successful call (including a router-level
    ``ok=False`` response, which is rendered as a clean error) and
    ``1`` if ``query`` is empty or whitespace-only.
    """
    if not query or not query.strip():
        print(
            "usage: repl ask <query>  "
            "(or run `repl chat` for the interactive REPL)",
            file=sys.stderr,
        )
        return 1
    response = think(query)
    try:
        memory.log_interaction(query, response)
    except Exception:
        pass
    print(render(response))
    return 0


# Banner is module-level so `help` / `?` in the REPL can reprint it
# without re-running any logic.
_BANNER = (
    "ailawfirm_usa brain — terminal front door\n"
    "  routes to 6 specialists:\n"
    "    📂 matter_agent     — case-file lookup, facts, parties, exhibits\n"
    "    📚 citation_agent   — citations, precedents, statutory references\n"
    "    ⚖️  court_agent      — listings, status, adjournments, orders\n"
    "    ✍️  drafting_agent   — draft documents, replies, notices, opinions\n"
    "    🗓️  deadline_agent   — limitation, hearings, filings, reminders\n"
    "    🛡️  compliance_agent — regulatory, procedural, secretarial checks\n"
    "\n"
    "  ⚠️  Always verify AI output independently before relying on it.\n"
    "  type 'help' or '?' to reprint this banner · 'quit' / ':q' to exit\n"
)


def run_chat() -> int:
    """Interactive REPL loop.

    Prints a banner, then reads lines from stdin. ``quit`` / ``exit`` /
    ``:q`` exit cleanly; ``help`` / ``?`` reprint the banner; blank
    lines are skipped. Every other line is routed through
    :func:`think` and rendered via :func:`render`.

    Per-line handling is wrapped in ``try/except`` so a single bad
    input never kills the loop. ``EOFError`` and ``KeyboardInterrupt``
    both close the session gracefully.
    """
    print(_BANNER)
    while True:
        try:
            line = input("> ")
        except (EOFError, KeyboardInterrupt):
            # EOFError: piped input ended or Ctrl-D. KeyboardInterrupt:
            # Ctrl-C. Both should close the session politely.
            print()
            print("session closed.")
            return 0

        stripped = line.strip()
        if not stripped:
            continue
        if stripped in {"quit", "exit", ":q"}:
            print("session closed.")
            return 0
        if stripped in {"help", "?"}:
            print(_BANNER)
            continue

        # Per-line isolation — one bad input must not kill the loop.
        try:
            response = think(line)
        except Exception as exc:  # noqa: BLE001 — top-of-loop safety net
            print(_c(_RED, f"⚠️  router raised: {exc}"), file=sys.stderr)
            continue

        try:
            memory.log_interaction(line, response)
        except Exception:
            pass

        try:
            print(render(response))
        except Exception as exc:  # noqa: BLE001
            print(_c(_RED, f"⚠️  render failed: {exc}"), file=sys.stderr)


__all__ = ["render", "run_ask", "run_chat"]
