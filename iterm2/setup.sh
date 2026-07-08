#!/usr/bin/env bash
# iTerm2 (macOS only): app, shell integration, dynamic profile (theme + font).
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os

if [ "$DOTFILES_OS" != "macos" ]; then
  skip "iTerm2 is macOS-only, skipping."
  exit 0
fi

ensure_brew

if [ -d "/Applications/iTerm.app" ]; then
  ok "iTerm2 already installed."
else
  brew_install iterm2 --cask
fi

brew_install font-meslo-lg-nerd-font --cask

# ---- Shell integration (sourced by zsh/.zshrc when present) ----
if [ -f "$HOME/.iterm2_shell_integration.zsh" ]; then
  ok "iTerm2 shell integration already installed."
else
  info "Installing iTerm2 shell integration..."
  curl -fsSL https://iterm2.com/shell_integration/zsh -o "$HOME/.iterm2_shell_integration.zsh"
fi

# ---- Dynamic profile (color theme + font) ----
PROFILE_DIR="$HOME/Library/Application Support/iTerm2/DynamicProfiles"
mkdir -p "$PROFILE_DIR"
if diff -q "$SCRIPT_DIR/com.dotfiles.json" "$PROFILE_DIR/com.dotfiles.json" &>/dev/null; then
  ok "iTerm2 dynamic profile already up to date."
else
  info "Installing iTerm2 dynamic profile..."
  cp "$SCRIPT_DIR/com.dotfiles.json" "$PROFILE_DIR/com.dotfiles.json"
fi

# ---- Default profile ----
if [ "$(defaults read com.googlecode.iterm2 "Default Bookmark Guid" 2>/dev/null)" = "557036D3-EF41-4D30-A395-3F301A17D49B" ]; then
  ok "iTerm2 default profile already set."
else
  defaults write com.googlecode.iterm2 "Default Bookmark Guid" -string "557036D3-EF41-4D30-A395-3F301A17D49B"
fi

ok "iTerm2 setup complete. Restart iTerm2 (Cmd+Q then relaunch) for theme + default profile."
