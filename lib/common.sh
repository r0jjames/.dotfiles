#!/usr/bin/env bash
# Shared helpers for all setup scripts. Source this file; do not execute it.
#   source "$(dirname "$0")/../lib/common.sh"

# ---- Logging ----
info() { echo "📦 $*"; }
ok()   { echo "✅ $*"; }
skip() { echo "⏭️  $*"; }
warn() { echo "⚠️  $*"; }

# ---- OS detection ----
# Sets DOTFILES_OS to "macos" or "linux".
detect_os() {
  case "$(uname -s)" in
    Darwin) DOTFILES_OS="macos" ;;
    Linux)  DOTFILES_OS="linux" ;;
    *)
      warn "Unsupported OS: $(uname -s). Only macOS and Linux (WSL Ubuntu) are supported."
      exit 1
      ;;
  esac
}

# True when running inside WSL.
is_wsl() {
  [ -f /proc/version ] && grep -qi microsoft /proc/version
}

# ---- Homebrew ----
# Install Homebrew if missing; make `brew` usable in the current script.
ensure_brew() {
  if command -v brew &>/dev/null; then
    return 0
  fi
  # On Linux, brew may be installed but not on PATH yet.
  if [ -x /home/linuxbrew/.linuxbrew/bin/brew ]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    return 0
  fi
  info "Installing Homebrew..."
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  if [ -x /home/linuxbrew/.linuxbrew/bin/brew ]; then
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
  elif [ -x /opt/homebrew/bin/brew ]; then
    eval "$(/opt/homebrew/bin/brew shellenv)"
  fi
  if ! command -v brew &>/dev/null; then
    warn "Homebrew install failed or brew not on PATH. See https://brew.sh"
    exit 1
  fi
}

# brew_install <pkg> [flags...] : install only if missing.
# Extra flags (e.g. --cask) are passed to `brew install`.
brew_install() {
  local pkg="$1"
  shift || true
  if brew list "$pkg" &>/dev/null; then
    ok "$pkg already installed."
  else
    info "Installing $pkg..."
    brew install "$@" "$pkg"
  fi
}

# ---- Symlinking ----
# link_file <source-in-repo> <target> : symlink target -> source.
# Skips when already linked correctly; backs up an existing real file/dir
# to <target>.bak-YYYY-MM-DD before linking.
link_file() {
  local src="$1"
  local target="$2"

  if [ ! -e "$src" ]; then
    warn "link_file: source does not exist: $src"
    return 1
  fi

  if [ -L "$target" ] && [ "$(readlink "$target")" = "$src" ]; then
    ok "$target already linked."
    return 0
  fi

  mkdir -p "$(dirname "$target")"

  if [ -e "$target" ] || [ -L "$target" ]; then
    local backup="$target.bak-$(date +%Y-%m-%d)"
    if [ -e "$backup" ] || [ -L "$backup" ]; then
      rm -rf "$target"   # already backed up today; drop the stale copy
    else
      info "Backing up $target -> $backup"
      mv "$target" "$backup"
    fi
  fi

  ln -s "$src" "$target"
  ok "Linked $target -> $src"
}
