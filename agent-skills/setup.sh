#!/usr/bin/env bash
# Agent skills: symlink custom skills into ~/.claude/skills via install.py.
# Community skills are skipped here (network); fetch them with:
#   python3 agent-skills/install.py --target claude
# Copilot install runs on the work machine:
#   python3 install.py --target copilot
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

if ! command -v python3 &>/dev/null; then
  warn "python3 not found — skipping agent skills."
  exit 0
fi

python3 "$SCRIPT_DIR/install.py" --target claude --skills-only
ok "Agent skills setup complete."
