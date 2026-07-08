#!/usr/bin/env bash
# Citrix VDI (macOS only): Karabiner-Elements + a Citrix-scoped rule so
# Windows IDE shortcuts (Alt+F1, Alt+F7, Shift+F6, ...) reach the VDI intact.
# Runs on the Mac — nothing is installed or configured inside the VDI.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os

if [ "$DOTFILES_OS" != "macos" ]; then
  skip "citrix-vdi is macOS-only, skipping."
  exit 0
fi

ensure_brew

if [ -d "/Applications/Karabiner-Elements.app" ]; then
  ok "Karabiner-Elements already installed."
else
  brew_install karabiner-elements --cask
fi

# ---- Complex-modification rule (assets folder; enabled once in the GUI) ----
ASSETS_DIR="$HOME/.config/karabiner/assets/complex_modifications"
mkdir -p "$ASSETS_DIR"
if diff -q "$SCRIPT_DIR/karabiner-citrix.json" "$ASSETS_DIR/karabiner-citrix.json" &>/dev/null; then
  ok "Karabiner Citrix rule already up to date."
else
  info "Installing Karabiner Citrix rule..."
  cp "$SCRIPT_DIR/karabiner-citrix.json" "$ASSETS_DIR/karabiner-citrix.json"
fi

ok "citrix-vdi setup complete. One-time manual steps remain (Karabiner rule enable + Citrix keyboard preferences) — see citrix-vdi/README.md."
