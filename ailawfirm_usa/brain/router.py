"""
Brain router — dispatches an intent to the matching agent.

v0.1: import-and-call pattern. v0.2+: dynamic agent registry with
hot-pluggable agents (matches Brain's mp-* agent autoloading).

PROVENANCE: structural (no domain claims here).
"""

import importlib
from ailawfirm_usa.brain.intents import Intent, AGENT_FOR_INTENT


def route(intent: Intent, payload: str) -> dict:
    """Dispatch an intent to the matching agent's handle() function.

    Args:
        intent: classified Intent
        payload: original user text (passed through to agent)

    Returns:
        dict response from the agent
    """
    agent_module_name = AGENT_FOR_INTENT.get(intent, "matter_agent")
    full_module = f"ailawfirm_usa.agents.{agent_module_name}"
    try:
        mod = importlib.import_module(full_module)
        handler = getattr(mod, "handle", None)
        if handler is None:
            return {
                "ok": False,
                "intent": intent.value,
                "agent": agent_module_name,
                "error": f"agent module {full_module} has no handle() function",
            }
        result = handler(payload)
        return {
            "ok": True,
            "intent": intent.value,
            "agent": agent_module_name,
            "result": result,
        }
    except ImportError as e:
        return {
            "ok": False,
            "intent": intent.value,
            "agent": agent_module_name,
            "error": f"agent module import failed: {e}",
        }


def think(text: str) -> dict:
    """Convenience: classify + route in one call.

    The user-facing brain entry point.
    """
    from ailawfirm_usa.brain.classifier import classify

    intent = classify(text)
    response = route(intent, text)

    # AI-backed specialist answer when a host LLM is available (GLM 5.2 / Claude / …).
    # Offline-safe: specialists.answer() returns None when no ANTHROPIC_* env is present,
    # so the structured result is returned unchanged and deterministic tests still pass.
    try:
        from ailawfirm_usa.brain import specialists

        grounding = response.get("result", {}) if isinstance(response, dict) else {}
        ai = specialists.answer(intent.value, text, grounding)
        if ai:
            response["answer"] = ai
    except Exception:
        pass

    return response
