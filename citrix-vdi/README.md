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
./install.sh citrix-vdi
```

Installs Karabiner-Elements (Homebrew cask) and copies the rule file to
`~/.config/karabiner/assets/complex_modifications/`.

### 2. Enable the Karabiner rule (one time) — *run on: Mac*

1. Open **Karabiner-Elements** (first launch: approve the system prompts,
   including **Privacy & Security → Input Monitoring** for
   `karabiner_grabber`).
2. Go to **Complex Modifications → Add predefined rule**.
3. Enable **"Citrix VDI: F1-F12 as function keys (with any modifiers)"**.
4. Enable **"Citrix VDI: Left Command as Alt (all keyboards)"** — makes the
   key next to the spacebar send Alt inside the VDI on the MacBook
   keyboard. Right Command still sends the Windows key. (Despite the name,
   it only affects keyboards Karabiner grabs — see the NuPhy section for
   why the external keyboard is handled differently.)

> Enabled rules are a copy — if this repo's rule file changes later, re-run
> the installer, then remove and re-add the rules in Karabiner to pick up
> the new version.

### 3. Citrix Workspace keyboard preferences (one time) — *run on: Mac*

In **Citrix Workspace app → Preferences (⌘,) → Keyboard**:

- Set **Keyboard input mode → Scancode** (instead of Automatic). Scancode
  mode sends raw PC scancodes: the Option key physically becomes Alt,
  Command becomes the Windows key, Control stays Control, and the entire
  "Unicode mode" shortcut section stops applying. This matters because some
  Citrix versions offer no plain-Option choice for "Send Alt character
  using" — in Unicode mode Alt would need a two-key chord.
- **Disconnect and reconnect the VDI session** after changing this.

### 4. NuPhy external keyboard (one time) — *run on: Mac*

Karabiner cannot grab the NuPhy over **Bluetooth** (grabbed keys stop
flowing), but works fine over the **2.4G dongle** or USB cable:

1. Connect the NuPhy via its **2.4G dongle** (or cable) — permanently.
2. Keep the NuPhy in **Windows mode permanently** (no mode switching).
   Inside the VDI the layout is then natively correct in Scancode mode:
   Ctrl-position = Ctrl, Cmd-position = Alt.
3. **Karabiner-Elements → Settings → Devices**: **Modify events ON** for
   the dongle entry (vendor id 6645); **OFF** for the Bluetooth entry
   (vendor id 2007) if it appears.
4. **Complex Modifications**: enable **"NuPhy (2.4G dongle, Windows mode):
   Ctrl/Cmd swap outside Citrix"**. Outside the VDI this makes the
   Ctrl-position key act as Cmd (Windows-style copy/paste on the Mac) and
   the Win-position key act as Ctrl.
5. **No macOS modifier swap**: System Settings → Keyboard → Keyboard
   Shortcuts → Modifier Keys must be at defaults for the NuPhy (a global
   swap there poisons Scancode mode inside the VDI).

## Expected behavior once set up

Consistent rule of thumb on both keyboards: **Ctrl-position key = shortcuts
(copy/paste), key next to the spacebar = Alt inside the VDI.**

### NuPhy (Windows mode, 2.4G dongle)

| Key (by its Windows legend) | Outside VDI (Mac) | Inside VDI (Windows) |
|---|---|---|
| `Ctrl` | ⌘ Command — Ctrl+C/V copies, Ctrl+Tab switches apps | Ctrl (native) — Ctrl+C/V, Ctrl+Shift+F, … |
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

1. **Karabiner rules**: Karabiner-Elements → Complex Modifications → Remove
   all three "Citrix VDI"/"NuPhy" rules.
2. **Rule file**:
   ```sh
   rm ~/.config/karabiner/assets/complex_modifications/karabiner-citrix.json
   ```
3. **Karabiner-Elements itself** (only if you don't use it for anything
   else): Karabiner-Elements → Settings → scroll to the uninstall section
   and use its own uninstaller (removes the virtual keyboard driver
   properly), or:
   ```sh
   brew uninstall --cask karabiner-elements
   ```
4. **Citrix**: Preferences → Keyboard → Keyboard input mode → **Automatic**
   (or press *Restore Defaults* to reset the whole pane). Reconnect the
   session.
5. **NuPhy**: free to use any mode (Mac/Windows) and any connection
   (Bluetooth/dongle/cable) again.
6. Repo side: remove `citrix-vdi` from `ALL_TOOLS`/`MAC_ONLY` in
   `install.sh` and delete the `citrix-vdi/` folder if you want it gone
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
