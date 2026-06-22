# agents/ — Specialized agents

Each agent is a domain-specialist handler with a single `handle(payload: str) -> dict` function. The brain's router dispatches to the agent based on classified intent.

## v0.1 agents (skeletons)

| Agent | Status | What it does | Backed by |
|---|---|---|---|
| `matter_agent` | STUB | active matter context | (v0.2+) |
| `citation_agent` | WRAPPED | parses/validates citations | `india_citation_validator` MCP tool |
| `court_agent` | WRAPPED | court info / jurisdiction | `india_court_lookup` MCP tool |
| `drafting_agent` | STUB | invokes wolfgang_rush plugins | (v0.2+) |
| `compliance_agent` | KEYWORD-FLAG | Rule 36 + DPDP firewall | keyword detect (v0.2+ real logic) |
| `deadline_agent` | STUB | limitation + hearing dates | (v0.2+) |

## Adding a new agent (v0.2+ template)

1. Create `ailawfirm_india/agents/<your_agent>.py` with `def handle(payload: str) -> dict:`
2. Add the Intent enum value to `brain/intents.py` if it's a new intent class
3. Add the mapping in `AGENT_FOR_INTENT` in `brain/intents.py`
4. Add classifier keywords to `brain/classifier.py` _RULES list
5. Add unit tests in `tests/test_agents_<your_agent>.py`
