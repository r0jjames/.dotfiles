#!/usr/bin/env bash
# WezTerm: install (macOS) + link config. On WSL, WezTerm runs on the Windows
# host — see README for pointing it at this repo's config.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os

if [ "$DOTFILES_OS" = "linux" ]; then
  skip "WezTerm belongs on the Windows host in a WSL setup. See wezterm/README.md."
  exit 0
fi

ensure_brew

brew_install wezterm --cask
brew_install font-go-mono-nerd-font --cask

# ---- Config ----
link_file "$SCRIPT_DIR/wezterm.lua" "$HOME/.config/wezterm/wezterm.lua"
link_file "$SCRIPT_DIR/events.lua" "$HOME/.config/wezterm/events.lua"

ok "WezTerm setup complete. Restart WezTerm to pick up config changes."
