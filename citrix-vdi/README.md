# citrix-vdi — Windows IDE shortcuts from a Mac through Citrix

Fixes JetBrains/VS Code shortcuts that use the F-row (`Alt+F1` Select In,
`Alt+F7` Find Usages, `Shift+F6` Rename, …) not reaching a Windows VDI when
connecting from a Mac with Citrix Workspace.

> **Where does all of this run? On your Mac personal laptop.**
> Nothing in this folder is installed or configured inside the Windows VDI.
> Your JetBrains keymap inside the VDI stays stock Windows — same shortcuts
> as when you use the VDI from a Windows laptop.

## Why it breaks on a Mac

1. The Mac F-row sends media codes by default (F1 = brightness down), so
   `Alt+F1` never leaves the Mac as an F-key chord.
2. Citrix's default (Unicode) keyboard mode maps Mac modifiers to Windows
   ones through preferences that, in some Citrix versions, offer no way to
   send a one-key Alt — fixed by switching to Scancode input mode (a
   GUI-only preference).

The fix maps F1–F12 to real function keys **only while the Citrix Viewer
window is focused** (via a Karabiner-Elements rule). Brightness/volume keys
keep working everywhere else on the Mac.

## Setup

### 1. Automated part — *run on: Mac*

```sh
./install.py install citrix-vdi
```

Installs Karabiner-Elements (Homebrew cask) and copies **two** rule files to
`~/.config/karabiner/assets/complex_modifications/`:

- `karabiner-citrix.json` — the **base package** (F-keys, Left-Cmd-as-Alt).
  Needed in every mode, on every keyboard.
- `karabiner-nuphy-windows-mode.json` — the **NuPhy Windows-mode-extra
  package** (Ctrl/Cmd swap, Ctrl+Arrow desktop-switch fix). Only needed
  while the NuPhy is in Windows mode outside Citrix.

### 2. Set up two Karabiner profiles (one time) — *run on: Mac*

You'll keep two Karabiner-Elements profiles and switch between them
whenever you flip the NuPhy's hardware Win/Mac switch. First launch:
approve the system prompts, including **Privacy & Security → Input
Monitoring** for `karabiner_grabber`.

**"NuPhy Windows mode" profile** (rename your current default profile to
this — Karabiner-Elements → Settings → Profiles → double-click the name):

1. **Complex Modifications → Add predefined rule** → enable all 4 rules:
   - "Citrix VDI: F1-F12 as function keys (with any modifiers)"
   - "Citrix VDI: Left Command as Alt (all keyboards)"
   - "NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl/Cmd swap outside Citrix"
   - "NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl+Left/Right switches desktop outside Citrix"
2. **Devices** tab: **Modify events ON** for both NuPhy entries — dongle
   (vendor id 6645) and Bluetooth (vendor id 2007).

**"NuPhy Mac mode" profile** (Settings → Profiles → **Add profile**, or
duplicate the Windows-mode profile and trim it — duplicating is faster
since Modify-events settings carry over):

1. **Complex Modifications**: enable only the 2 base rules — "Citrix VDI:
   F1-F12 as function keys" and "Citrix VDI: Left Command as Alt". Leave
   the 2 NuPhy Windows-mode rules disabled (or remove them if you
   duplicated from the Windows-mode profile).
2. **Devices** tab: **Modify events ON** for both NuPhy entries, same as
   above — the base rules still need to see the device.

> Enabled rules are a copy — if this repo's rule files change later,
> re-run the installer, then remove and re-add the affected rules in each
> profile to pick up the new version.

### Switching NuPhy mode — *run on: Mac, every time you flip modes*

Two flicks, done together:

1. **NuPhy hardware switch** (bottom of the keyboard, or `Fn`+`Win/Cmd`
   depending on firmware) → Win or Mac.
2. **Karabiner-Elements menu-bar icon** → select the matching profile:
   "NuPhy Windows mode" or "NuPhy Mac mode".

Mismatched state (e.g. NuPhy in Mac mode but the "Windows mode" profile
still active) re-triggers the double-swap bug this setup fixes — Ctrl/Cmd
will feel backwards outside Citrix. If that happens, just switch the
profile to match.

### 3. Citrix Workspace keyboard preferences (one time) — *run on: Mac*

In **Citrix Workspace app → Preferences (⌘,) → Keyboard**:

- Set **Keyboard input mode → Scancode** (instead of Automatic). Scancode
  mode sends raw PC scancodes: the Option key physically becomes Alt,
  Command becomes the Windows key, Control stays Control, and the entire
  "Unicode mode" shortcut section stops applying. This matters because some
  Citrix versions offer no plain-Option choice for "Send Alt character
  using" — in Unicode mode Alt would need a two-key chord.
- **Disconnect and reconnect the VDI session** after changing this.

### 4. NuPhy external keyboard — *run on: Mac*

Works over the **2.4G dongle** and **Bluetooth** (the swap rule matches
both; a wired USB-C cable is not covered by the rule):

1. Connect the NuPhy via its **2.4G dongle** or **Bluetooth**.
2. Pick your mode per the "Switching NuPhy mode" section above:
   - **Windows mode** (needed inside Citrix; optional default outside
     Citrix too) — the Karabiner "NuPhy Windows mode" profile's swap rule
     makes the Ctrl-position key act as Cmd and the Win-position key act
     as Ctrl outside Citrix (Windows-style copy/paste on the Mac), plus
     bare `Ctrl+←/→` keeps working as macOS desktop/Space switching.
     Inside Citrix the layout is natively correct in Scancode mode either
     way: Ctrl-position = Ctrl, Cmd-position = Alt.
   - **Mac mode** — the keyboard already sends native Mac modifier codes
     outside Citrix, so the "NuPhy Mac mode" profile needs no swap rule at
     all: Ctrl-position = Ctrl, Option-position = Option, Cmd-position =
     Cmd, all standard. Inside Citrix, the base package's "Left Command as
     Alt" rule still turns the Cmd-position key into Alt, matching the
     Windows-mode experience.
3. **No macOS modifier swap**: System Settings → Keyboard → Keyboard
   Shortcuts → Modifier Keys must be at defaults for the NuPhy (a global
   swap there poisons Scancode mode inside the VDI, in either NuPhy mode).

## What gets installed where — *on: Mac*

Everything the setup (automated + manual steps) leaves on the Mac, and what
removes it:

| Location | What / written by | Removed by |
|---|---|---|
| `/Applications/Karabiner-Elements.app` (+ background services and the virtual keyboard driver) | Homebrew cask, installed by the installer | manual, optional (see Uninstall step 3) |
| `~/.config/karabiner/assets/complex_modifications/karabiner-citrix.json` + `karabiner-nuphy-windows-mode.json` | base + NuPhy-Windows-mode-extra rule files copied by the installer | `./install.py uninstall citrix-vdi` |
| `~/.config/karabiner/karabiner.json` — `profiles[*].complex_modifications.rules` | 2 rules in the "NuPhy Mac mode" profile, 4 in the "NuPhy Windows mode" profile, copied in when you enable them in the GUI (setup step 2) | `./install.py uninstall citrix-vdi` |
| `~/.config/karabiner/karabiner.json` — `profiles[*].name` | the two profile names themselves ("NuPhy Windows mode", "NuPhy Mac mode") | manual, Karabiner-Elements → Settings → Profiles |
| `~/.config/karabiner/karabiner.json` — per-device settings | "Modify events" toggles for the NuPhy entries (setup step 2) | nothing — harmless without rules, or reset in the GUI |
| `~/Library/Application Support/Citrix Receiver/Config` — `KeyboardInputMode=Scancode` | Citrix Workspace preferences GUI (setup step 3) | manual, GUI only (Uninstall step 1) |

## Expected behavior once set up

Consistent rule of thumb on both keyboards: **Ctrl-position key = shortcuts
(copy/paste), key next to the spacebar = Alt inside the VDI.**

### NuPhy (Windows mode, 2.4G dongle or Bluetooth)

| Key (by its Windows legend) | Outside VDI (Mac) | Inside VDI (Windows) |
|---|---|---|
| `Ctrl` | ⌘ Command — Ctrl+C/V copies, Ctrl+Tab switches apps; bare Ctrl+←/→ stays desktop/Space switch (end/start of line: use Home/End) | Ctrl (native) — Ctrl+C/V, Ctrl+Shift+F, … |
| `Win` | ⌃ Control — terminal interrupt, Mission Control combos | Alt (via Karabiner rule; Start menu via mouse) |
| `Alt` (next to space) | ⌥ Option | Alt (native) — Alt+F1, Alt+Enter, Alt+F7 |
| `F1`–`F12` | as the keyboard sends them | F1–F12 |

### MacBook built-in keyboard

| Key | Outside VDI (Mac) | Inside VDI (Windows) |
|---|---|---|
| `⌃ Control` | Control (standard Mac) | Ctrl — Ctrl+C/V, Ctrl+Shift+F, … |
| `⌥ Option` | Option (standard Mac) | Alt (Scancode mode, native) |
| `⌘ Command` (left) | Command (standard Mac) | Alt (via Karabiner rule) — Cmd+1, Cmd+F1 = Alt+1, Alt+F1 |
| `⌘ Command` (right) | Command | Windows key |
| F-row | media keys (brightness/volume) | real F1–F12 (via Karabiner rule) |

Outside the VDI the MacBook is 100% standard Mac — nothing changes.

## Uninstall — revert everything to normal

All on the Mac; nothing to undo inside the VDI.

### Automated part — *run on: Mac*

```sh
./install.py uninstall citrix-vdi
```

Removes the enabled "Citrix VDI"/"NuPhy" rules (from both the base and
NuPhy-Windows-mode-extra packages) from every profile in
`~/.config/karabiner/karabiner.json` (after backing it up to
`karabiner.json.bak-YYYY-MM-DD`; Karabiner picks up the change
automatically) and deletes both rule files from the assets folder. Safe to
rerun.

### Manual part — *on: Mac*

1. **Citrix**: Preferences → Keyboard → Keyboard input mode → **Automatic**
   (or press *Restore Defaults* to reset the whole pane). Reconnect the
   session.
2. **NuPhy**: free to use any mode (Mac/Windows) and any connection
   (Bluetooth/dongle/cable) again.
3. **Karabiner profiles**: delete the 'NuPhy Windows mode' and 'NuPhy Mac mode' profiles if you no longer want them (Karabiner-Elements → Settings → Profiles).
4. **Karabiner-Elements itself** (only if you don't use it for anything
   else): Karabiner-Elements → Settings → scroll to the uninstall section
   and use its own uninstaller (removes the virtual keyboard driver
   properly), or:
   ```sh
   brew uninstall --cask karabiner-elements
   ```
5. Repo side: remove `citrix_vdi` from `lib/tools/__init__.py` and delete
   `lib/tools/citrix_vdi.py` + the `citrix-vdi/` folder if you want it gone
   from the dotfiles too.

## Diagnostic — *performed inside the VDI session (changes nothing there)*

In IntelliJ/PyCharm inside the VDI:

| Test | Works? | Meaning |
|---|---|---|
| `Alt+Enter` (letter chord) | no | Alt not reaching the VDI → Scancode mode not set or session not reconnected (step 3) |
| `Alt+Enter` yes, `Alt+F1` no | — | F-row rule not active → redo step 2 (rule enabled? Input Monitoring granted?) |
| Both yes | — | Done. `Alt+F1, 1` opens Project view Select In |

## macOS shortcuts that can still steal keys — *run on: Mac*

macOS handles these before Citrix sees them. Disable only the ones you
actually need inside the VDI (System Settings → Keyboard → Keyboard
Shortcuts):

| Shortcut | macOS default | Where to disable |
|---|---|---|
| `Ctrl+←` / `Ctrl+→` | Mission Control space switch | Mission Control |
| `Ctrl+↑` / `Ctrl+↓` | Mission Control / App windows | Mission Control |
| `Cmd+Space` | Spotlight | Spotlight |
| `Ctrl+Space` | Input source switch (if enabled) | Input Sources |

## Verify outside the VDI — *run on: Mac*

With Finder or a browser focused, brightness (F1/F2) and volume (F10–F12)
keys must still act as media keys. The Karabiner rule only fires while the
Citrix Viewer window is frontmost.
