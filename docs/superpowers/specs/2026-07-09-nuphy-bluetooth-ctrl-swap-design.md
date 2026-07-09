# NuPhy Bluetooth Ctrl/Cmd swap — design

**Date:** 2026-07-09
**Problem:** Outside the VDI, Windows-style copy/paste (physical `Ctrl+C` /
`Ctrl+V`) only works when the NuPhy is connected via the 2.4G dongle. Over
Bluetooth the Karabiner swap rule does not match, so the user must press the
opt-legend key (which sends the Win/GUI code = macOS Command in Windows
mode) to copy. Inside the VDI everything already works and must not change.

**Goal:** Physical `Ctrl+C`/`Ctrl+V` copies/pastes on the Mac (outside
Citrix) on **both** connections — 2.4G dongle and Bluetooth. Keyboard stays
in Windows mode; no NuPhy hardware/firmware change.

## Root cause

The rule `NuPhy (2.4G dongle, Windows mode): Ctrl/Cmd swap outside Citrix`
in `citrix-vdi/karabiner-citrix.json` has a `device_if` condition matching
only the dongle (`vendor_id 6645, product_id 4136`). The Bluetooth
connection enumerates as `vendor_id 2007` (no stable product id) and is
never matched.

## Rejected approaches

- **NuPhy-side remap (VIA/onboard):** keyboard cannot know Citrix window
  focus; a hardware Ctrl↔Win swap would leak inside the VDI and break
  Ctrl+C there.
- **macOS System Settings per-device modifier swap:** applies system-wide
  including inside Citrix; previously tried and it corrupts Scancode mode
  in the VDI.

## Design

1. **Rule change** (`citrix-vdi/karabiner-citrix.json`): add
   `{"vendor_id": 2007}` as a second identifier to the `device_if`
   condition of both manipulators in the swap rule. `device_if` matches if
   any identifier matches. Rename the rule to
   `NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl/Cmd swap outside Citrix`.
2. **Apply:** copy to the Karabiner assets folder (setup.sh path) and
   replace the old enabled copy of the rule inside
   `~/.config/karabiner/karabiner.json` (backup first). Karabiner
   auto-reloads. The Bluetooth device entry (vendor 2007) must have
   "Modify events" ON — it currently is (no `ignore: true`).
3. **Docs:** update `citrix-vdi/README.md` — NuPhy setup steps (dongle no
   longer mandatory, Modify events ON for both entries), behavior matrix
   heading, and soften the "cannot grab over Bluetooth" note to a
   troubleshooting fallback.
4. **Memory:** update the `citrix-vdi-keyboard-context` memory after the
   change is verified.

## Risk & rollback

An earlier session observed Karabiner dropping all events when grabbing
the Bluetooth connection ("grabbed keys stop flowing"). The current config
already has Modify events ON for vendor 2007 and typing works, so the note
is likely stale — but if keys stop flowing over Bluetooth after this
change: set Modify events OFF for the vendor 2007 entry in Karabiner →
Settings → Devices (or restore the karabiner.json backup) and fall back to
the dongle. The MacBook built-in keyboard is unaffected and always usable
for recovery.

## Test plan

- Bluetooth, outside VDI: `Ctrl+C`/`Ctrl+V` copies/pastes; `Win`-legend key
  acts as Control.
- Bluetooth, inside VDI: `Ctrl+C`/`Ctrl+V` still native Ctrl; `Win`-legend
  key now acts as Alt (matches dongle behavior matrix).
- Dongle: unchanged behavior both inside and outside.
- Typing over Bluetooth keeps flowing (regression check for the old grab
  bug).
