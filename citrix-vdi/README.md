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
2. Citrix Workspace must be told to send Alt when you press Option — a
   GUI-only preference.

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

- **"Send Alt character using"**: default is `⌘⌥ Command (left)-Option`,
  which means plain Option does NOT send Alt. Change it to the **⌥ Option**
  variant if the dropdown offers one.
- **Uncheck "Send F1 - F12 keys with ⌥ Option and the corresponding keypad
  keys"** — Citrix's own F-key emulation hijacks Option+key combos and
  fights both the Karabiner rule and Option-as-Alt.
- If the dropdown has no plain-Option choice: set **Keyboard input mode →
  Scancode** (instead of Automatic). Scancode mode sends raw PC scancodes —
  Option physically becomes Alt, Command becomes the Windows key, and the
  whole "Unicode mode" shortcut section stops applying.
- **Disconnect and reconnect the VDI session** after changing these.

Exact labels vary by Citrix Workspace version; the intent is: **Option must
reach the VDI as Alt**.

### 4. NuPhy external keyboard (one time) — *run on: Mac*

Karabiner cannot reliably grab the NuPhy over Bluetooth (with "Modify
events" on, its keys stop reaching Citrix correctly), so the NuPhy is
configured *outside* Karabiner:

1. **Karabiner-Elements → Settings → Devices**: leave **Modify events OFF**
   for the NuPhy. Karabiner rules never apply to it — that's intended.
2. Keep the NuPhy in **Windows mode permanently** (no more mode
   switching). Inside the VDI its Cmd-position key sends Alt natively.
3. **System Settings → Keyboard → Keyboard Shortcuts → Modifier Keys**,
   select the NuPhy in the keyboard dropdown, then swap:
   - **Control (⌃) key → ⌘ Command**
   - **Command (⌘) key → ⌃ Control**

   Result: the Ctrl-position key copies/pastes on the Mac (Windows feel)
   and still acts as Ctrl inside the VDI, because the Citrix preference
   "Send Control character using ⌘ Command (left)" converts it back.

## Diagnostic — *performed inside the VDI session (changes nothing there)*

In IntelliJ/PyCharm inside the VDI:

| Test | Works? | Meaning |
|---|---|---|
| `Alt+Enter` (letter chord) | no | Citrix Option→Alt preference wrong → redo step 3 |
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
