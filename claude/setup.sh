#!/usr/bin/env bash
# Claude Code: CLI install + global settings + statusline.
# Plugins install themselves on next `claude` start from settings.json
# (enabledPlugins + extraKnownMarketplaces). See claude/README.md.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# ---- CLI ----
if command -v claude &>/dev/null; then
  ok "Claude Code already installed: $(claude --version)"
else
  info "Installing Claude Code CLI (native installer)..."
  if curl -fsSL https://claude.ai/install.sh | bash; then
    ok "Claude Code installed. Installer puts it in ~/.local/bin; open a new terminal if 'claude' is not found."
  else
    warn "Installer failed. See https://claude.com/claude-code for install options."
    exit 1
  fi
fi

# ---- Settings + statusline + global memory ----
link_file "$SCRIPT_DIR/settings.json" "$HOME/.claude/settings.json"
link_file "$SCRIPT_DIR/statusline-command.sh" "$HOME/.claude/statusline-command.sh"
link_file "$SCRIPT_DIR/CLAUDE.md" "$HOME/.claude/CLAUDE.md"

info "Plugins listed in settings.json install automatically on the next 'claude' start."
info "VS Code extension is handled by the vscode tool (vscode/extensions.txt)."
ok "Claude Code setup complete."
