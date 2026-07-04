# Contributing to AI Brain — USA

Thanks for wanting to help. **AI Brain — USA** is open source (MIT). Contributions of all sizes are welcome — typo fixes, statute-corpus corrections, new drafting templates, agent improvements, and translations.

## Getting started

```bash
git clone https://github.com/Wolfgangrush/ai-law-firm-usa.git
cd ai-law-firm-usa
pip install -e ".[dev]"
```

## Running tests

```bash
pytest tests/ -v
```

All tests must pass before a PR. Tests run without API keys or network access.

## Project structure

```
ailawfirm_usa/   ← core package (see ailawfirm_usa/README.md for the module/agent guide)
tests/         ← test suite
examples/      ← usage examples
docs/          ← additional documentation
assets/        ← logo + brand
```

## PR guidelines

1. Fork and create a feature branch: `git checkout -b feat/my-thing`
2. Make your change
3. Add or update tests where applicable
4. Run `pytest tests/ -v` — everything must pass
5. Commit using [conventional commits](https://www.conventionalcommits.org/):
   - `feat: add <jurisdiction> statute digest`
   - `fix: correct citation-parser edge case`
   - `docs: clarify model-setup guide`
6. Push to your fork and open a PR against `main`

## Code style

- **Formatting**: [Ruff](https://docs.astral.sh/ruff/), 100-char line limit (configured in `pyproject.toml`)
- **Naming**: `snake_case` for functions/variables, `PascalCase` for classes
- **Docstrings**: on all modules and public functions
- **Type hints**: where they improve readability
- **Dependencies**: keep minimal; open an issue before adding a new one

## Domain contributions (statutes / templates)

Legal accuracy matters most. If you correct a statute digest, drafting template, or compliance mapping, cite the primary source (Act / section / rule, official gazette, or regulator notice) in the PR. See [KNOWLEDGE_PROVENANCE.md](KNOWLEDGE_PROVENANCE.md) for the provenance discipline this project follows.

## Architecture principles

- **Local first** — everything runs on the user's machine; no cloud dependency for core features.
- **Zero API by default** — core features must work without any API key.
- **No PII, no data collection** — see [NO_PII_NO_DATA.md](NO_PII_NO_DATA.md).
- **Honest claims** — every domain claim traces to a cited source.

## License

MIT — your contributions are released under the same license.
