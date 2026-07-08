#!/usr/bin/env bash
# Starship prompt: install + link config. Init line lives in zsh/.zshrc.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os
ensure_brew

brew_install starship
link_file "$SCRIPT_DIR/starship.toml" "$HOME/.config/starship.toml"

ok "Starship setup complete."
