#!/usr/bin/env bash
# Zsh shell stack: zsh, modern CLI tools, plugins, ~/.zshrc (symlinked).
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os
ensure_brew

# ---- zsh itself ----
# Linux: apt (brew-installed zsh as a login shell is fragile). macOS: built in.
if [ "$DOTFILES_OS" = "linux" ]; then
  if command -v zsh &>/dev/null; then
    ok "zsh already installed."
  else
    info "Installing zsh via apt..."
    sudo apt-get update && sudo apt-get install -y zsh
  fi
  if [ "$(basename "${SHELL:-}")" != "zsh" ]; then
    info "Setting zsh as login shell..."
    chsh -s "$(command -v zsh)"
  else
    ok "zsh is already the login shell."
  fi
fi

# ---- CLI tools ----
for tool in bat eza fzf zoxide ripgrep fd htop; do
  brew_install "$tool"
done

# ---- Zsh plugins (brew, sourced by .zshrc) ----
brew_install zsh-autosuggestions
brew_install zsh-syntax-highlighting

# ---- ~/.zshrc ----
link_file "$SCRIPT_DIR/.zshrc" "$HOME/.zshrc"

ok "Zsh setup complete. Open a new terminal to pick up changes."
