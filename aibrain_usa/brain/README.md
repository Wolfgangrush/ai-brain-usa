# brain/ — Decision-maker layer

The brain receives a user request, classifies the intent, and routes to the
matching specialized agent. The user-facing surface never loads everything onto
a single context — the brain pre-filters intent and the agent loads only the
relevant context.

Pattern adopted from the memory layer's own brain-frame restructure (2026-05-08).

## v0.1 — what's here
- `intents.py` — Intent enum + intent→agent routing table
- `classifier.py` — rule-based keyword classifier (Intent detection)
- `router.py` — dispatches an Intent to the matching agent's `handle()` function
- `think(text)` — convenience function: classify + route in one call

## v0.2+ — what's coming
- Ollama-based classifier (replaces _RULES keyword match)
- Context loader (per-matter alias-compressed context)
- Agent registry with hot-pluggable agents
- Feedback loop: track which routing decisions led to satisfaction vs re-classification
