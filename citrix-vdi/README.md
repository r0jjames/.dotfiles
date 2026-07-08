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

### 3. Citrix Workspace keyboard preferences (one time) — *run on: Mac*

In **Citrix Workspace app → Preferences (⌘,) → Keyboard**:

- **"Send Alt using"** (or "Left Option key"): set so Option sends **Alt**.
- Review the Command-key setting — leave it as **Command (Windows key)**
  unless you want Cmd shortcuts forwarded differently.

Exact labels vary by Citrix Workspace version; the intent is: **Option must
reach the VDI as Alt**.

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
