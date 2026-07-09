#!/usr/bin/env bash
# Citrix VDI uninstall (macOS only): removes the Karabiner rule file and the
# enabled Citrix/NuPhy rules from the live Karabiner config. Leaves
# Karabiner-Elements itself, Citrix preferences, and the NuPhy alone —
# manual follow-ups are printed at the end. See citrix-vdi/README.md.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os

if [ "$DOTFILES_OS" != "macos" ]; then
  skip "citrix-vdi is macOS-only, nothing to uninstall."
  exit 0
fi

KARABINER_CONFIG="$HOME/.config/karabiner/karabiner.json"
ASSETS_FILE="$HOME/.config/karabiner/assets/complex_modifications/karabiner-citrix.json"
RULES_FILE="$SCRIPT_DIR/karabiner-citrix.json"

# ---- 1. Remove enabled rules from the live Karabiner config ----
if [ ! -f "$KARABINER_CONFIG" ]; then
  skip "No $KARABINER_CONFIG — no enabled rules to remove."
elif ! command -v python3 &>/dev/null; then
  warn "python3 not found. Remove the rules manually: Karabiner-Elements ->"
  warn "Complex Modifications -> delete the 'Citrix VDI'/'NuPhy' rules."
else
  backup="$KARABINER_CONFIG.bak-$(date +%Y-%m-%d)"
  if [ ! -e "$backup" ]; then
    info "Backing up $KARABINER_CONFIG -> $backup"
    cp "$KARABINER_CONFIG" "$backup"
  fi
  removed=$(python3 - "$RULES_FILE" "$KARABINER_CONFIG" <<'PY'
import json, sys

rules_file, config_file = sys.argv[1], sys.argv[2]
with open(rules_file) as f:
    ours = {r["description"] for r in json.load(f)["rules"]}
with open(config_file) as f:
    config = json.load(f)

removed = 0
for profile in config.get("profiles", []):
    rules = profile.get("complex_modifications", {}).get("rules", [])
    kept = [r for r in rules if r.get("description") not in ours]
    removed += len(rules) - len(kept)
    if len(kept) != len(rules):
        profile["complex_modifications"]["rules"] = kept

if removed:
    with open(config_file, "w") as f:
        json.dump(config, f, indent=4)
        f.write("\n")
print(removed)
PY
)
  if [ "$removed" -gt 0 ]; then
    ok "Removed $removed enabled rule(s) from karabiner.json (Karabiner reloads automatically)."
  else
    ok "No Citrix/NuPhy rules enabled in karabiner.json."
  fi
fi

# ---- 2. Remove the rule file from the assets folder ----
if [ -f "$ASSETS_FILE" ]; then
  rm -f "$ASSETS_FILE"
  ok "Removed $ASSETS_FILE"
else
  ok "Rule file already absent from assets folder."
fi

# ---- 3. Manual follow-ups ----
echo ""
ok "citrix-vdi uninstall complete. Remaining manual steps:"
echo "  1. Citrix Workspace -> Preferences -> Keyboard -> Keyboard input mode"
echo "     -> Automatic (then disconnect and reconnect the VDI session)."
echo "  2. NuPhy: free to use any mode (Mac/Windows) and any connection"
echo "     (Bluetooth/dongle/cable) again."
echo "  3. Optional, only if you don't use Karabiner-Elements for anything else:"
echo "     Karabiner-Elements -> Settings -> uninstall section (preferred), or"
echo "     brew uninstall --cask karabiner-elements"
