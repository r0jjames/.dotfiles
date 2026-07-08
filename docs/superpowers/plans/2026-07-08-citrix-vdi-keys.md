# Citrix VDI Keyboard Fix Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Windows IDE shortcuts (`Alt+F1`, `Alt+F7`, `Shift+F6`, …) work from a Mac inside a Citrix Windows VDI, with no behavior change outside the VDI and no changes inside the VDI.

**Architecture:** New `citrix-vdi/` per-tool folder (matches `iterm2/` pattern): an idempotent `setup.sh` installs Karabiner-Elements and drops a complex-modification rule into Karabiner's assets folder; the rule re-emits `f1`–`f12` as plain function keys only when the Citrix Viewer window is frontmost. A README documents the GUI-only manual steps (Karabiner rule enable, Citrix keyboard preferences) with explicit "Run on: Mac" markers.

**Tech Stack:** bash (`lib/common.sh` helpers), Homebrew cask, Karabiner-Elements complex modifications (JSON).

**Spec:** `docs/superpowers/specs/2026-07-08-citrix-vdi-keys-design.md`

## Global Constraints

- All setup runs on the Mac; nothing is installed or configured inside the Windows VDI.
- Every script must be idempotent (safe to re-run; second run reports ok/skip).
- macOS-only: `setup.sh` must `detect_os` and skip on Linux; register the tool in `MAC_ONLY` in `install.sh`.
- Follow `lib/common.sh` logging helpers (`info`/`ok`/`skip`/`warn`) — no bare `echo` for status.
- No global macOS `fnState` change — F-row stays media keys outside Citrix.
- Copy the rule to `~/.config/karabiner/assets/complex_modifications/`; never edit `~/.config/karabiner/karabiner.json` directly (Karabiner rewrites it at runtime).

**Implementation note (mechanism):** the spec describes remapping "media codes to F-keys". The proven Karabiner pattern is simpler: on Apple keyboards Karabiner receives `key_code f1`–`f12` from the hardware, and macOS applies the media translation *after* Karabiner — but only to events Karabiner has not modified. So a complex modification `f1 → f1` (condition: Citrix frontmost, modifiers optional any) bypasses the media translation exactly and only when the VDI is focused. The plan uses this `f1 → f1` form.

---

### Task 1: Karabiner rule file

**Files:**
- Create: `citrix-vdi/karabiner-citrix.json`

**Interfaces:**
- Produces: `citrix-vdi/karabiner-citrix.json` — copied verbatim by Task 2's `setup.sh`. Rule title shown in the Karabiner GUI: **"Citrix VDI: F1-F12 as function keys (with any modifiers)"**.

- [ ] **Step 1: Write the rule file**

Twelve manipulators, one per F-key. Condition matches Citrix Viewer bundle ids (`com.citrix.receiver.icaviewer.mac` is the current Citrix Workspace session window; `com.citrix.XenAppViewer` covers older installs). `"modifiers": {"optional": ["any"]}` lets `Alt+F1`, `Ctrl+Alt+F7`, `Shift+F6` pass through intact.

Create `citrix-vdi/karabiner-citrix.json`:

```json
{
  "title": "Citrix VDI: F-keys for Windows IDE shortcuts",
  "rules": [
    {
      "description": "Citrix VDI: F1-F12 as function keys (with any modifiers)",
      "manipulators": [
        {
          "type": "basic",
          "from": { "key_code": "f1", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f1" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f2", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f2" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f3", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f3" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f4", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f4" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f5", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f5" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f6", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f6" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f7", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f7" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f8", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f8" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f9", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f9" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f10", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f10" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f11", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f11" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        },
        {
          "type": "basic",
          "from": { "key_code": "f12", "modifiers": { "optional": ["any"] } },
          "to": [{ "key_code": "f12" }],
          "conditions": [
            {
              "type": "frontmost_application_if",
              "bundle_identifiers": [
                "^com\\.citrix\\.receiver\\.icaviewer\\.mac$",
                "^com\\.citrix\\.XenAppViewer$"
              ]
            }
          ]
        }
      ]
    }
  ]
}
```

- [ ] **Step 2: Validate JSON parses**

Run: `python3 -m json.tool citrix-vdi/karabiner-citrix.json > /dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 3: Verify 12 manipulators, all f1-f12 covered, from == to**

Run:

```bash
python3 - <<'EOF'
import json
rules = json.load(open('citrix-vdi/karabiner-citrix.json'))['rules'][0]['manipulators']
assert len(rules) == 12, f"expected 12 manipulators, got {len(rules)}"
keys = [m['from']['key_code'] for m in rules]
assert keys == [f'f{i}' for i in range(1, 13)], keys
for m in rules:
    assert m['to'][0]['key_code'] == m['from']['key_code']
    assert m['from']['modifiers'] == {'optional': ['any']}
    assert m['conditions'][0]['type'] == 'frontmost_application_if'
print('OK: 12 manipulators, f1-f12, modifiers optional any, Citrix-scoped')
EOF
```

Expected: `OK: 12 manipulators, f1-f12, modifiers optional any, Citrix-scoped`

- [ ] **Step 4: Commit**

```bash
git add citrix-vdi/karabiner-citrix.json
git commit -m "Add Karabiner Citrix-scoped F-key rule"
```

---

### Task 2: setup.sh

**Files:**
- Create: `citrix-vdi/setup.sh`

**Interfaces:**
- Consumes: `citrix-vdi/karabiner-citrix.json` (Task 1); `lib/common.sh` helpers `detect_os`, `ensure_brew`, `brew_install`, `info`, `ok`, `skip`.
- Produces: `citrix-vdi/setup.sh`, runnable standalone or via `install.sh` (Task 4). Installs the rule file to `~/.config/karabiner/assets/complex_modifications/karabiner-citrix.json`.

- [ ] **Step 1: Write setup.sh**

Create `citrix-vdi/setup.sh` (mode 755):

```bash
#!/usr/bin/env bash
# Citrix VDI (macOS only): Karabiner-Elements + a Citrix-scoped rule so
# Windows IDE shortcuts (Alt+F1, Alt+F7, Shift+F6, ...) reach the VDI intact.
# Runs on the Mac — nothing is installed or configured inside the VDI.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/../lib/common.sh"

detect_os

if [ "$DOTFILES_OS" != "macos" ]; then
  skip "citrix-vdi is macOS-only, skipping."
  exit 0
fi

ensure_brew

if [ -d "/Applications/Karabiner-Elements.app" ]; then
  ok "Karabiner-Elements already installed."
else
  brew_install karabiner-elements --cask
fi

# ---- Complex-modification rule (assets folder; enabled once in the GUI) ----
ASSETS_DIR="$HOME/.config/karabiner/assets/complex_modifications"
mkdir -p "$ASSETS_DIR"
if diff -q "$SCRIPT_DIR/karabiner-citrix.json" "$ASSETS_DIR/karabiner-citrix.json" &>/dev/null; then
  ok "Karabiner Citrix rule already up to date."
else
  info "Installing Karabiner Citrix rule..."
  cp "$SCRIPT_DIR/karabiner-citrix.json" "$ASSETS_DIR/karabiner-citrix.json"
fi

ok "citrix-vdi setup complete. One-time manual steps remain (Karabiner rule enable + Citrix keyboard preferences) — see citrix-vdi/README.md."
```

Then: `chmod +x citrix-vdi/setup.sh`

- [ ] **Step 2: Syntax check**

Run: `bash -n citrix-vdi/setup.sh && echo SYNTAX-OK`
Expected: `SYNTAX-OK`

- [ ] **Step 3: Run twice, verify idempotent**

Run: `bash citrix-vdi/setup.sh && echo --- && bash citrix-vdi/setup.sh`
Expected first run: installs Karabiner-Elements cask if missing (or `✅ Karabiner-Elements already installed.`), then `📦 Installing Karabiner Citrix rule...`
Expected second run: every line `✅` (already installed / already up to date), no `📦` lines.

Verify rule landed: `diff citrix-vdi/karabiner-citrix.json ~/.config/karabiner/assets/complex_modifications/karabiner-citrix.json && echo SAME`
Expected: `SAME`

- [ ] **Step 4: Commit**

```bash
git add citrix-vdi/setup.sh
git commit -m "Add citrix-vdi setup script (Karabiner install + rule copy)"
```

---

### Task 3: README.md

**Files:**
- Create: `citrix-vdi/README.md`

**Interfaces:**
- Consumes: rule title from Task 1 ("Citrix VDI: F1-F12 as function keys (with any modifiers)"); `setup.sh` behavior from Task 2.
- Produces: user-facing doc referenced by `setup.sh`'s completion message.

- [ ] **Step 1: Write README.md**

Create `citrix-vdi/README.md`:

```markdown
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
```

- [ ] **Step 2: Commit**

```bash
git add citrix-vdi/README.md
git commit -m "Add citrix-vdi README (manual steps, diagnostics, run-on-Mac markers)"
```

---

### Task 4: Register in install.sh

**Files:**
- Modify: `install.sh:13-14`

**Interfaces:**
- Consumes: `citrix-vdi/setup.sh` (Task 2) — `install.sh` requires `$tool/setup.sh` to exist.
- Produces: `./install.sh citrix-vdi` works; full `./install.sh` includes it on macOS, skips it on Linux.

- [ ] **Step 1: Add citrix-vdi to ALL_TOOLS and MAC_ONLY**

In `install.sh`, change lines 13–14 from:

```bash
ALL_TOOLS=(zsh starship nvim wezterm vscode terminal-macos iterm2)
MAC_ONLY=(terminal-macos iterm2)
```

to:

```bash
ALL_TOOLS=(zsh starship nvim wezterm vscode terminal-macos iterm2 citrix-vdi)
MAC_ONLY=(terminal-macos iterm2 citrix-vdi)
```

- [ ] **Step 2: Run via installer, verify**

Run: `./install.sh citrix-vdi`
Expected: `===== citrix-vdi =====` banner, then all `✅` lines (idempotent — Task 2 already installed everything), ending `✅ All done. ...`

- [ ] **Step 3: Commit**

```bash
git add install.sh
git commit -m "Register citrix-vdi tool in installer (macOS-only)"
```
