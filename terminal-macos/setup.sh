#!/usr/bin/env bash
# Terminal.app (macOS only): Solarized themes + MesloLGS NF font defaults.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os

if [ "$DOTFILES_OS" != "macos" ]; then
  skip "Terminal.app is macOS-only, skipping."
  exit 0
fi

ensure_brew

brew_install font-meslo-lg-nerd-font --cask

# ---- Download themes if not already downloaded ----
if [ ! -d "$HOME/Downloads/macos-terminal-themes-master" ]; then
  info "Downloading Terminal.app themes..."
  curl -L https://github.com/lysyi3m/macos-terminal-themes/archive/refs/heads/master.zip -o "$HOME/Downloads/terminal-themes.zip"
  unzip -o "$HOME/Downloads/terminal-themes.zip" -d "$HOME/Downloads"
  rm "$HOME/Downloads/terminal-themes.zip"
else
  ok "Terminal themes already downloaded."
fi

# ---- Load themes into Terminal if not already loaded ----
osascript -e 'quit app "Terminal"' || true
sleep 2
for theme in "$HOME/Downloads/macos-terminal-themes-master/themes/"*.terminal; do
  theme_name=$(basename "$theme" .terminal)
  if ! defaults read com.apple.Terminal "Window Settings" | grep -q "$theme_name"; then
    open "$theme"
  fi
done
sleep 5
osascript -e 'quit app "Terminal"' || true

# ---- Default theme + font ----
if defaults read com.apple.Terminal "Default Window Settings" 2>/dev/null | grep -q "Solarized Dark"; then
  ok "Terminal default theme already set."
else
  defaults write com.apple.Terminal "Default Window Settings" -string "Solarized Dark"
  defaults write com.apple.Terminal "Startup Window Settings" -string "Solarized Dark"
fi

ok "Terminal.app setup complete. Restart Terminal for all changes to take effect."
