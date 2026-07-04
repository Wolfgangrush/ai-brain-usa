#!/usr/bin/env bash
# Install repo git hooks so local push == CI lint gate. Idempotent.
# Run once per fresh clone:  bash scripts/install-git-hooks.sh
set -euo pipefail
ROOT="$(git rev-parse --show-toplevel)"
cp "$ROOT/scripts/hooks/pre-push" "$ROOT/.git/hooks/pre-push"
chmod +x "$ROOT/.git/hooks/pre-push"
echo "installed: .git/hooks/pre-push (ruff lint gate mirroring CI)"
