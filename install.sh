#!/usr/bin/env bash
# Dotfiles installer. Run everything:
#   ./install.sh
# Or a subset:
#   ./install.sh zsh nvim
set -e

DOTFILES_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$DOTFILES_DIR/lib/common.sh"

detect_os

ALL_TOOLS=(zsh starship nvim wezterm vscode claude agent-skills terminal-macos iterm2 citrix-vdi)
MAC_ONLY=(terminal-macos iterm2 citrix-vdi)

TOOLS=("$@")
if [ ${#TOOLS[@]} -eq 0 ]; then
  TOOLS=("${ALL_TOOLS[@]}")
fi

for tool in "${TOOLS[@]}"; do
  if [ ! -f "$DOTFILES_DIR/$tool/setup.sh" ]; then
    warn "Unknown tool: $tool (no $tool/setup.sh). Available: ${ALL_TOOLS[*]}"
    exit 1
  fi
done

for tool in "${TOOLS[@]}"; do
  if [ "$DOTFILES_OS" = "linux" ] && [[ " ${MAC_ONLY[*]} " == *" $tool "* ]]; then
    skip "$tool is macOS-only, skipping."
    continue
  fi
  echo ""
  echo "===== $tool ====="
  bash "$DOTFILES_DIR/$tool/setup.sh"
done

echo ""
ok "All done. Open a new terminal for shell changes to take effect."
