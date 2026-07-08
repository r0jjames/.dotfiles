# citrix-vdi keyboard fix design

## Problem

On a Mac running Citrix Workspace to reach a Windows VDI, JetBrains/VS Code
shortcuts that use the F-row (e.g. `Alt+F1` "Select In", `Alt+F7` "Find Usages",
`Shift+F6` "Rename") don't reach the remote IDE. The same shortcuts work when
the VDI is used from a Windows laptop.

Two failure layers:

1. **Mac F-row sends media codes** — F1 is brightness-down, not F1, so
   `Alt+F1` never leaves the Mac as an F-key chord.
2. **Citrix Option/Alt mapping** — the Option key must be configured to send
   Alt; this lives in Citrix Workspace preferences (GUI-only, not scriptable).

## Goal

Windows shortcuts work inside the VDI from the Mac, with **zero behavior
change outside the VDI** (brightness/volume keys keep working everywhere
else) and **zero changes inside the VDI** (JetBrains keymaps stay stock
Windows — same muscle memory as the Windows laptop).

## Where everything runs

**All setup happens on the Mac personal laptop.** Nothing is installed or
configured inside the Windows VDI. The README states this explicitly at the
top and on each step.

## Approach

New per-tool folder following repo conventions (mac-only guard,
`lib/common.sh`, idempotent):

```
citrix-vdi/
├── setup.sh                  # idempotent installer (runs on the Mac)
├── karabiner-citrix.json     # Karabiner complex-modification rule
└── README.md                 # manual steps + diagnostics (all on the Mac)
```

### setup.sh

Follows the `iterm2/setup.sh` pattern:

1. `detect_os`; skip with message unless macOS.
2. `ensure_brew`; `brew_install karabiner-elements --cask` (skip if the app
   is already in `/Applications`).
3. Copy `karabiner-citrix.json` into
   `~/.config/karabiner/assets/complex_modifications/` (mkdir -p, diff-check
   before copy, like the iTerm2 dynamic profile). We copy to the assets
   folder rather than editing `karabiner.json` directly because Karabiner
   rewrites that file at runtime; the trade-off is a one-time manual enable
   in the Karabiner GUI, documented in the README.
4. Completion message pointing at the README for the manual steps
   (Karabiner rule enable, Input Monitoring permission, Citrix preferences).

### karabiner-citrix.json

One complex-modification rule:

- **Condition:** `frontmost_application_if` with bundle identifier
  `com.citrix.receiver.icaviewer.mac` (the Citrix Viewer session window).
- **Mappings:** each F-row media key (`display_brightness_decrement`,
  `display_brightness_increment`, `mission_control`, `launchpad`/`spotlight`,
  `dictation`, `f6`-row variants, `rewind`, `play_or_pause`, `fast_forward`,
  `mute`, `volume_decrement`, `volume_increment`) remapped to the
  corresponding `f1`–`f12` key code, passing modifiers through
  (`modifiers.optional: any`) so `Alt+F1`, `Ctrl+Alt+F7`, `Shift+F6` all
  transmit intact.
- No global `fnState` change; outside Citrix the F-row stays media keys.

### README.md

Every section starts with a **"Run on: Mac"** marker (nothing runs inside
the VDI).

1. **What this fixes and where to run it** — explicit note: all steps on the
   Mac personal laptop, nothing inside the Windows VDI.
2. **Automated part** — `./install.sh citrix-vdi` (on the Mac).
3. **One-time manual steps (Mac):**
   - Open Karabiner-Elements → grant Input Monitoring permission when
     prompted → Complex Modifications → Add rule → enable the
     "Citrix VDI F-keys" rule.
   - Citrix Workspace preferences → Keyboard: set Option (Alt) to send Alt;
     review Command-key handling.
4. **Diagnostic (inside the VDI session, no changes made):** in IntelliJ try
   `Alt+Enter` (letter chord) vs `Alt+F1` (F-row chord).
   - Both fail → Citrix Option/Alt preference is wrong (step 3b).
   - Only `Alt+F1` fails → F-row mapping not active (Karabiner rule not
     enabled or missing permission).
5. **macOS shortcut conflicts** — shortcuts macOS intercepts before Citrix
   sees them (Mission Control Ctrl+Arrow keys, Spotlight Cmd+Space, etc.)
   with System Settings paths to disable them if needed.

### install.sh registration

Add `citrix-vdi` to `ALL_TOOLS` and `MAC_ONLY` arrays.

## Testing

1. `./install.sh citrix-vdi` twice — second run reports all ok/skip
   (idempotency).
2. Enable the rule in Karabiner, open the Citrix VDI session, and in
   IntelliJ/PyCharm verify `Alt+F1` opens the Select In popup and `Alt+F7`
   finds usages.
3. Outside Citrix (Finder/browser focused) verify brightness and volume
   keys still act as media keys.

## Out of scope

- Any configuration inside the Windows VDI (JetBrains keymaps stay stock).
- Windows laptop workflow (already works; unchanged).
- VS Code-specific keybindings — the fix is at the key-transmission layer,
  so it covers all IDEs at once.
