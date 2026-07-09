# citrix-vdi uninstall script — design

Date: 2026-07-09
Status: approved

## Goal

One script that reverts the automatable parts of the citrix-vdi setup on the
Mac, plus README documentation of the full install footprint (what lands
where) so the manual leftovers are obvious.

## Scope decision (approved)

- Script removes: the rule file in the Karabiner assets folder AND the three
  enabled Citrix/NuPhy rules inside `~/.config/karabiner/karabiner.json`
  (with a dated backup first).
- Script does NOT remove: Karabiner-Elements app, device "Modify events"
  toggles, Citrix Workspace preference, NuPhy hardware state. These are
  printed as manual follow-ups.
- Structure: single `citrix-vdi/uninstall.sh`, run directly. No top-level
  uninstall dispatcher (YAGNI — only one tool needs uninstall).

## Components

### `citrix-vdi/uninstall.sh`

Mirrors `setup.sh` conventions: `set -e`, sources `lib/common.sh`,
`detect_os`, macOS-only guard, idempotent (rerun-safe, every step no-ops
with `ok`/`skip` when nothing to do).

Steps:

1. **Backup** `~/.config/karabiner/karabiner.json` to
   `karabiner.json.bak-YYYY-MM-DD` (same dating convention as `link_file`).
   Skip if config missing.
2. **Strip enabled rules** via inline python3: read `description` values
   from the repo's `karabiner-citrix.json` (no hardcoded list — no drift),
   remove matching rules from `profiles[*].complex_modifications.rules` in
   the live config, report count removed. Karabiner auto-reloads the file;
   no restart needed. Warn and point to GUI steps if python3 missing.
3. **Delete rule file**
   `~/.config/karabiner/assets/complex_modifications/karabiner-citrix.json`
   (`rm -f`).
4. **Print manual steps**: Citrix Preferences → Keyboard → input mode back
   to Automatic + reconnect session; NuPhy free to use any mode/connection;
   optional Karabiner-Elements removal (its own uninstaller preferred, or
   `brew uninstall --cask karabiner-elements`).

### README updates

1. New section "**What gets installed where**" — full install footprint on
   the Mac:
   - `/Applications/Karabiner-Elements.app` + its services and virtual
     keyboard driver (Homebrew cask).
   - `~/.config/karabiner/assets/complex_modifications/karabiner-citrix.json`
     — rule file copied by `setup.sh`.
   - `~/.config/karabiner/karabiner.json` — enabled rules copied into
     `profiles[*].complex_modifications.rules` by the GUI, plus per-device
     "Modify events" settings (NuPhy dongle vendor id 6645).
   - `~/Library/Application Support/Citrix Receiver/Config` —
     `KeyboardInputMode=Scancode` written by Citrix Workspace preferences
     (GUI-managed; not touched by any script).
2. Uninstall section rewritten: script covers rule removal (old manual
   steps 1–2), remaining manual steps kept.

## Error handling

`set -e` throughout; missing files/tools degrade to `skip`/`warn` with
pointer to the manual GUI steps, never a hard failure on a clean machine.

## Testing

Run `./citrix-vdi/uninstall.sh` on the live machine: verify the three rules
are gone from `karabiner.json`, assets file deleted, backup created. Rerun
to confirm idempotency. Restore state afterwards (backup file back in
place, re-run `setup.sh`).
