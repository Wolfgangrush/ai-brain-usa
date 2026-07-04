# Transparency Gate

This skill delegates to the shared agent library at drafting-agents-core.

**On invocation:**
1. Read `../../drafting-agents-core/agents/transparency_gate/SKILL.md` (the canonical skill body)
2. Load this firm's config from `~/.ailawfirm_usa/config.toml`
3. Substitute placeholders ({{JURISDICTION_*}}) with config values
4. Execute the canonical skill body with substituted values

See: https://github.com/Wolfgangrush/drafting-agents-core
