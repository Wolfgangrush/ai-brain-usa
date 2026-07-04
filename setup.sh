#!/usr/bin/env bash
# Setup script for AI Brain — USA
# Ensures drafting-agents-core is available as a sibling repo

set -euo pipefail

PARENT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
CORE_DIR="$PARENT_DIR/drafting-agents-core"

if [ ! -d "$CORE_DIR" ]; then
  echo "Drafting Agents Core not found alongside this firm."
  echo "Cloning from GitHub..."
  git clone https://github.com/Wolfgangrush/drafting-agents-core "$CORE_DIR"
else
  echo "Drafting Agents Core found at: $CORE_DIR"
  echo "(run 'cd $CORE_DIR && git pull' to update)"
fi

# Create firm config from template
CONFIG_FILE="$HOME/.ailawfirm_usa/config.toml"
mkdir -p "$(dirname "$CONFIG_FILE")"
if [ ! -f "$CONFIG_FILE" ]; then
  cp ./config.toml.template "$CONFIG_FILE"
  echo "Firm config created at: $CONFIG_FILE"
fi

echo "Setup complete. Run 'claude' from this directory to start."
