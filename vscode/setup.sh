#!/usr/bin/env bash
# VS Code: settings, keybindings, extensions.
#   macOS          — symlinks into ~/Library/Application Support/Code/User
#   Windows (Git Bash) — copies into $APPDATA/Code/User (symlinks need admin there)
#   WSL            — VS Code lives on the Windows host; run this from Git Bash instead
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

# Own platform detection: unlike other tools, this one also runs on Git Bash.
case "$(uname -s)" in
  Darwin)
    TARGET_DIR="$HOME/Library/Application Support/Code/User"
    MODE="link"
    ;;
  MINGW*|MSYS*)
    if [ -z "${APPDATA:-}" ]; then
      warn "APPDATA not set; cannot locate VS Code user dir."
      exit 1
    fi
    TARGET_DIR="$APPDATA/Code/User"
    MODE="copy"
    ;;
  Linux)
    if is_wsl; then
      skip "In WSL, VS Code runs on the Windows host. Run this script from Git Bash on Windows instead (see vscode/README.md)."
    else
      skip "No VS Code target on plain Linux configured. Skipping."
    fi
    exit 0
    ;;
  *)
    warn "Unsupported platform: $(uname -s)"
    exit 1
    ;;
esac

# copy_file <src> <target> : copy with dated backup, skip when identical.
copy_file() {
  local src="$1" target="$2"
  if diff -q "$src" "$target" &>/dev/null; then
    ok "$target already up to date."
    return 0
  fi
  mkdir -p "$(dirname "$target")"
  if [ -f "$target" ]; then
    local backup="$target.bak-$(date +%Y-%m-%d)"
    [ -e "$backup" ] || cp "$target" "$backup"
  fi
  cp "$src" "$target"
  ok "Copied $src -> $target"
}

info "Applying VS Code settings + keybindings ($MODE)..."
for f in settings.json keybindings.json; do
  if [ "$MODE" = "link" ]; then
    link_file "$SCRIPT_DIR/$f" "$TARGET_DIR/$f"
  else
    copy_file "$SCRIPT_DIR/$f" "$TARGET_DIR/$f"
  fi
done

# ---- Extensions ----
if ! command -v code &>/dev/null; then
  warn "'code' CLI not found — skipping extension install."
  warn "In VS Code: Cmd/Ctrl+Shift+P -> 'Shell Command: Install code command in PATH', then re-run."
  exit 0
fi

info "Installing extensions (skipping already installed)..."
INSTALLED="$(code --list-extensions | tr '[:upper:]' '[:lower:]')"
while IFS= read -r ext; do
  # strip comments/blank lines
  ext="${ext%%#*}"
  ext="$(echo "$ext" | tr -d '[:space:]')"
  [ -z "$ext" ] && continue
  if echo "$INSTALLED" | grep -qx "$(echo "$ext" | tr '[:upper:]' '[:lower:]')"; then
    ok "$ext already installed."
  else
    info "Installing $ext..."
    code --install-extension "$ext" || warn "Failed to install $ext (continuing)."
  fi
done < "$SCRIPT_DIR/extensions.txt"

ok "VS Code setup complete. Reload VS Code to pick up everything."
