# NuPhy Windows/Mac mode packages — design

Date: 2026-07-23
Status: approved

## Problem

The NuPhy Air75 V3 has a hardware Win/Mac mode switch. `citrix-vdi/`'s
Karabiner setup was built assuming the keyboard stays in **Windows mode
permanently** (see `citrix-vdi-keyboard-context` memory, 2026-07-08): two
rules swap Ctrl/Cmd (and fix the resulting Ctrl+Arrow desktop-switch side
effect) whenever the NuPhy is used **outside** Citrix, compensating for
Windows-mode HID output on a Mac.

Roj now also uses the NuPhy in **Mac mode** outside Citrix, where it already
sends native Mac modifier codes — the swap rules double-swap and break
Ctrl/Cmd. He wants Windows mode kept fully working (still used inside
Citrix, and he may keep using it as primary outside Citrix too), with Mac
mode available as an easy, organized switch — not a one-time migration.

## Why Karabiner profiles, not a code toggle

Karabiner-Elements' enabled complex-modification rules and per-device
"Modify events" settings are stored per **profile** in the live
`~/.config/karabiner/karabiner.json`, switchable with one click from the
menu-bar icon. This is the native mechanism for "two configurations, switch
instantly" and needs no new scripting — the repo's job is only to package
the *source* rules so enabling the right set per profile is a one-click
action instead of hand-picking from a flat mixed list (see attached
screenshot: currently all 4 rules sit undifferentiated in one Enabled Rules
list).

## Rule packaging (repo-side)

Split the existing single `citrix-vdi/karabiner-citrix.json` into two files,
avoiding duplication of shared rules:

- **`citrix-vdi/karabiner-citrix.json`** (base, trimmed) — the 2
  device-agnostic rules, needed in every mode since they apply regardless of
  NuPhy Win/Mac mode (and also cover the MacBook built-in keyboard):
  - "Citrix VDI: F1-F12 as function keys (with any modifiers)"
  - "Citrix VDI: Left Command as Alt (all keyboards)"
- **`citrix-vdi/karabiner-nuphy-windows-mode.json`** (new) — the 2
  NuPhy-specific, Windows-mode-only rules (both scoped
  `frontmost_application_unless` Citrix, `device_if` NuPhy vendor/product
  ids 6645/4136 dongle + 2007 Bluetooth):
  - "NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl/Cmd swap outside
    Citrix"
  - "NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl+Left/Right switches
    desktop outside Citrix"

No rule content changes — this is a pure file split. The Citrix-scoped
rules are untouched, so Windows-mode-inside-Citrix behavior is unaffected
either way.

## Karabiner profiles (live config, manual one-time setup)

- Rename the current default profile (already has all 4 rules enabled +
  Modify-events ON for both NuPhy device entries) to **"NuPhy Windows
  mode"**. No changes needed inside it — it already matches the desired
  Windows-mode package (base + extra).
- **Duplicate** that profile to a new one named **"NuPhy Mac mode"**, then
  in the copy disable/remove the 2 NuPhy-specific rules from the "extra"
  package, keeping the base package's 2 rules and Modify-events ON for both
  NuPhy entries (needed so the base rules still see the device).
- Daily use: toggle the NuPhy hardware Win/Mac switch and the Karabiner
  menu-bar profile switch together.

## Code changes (`lib/tools/citrix_vdi.py`)

- `_post()`: copy both source files to
  `~/.config/karabiner/assets/complex_modifications/` (was one).
- `_uninstall()`: run the existing `remove_enabled_rules(rules_file,
  config_file)` once per source file (union of descriptions removed across
  all profiles), then delete both asset files instead of one.
- `_probe()`: report installed only if both asset files match their repo
  source (`filecmp.cmp` for each).
- `remove_enabled_rules` itself is unchanged — it already takes a single
  rules file path, so calling it twice covers both packages. No test
  changes needed; `tests/test_citrix.py`'s existing coverage of the matching
  logic still applies to each call.

## README changes (`citrix-vdi/README.md`)

- Setup section: describe copying 2 files.
- Rewrite "Enable the Karabiner rule" step around the two packages and two
  profiles (base package always; Windows-mode extra package only in the
  "NuPhy Windows mode" profile).
- New **"Switching NuPhy mode"** section: one-time profile setup (rename +
  duplicate + trim) and the daily two-flick switch procedure.
- Update "What gets installed where" table: 2 asset files instead of 1;
  note that enabled rules and Modify-events are per-profile.
- Uninstall section: script now removes rules sourced from both files.

## Memory update

Update `citrix-vdi-keyboard-context` memory to record: base/extra file
split, two Karabiner profiles ("NuPhy Windows mode" / "NuPhy Mac mode"),
switch procedure. Superseded the old "NuPhy Air75 V3, Windows mode
permanently" line.

## Out of scope

- Any change to Citrix-scoped rule content or the F-key/Left-Cmd-as-Alt
  logic.
- Scripting the Karabiner profile creation/switch itself — Karabiner has no
  CLI for this; profile setup and daily switching stay manual GUI actions.
- Verifying NuPhy's actual per-mode HID output empirically — assumed
  correct from existing memory/README documentation of Windows-mode
  behavior; Mac-mode behavior should be spot-checked live (Ctrl+C/V, Alt
  chords inside Citrix) after setup, per the existing README diagnostic
  pattern.

## Testing

1. `./install.py install citrix-vdi` — verify both asset files land in
   `~/.config/karabiner/assets/complex_modifications/`, rerun for
   idempotency (existing `copy_file` diff-check behavior, unchanged).
2. Manual: set up the two profiles per the README section, confirm
   Windows-mode profile behaves exactly as before (regression check) and
   Mac-mode profile leaves Ctrl/Cmd untouched outside Citrix.
3. `./install.py uninstall citrix-vdi` — verify rules sourced from both
   files are removed from every profile in `karabiner.json`, both asset
   files deleted, rerun for idempotency.
