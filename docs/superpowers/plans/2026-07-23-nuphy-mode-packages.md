# NuPhy Windows/Mac Mode Karabiner Packages Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Split `citrix-vdi`'s single Karabiner rule file into a device-agnostic base package and a NuPhy-Windows-mode-only extra package, so Roj can maintain two Karabiner profiles ("NuPhy Windows mode" / "NuPhy Mac mode") and switch between them with one click, alongside the NuPhy's own hardware Win/Mac switch.

**Architecture:** Pure file-and-docs change. `citrix-vdi/karabiner-citrix.json` keeps the 2 rules needed in every mode; a new `citrix-vdi/karabiner-nuphy-windows-mode.json` holds the 2 rules needed only when the NuPhy is in Windows mode. `lib/tools/citrix_vdi.py` is generalized from one rule file to a list of two, everywhere it currently assumes one. No rule *content* changes — Citrix-scoped rule logic is untouched, so existing Windows-mode-inside-Citrix behavior is a pure regression case, not new behavior.

**Tech Stack:** Python 3 (repo's `lib/` installer framework), `unittest`, Karabiner-Elements complex-modification JSON, Karabiner Profiles (GUI-only, no CLI).

## Global Constraints

- macOS-only tool (existing `platforms=frozenset({"macos"})` on `TOOL` — unchanged).
- No content changes to rule *logic* — only which file each rule lives in. The 2 Citrix-scoped rules ("F1-F12 as function keys", "Left Command as Alt") and the 2 NuPhy rules ("Ctrl/Cmd swap outside Citrix", "Ctrl+Left/Right switches desktop outside Citrix") keep their exact `manipulators` content.
- Karabiner profile creation/switching has no CLI — stays a documented manual GUI procedure, never scripted.
- Idempotent installer pattern (existing `core.copy_file` diff-checks before copying; `_uninstall` safe to rerun) must still hold for both files.
- Every README step keeps the existing "Run on: Mac" framing — nothing changes inside the Windows VDI.

---

### Task 1: Split the Karabiner rule file into base + NuPhy-Windows-mode-extra packages

**Files:**
- Modify: `citrix-vdi/karabiner-citrix.json` (trim to 2 rules, retitle)
- Create: `citrix-vdi/karabiner-nuphy-windows-mode.json` (2 rules)
- Modify: `lib/tools/citrix_vdi.py:17-19` (`_rules_src` → `_rules_srcs`)
- Test: `tests/test_citrix.py`

**Interfaces:**
- Produces: `citrix_vdi._rules_srcs() -> list[Path]`, returning exactly
  `[REPO_ROOT / "citrix-vdi" / "karabiner-citrix.json", REPO_ROOT / "citrix-vdi" / "karabiner-nuphy-windows-mode.json"]`,
  in that order. Task 2 consumes this list.

- [ ] **Step 1: Write the failing test**

Add to `tests/test_citrix.py` (new class, alongside the existing `RemoveEnabledRulesTest`):

```python
class RuleFilesTest(unittest.TestCase):
    def test_two_rule_files_with_expected_descriptions(self):
        files = citrix_vdi._rules_srcs()
        self.assertEqual(
            [f.name for f in files],
            ["karabiner-citrix.json", "karabiner-nuphy-windows-mode.json"])
        for f in files:
            self.assertTrue(f.is_file(), f"{f} does not exist")

        base = json.loads(files[0].read_text())
        self.assertEqual(
            [r["description"] for r in base["rules"]],
            ["Citrix VDI: F1-F12 as function keys (with any modifiers)",
             "Citrix VDI: Left Command as Alt (all keyboards)"])

        extra = json.loads(files[1].read_text())
        self.assertEqual(
            [r["description"] for r in extra["rules"]],
            ["NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl/Cmd swap outside Citrix",
             "NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl+Left/Right switches desktop outside Citrix"])
```

`json` and `citrix_vdi` are already imported at the top of the file — no new imports needed.

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m pytest tests/test_citrix.py::RuleFilesTest -v` (or `python3 -m unittest tests.test_citrix.RuleFilesTest -v` if pytest isn't installed)
Expected: FAIL — `AttributeError: module 'lib.tools.citrix_vdi' has no attribute '_rules_srcs'`

- [ ] **Step 3: Split the JSON file**

Run this one-off script from the repo root — it reads the current 4-rule file, asserts the split point, and writes both target files:

```bash
python3 <<'EOF'
import json
from pathlib import Path

src = Path("citrix-vdi/karabiner-citrix.json")
data = json.loads(src.read_text())
rules = data["rules"]
assert len(rules) == 4, f"expected 4 rules, found {len(rules)}"

base_rules, extra_rules = rules[:2], rules[2:]

base = {"title": "Citrix VDI: base rules (all keyboards)", "rules": base_rules}
extra = {
    "title": "NuPhy: Windows mode extra (Ctrl/Cmd swap + desktop switch)",
    "rules": extra_rules,
}

src.write_text(json.dumps(base, indent=2) + "\n")
Path("citrix-vdi/karabiner-nuphy-windows-mode.json").write_text(
    json.dumps(extra, indent=2) + "\n")

print("base:", [r["description"] for r in base_rules])
print("extra:", [r["description"] for r in extra_rules])
EOF
```

Expected output:
```
base: ['Citrix VDI: F1-F12 as function keys (with any modifiers)', 'Citrix VDI: Left Command as Alt (all keyboards)']
extra: ['NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl/Cmd swap outside Citrix', 'NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl+Left/Right switches desktop outside Citrix']
```

- [ ] **Step 4: Verify both files are valid and git sees the split**

Run: `python3 -m json.tool citrix-vdi/karabiner-citrix.json > /dev/null && python3 -m json.tool citrix-vdi/karabiner-nuphy-windows-mode.json > /dev/null && echo OK`
Expected: `OK`

Run: `git status --short citrix-vdi/`
Expected:
```
 M citrix-vdi/karabiner-citrix.json
?? citrix-vdi/karabiner-nuphy-windows-mode.json
```

- [ ] **Step 5: Update `_rules_src` to `_rules_srcs` in `lib/tools/citrix_vdi.py`**

Replace lines 17-19:

```python
def _rules_src() -> Path:
    return core.REPO_ROOT / "citrix-vdi" / "karabiner-citrix.json"
```

with:

```python
def _rules_srcs() -> list[Path]:
    return [
        core.REPO_ROOT / "citrix-vdi" / "karabiner-citrix.json",
        core.REPO_ROOT / "citrix-vdi" / "karabiner-nuphy-windows-mode.json",
    ]
```

(Task 2 updates every caller of the old `_rules_src()` — this task only introduces the new accessor.)

- [ ] **Step 6: Run test to verify it passes**

Run: `python3 -m pytest tests/test_citrix.py::RuleFilesTest -v`
Expected: PASS

- [ ] **Step 7: Commit**

```bash
git add citrix-vdi/karabiner-citrix.json citrix-vdi/karabiner-nuphy-windows-mode.json lib/tools/citrix_vdi.py tests/test_citrix.py
git commit -m "$(cat <<'EOF'
refactor(citrix-vdi): split Karabiner rules into base + NuPhy-Windows-mode packages

Base package (F-keys, Left-Cmd-as-Alt) applies regardless of NuPhy
mode; the NuPhy Ctrl/Cmd swap rules move to their own file so they can
be enabled only in a "Windows mode" Karabiner profile, leaving a
"Mac mode" profile that enables just the base package.
EOF
)"
```

---

### Task 2: Generalize `_post`, `_uninstall`, `_probe` to both rule files

**Files:**
- Modify: `lib/tools/citrix_vdi.py:21-24` (`_assets_file`), `:49-57` (`_post`), `:60-91` (`_uninstall`), `:93-95` (`_probe`)

**Interfaces:**
- Consumes: `_rules_srcs() -> list[Path]` from Task 1; `remove_enabled_rules(rules_file: Path, config_file: Path) -> int` (existing, unchanged).
- Produces: `_asset_file_for(src: Path) -> Path`, used by `_post`, `_uninstall`, `_probe`.

- [ ] **Step 1: Replace `_assets_file` with `_asset_file_for`**

Replace lines 21-24:

```python
def _assets_file() -> Path:
    return (Path.home() / ".config/karabiner/assets/complex_modifications"
            / "karabiner-citrix.json")
```

with:

```python
def _assets_dir() -> Path:
    return Path.home() / ".config/karabiner/assets/complex_modifications"


def _asset_file_for(src: Path) -> Path:
    return _assets_dir() / src.name
```

- [ ] **Step 2: Update `_post` to copy both files**

Replace:

```python
def _post() -> None:
    if Path("/Applications/Karabiner-Elements.app").is_dir():
        core.ok("Karabiner-Elements already installed.")
    else:
        core.brew_install("karabiner-elements", cask=True)
    core.copy_file(_rules_src(), _assets_file())
    core.ok("citrix-vdi setup complete. One-time manual steps remain "
            "(Karabiner rule enable + Citrix keyboard preferences) — "
            "see citrix-vdi/README.md.")
```

with:

```python
def _post() -> None:
    if Path("/Applications/Karabiner-Elements.app").is_dir():
        core.ok("Karabiner-Elements already installed.")
    else:
        core.brew_install("karabiner-elements", cask=True)
    for src in _rules_srcs():
        core.copy_file(src, _asset_file_for(src))
    core.ok("citrix-vdi setup complete. One-time manual steps remain "
            "(Karabiner profile setup + Citrix keyboard preferences) — "
            "see citrix-vdi/README.md.")
```

- [ ] **Step 3: Update `_uninstall` to remove rules from and delete both files**

Replace the body of `_uninstall` (lines 60-90) with:

```python
def _uninstall() -> None:
    config = _karabiner_config()
    # ---- 1. Remove enabled rules from the live Karabiner config ----
    if not config.is_file():
        core.skip(f"No {config} — no enabled rules to remove.")
    else:
        backup = config.with_name(
            config.name + ".bak-" + date.today().isoformat())
        if not backup.exists():
            core.info(f"Backing up {config} -> {backup}")
            shutil.copy2(config, backup)
        removed = sum(remove_enabled_rules(src, config)
                      for src in _rules_srcs())
        if removed:
            core.ok(f"Removed {removed} enabled rule(s) from karabiner.json "
                    "(Karabiner reloads automatically).")
        else:
            core.ok("No Citrix/NuPhy rules enabled in karabiner.json.")
    # ---- 2. Remove the rule files from the assets folder ----
    for src in _rules_srcs():
        asset = _asset_file_for(src)
        if asset.exists():
            asset.unlink()
            core.ok(f"Removed {asset}")
        else:
            core.ok(f"{asset.name} already absent from assets folder.")
    # ---- 3. Manual follow-ups ----
    core.ok("citrix-vdi uninstall complete. Remaining manual steps:")
    print("  1. Citrix Workspace -> Preferences -> Keyboard -> Keyboard input"
          " mode -> Automatic (then reconnect the VDI session).")
    print("  2. NuPhy: free to use any mode and connection again.")
    print("  3. Karabiner: delete the 'NuPhy Windows mode' / 'NuPhy Mac mode'"
          " profiles if you no longer want them (Karabiner-Elements ->"
          " Settings -> Profiles).")
    print("  4. Optional, if Karabiner-Elements is otherwise unused: "
          "Karabiner-Elements -> Settings -> uninstall section, or "
          "brew uninstall --cask karabiner-elements")
```

(`remove_enabled_rules` reads `config_file` fresh each call, so calling it twice in sequence on the same path correctly accumulates removals from both rule files.)

- [ ] **Step 4: Update `_probe` to check both files**

Replace:

```python
def _probe() -> bool:
    t = _assets_file()
    return t.exists() and filecmp.cmp(str(_rules_src()), str(t), shallow=False)
```

with:

```python
def _probe() -> bool:
    return all(
        _asset_file_for(src).exists()
        and filecmp.cmp(str(src), str(_asset_file_for(src)), shallow=False)
        for src in _rules_srcs()
    )
```

- [ ] **Step 5: Run the full test suite**

Run: `python3 -m pytest tests/test_citrix.py -v`
Expected: all tests PASS (the pre-existing `RemoveEnabledRulesTest` cases plus `RuleFilesTest` from Task 1).

- [ ] **Step 6: Manual dry run on the live machine**

```bash
./install.py install citrix-vdi
```
Expected: both `karabiner-citrix.json` and `karabiner-nuphy-windows-mode.json` appear under `~/.config/karabiner/assets/complex_modifications/`. Rerun the same command — expect `ok`/`skip` output for both files (idempotent, no error).

- [ ] **Step 7: Commit**

```bash
git add lib/tools/citrix_vdi.py
git commit -m "$(cat <<'EOF'
feat(citrix-vdi): install/uninstall/probe both Karabiner rule packages

_post, _uninstall, and _probe now loop over _rules_srcs() instead of
a single file, so the new NuPhy-Windows-mode-extra package is
installed, cleaned up, and status-checked alongside the base package.
EOF
)"
```

---

### Task 3: README — package/profile setup and the "Switching NuPhy mode" section

**Files:**
- Modify: `citrix-vdi/README.md`

**Interfaces:** None (docs only).

- [ ] **Step 1: Update the "Automated part" step (current lines 27-34)**

Replace:

```markdown
### 1. Automated part — *run on: Mac*

```sh
./install.py install citrix-vdi
```

Installs Karabiner-Elements (Homebrew cask) and copies the rule file to
`~/.config/karabiner/assets/complex_modifications/`.
```

with:

```markdown
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
```

- [ ] **Step 2: Replace step 2 "Enable the Karabiner rule" (current lines 36-51) with two-profile setup**

Replace that whole section with:

```markdown
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
```

- [ ] **Step 3: Insert a new "Switching NuPhy mode" section** after the new step 2 (before the current "3. Citrix Workspace keyboard preferences" step)

Insert:

```markdown
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
```

- [ ] **Step 4: Update step 4 "NuPhy external keyboard" (current lines 65-89)**

Replace the numbered list (items 2 and 4, which describe "Windows mode
permanently" and enabling the two NuPhy rules directly) with:

```markdown
4. **NuPhy external keyboard** — *run on: Mac*

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
```

- [ ] **Step 5: Update "What gets installed where" table (current lines 91-102)**

Change the row:

```markdown
| `~/.config/karabiner/assets/complex_modifications/karabiner-citrix.json` | rule file copied by the installer | `./install.py uninstall citrix-vdi` |
```

to:

```markdown
| `~/.config/karabiner/assets/complex_modifications/karabiner-citrix.json` + `karabiner-nuphy-windows-mode.json` | base + NuPhy-Windows-mode-extra rule files copied by the installer | `./install.py uninstall citrix-vdi` |
```

And change:

```markdown
| `~/.config/karabiner/karabiner.json` — `profiles[*].complex_modifications.rules` | the three rules, copied in when you enable them in the GUI (setup steps 2 and 4) | `./install.py uninstall citrix-vdi` |
```

to:

```markdown
| `~/.config/karabiner/karabiner.json` — `profiles[*].complex_modifications.rules` | 2 rules in the "NuPhy Mac mode" profile, 4 in the "NuPhy Windows mode" profile, copied in when you enable them in the GUI (setup step 2) | `./install.py uninstall citrix-vdi` |
| `~/.config/karabiner/karabiner.json` — `profiles[*].name` | the two profile names themselves ("NuPhy Windows mode", "NuPhy Mac mode") | manual, Karabiner-Elements → Settings → Profiles |
```

- [ ] **Step 6: Update the Uninstall automated-part paragraph (current lines 136-144)**

Replace "Removes the three enabled..." with:

```markdown
Removes the enabled "Citrix VDI"/"NuPhy" rules (from both the base and
NuPhy-Windows-mode-extra packages) from every profile in
`~/.config/karabiner/karabiner.json` (after backing it up to
`karabiner.json.bak-YYYY-MM-DD`; Karabiner picks up the change
automatically) and deletes both rule files from the assets folder. Safe to
rerun.
```

- [ ] **Step 7: Proofread — verify every referenced rule/file name matches reality**

```bash
grep -n "karabiner-citrix.json\|karabiner-nuphy-windows-mode.json" citrix-vdi/README.md
grep -n "NuPhy Windows mode\|NuPhy Mac mode" citrix-vdi/README.md
```

Confirm every match is spelled identically to the actual file names
(`citrix-vdi/karabiner-citrix.json`, `citrix-vdi/karabiner-nuphy-windows-mode.json`)
and profile names used in Task 3 Step 2/3 above — no typos, no leftover
"Windows mode permanently" language.

- [ ] **Step 8: Commit**

```bash
git add citrix-vdi/README.md
git commit -m "$(cat <<'EOF'
docs(citrix-vdi): document base/extra packages and NuPhy mode switching

Replaces the old "keep NuPhy in Windows mode permanently" instructions
with a two-Karabiner-profile setup and an explicit switching procedure
for flipping the NuPhy hardware switch and the matching profile
together.
EOF
)"
```

---

### Task 4: Update the citrix-vdi-keyboard-context memory

**Files:**
- Modify: `/Users/roj/.claude/projects/-Users-roj-Dev--dotfiles/memory/citrix-vdi-keyboard-context.md`
- Modify: `/Users/roj/.claude/projects/-Users-roj-Dev--dotfiles/memory/MEMORY.md`

**Interfaces:** None (memory content only).

- [ ] **Step 1: Rewrite the memory body**

Replace the line:

```
- **NuPhy Air75 V3, Windows mode permanently; dongle (vendor 6645, product 4136) or Bluetooth (vendor 2007) both fine.** 2026-07-09: Ctrl↔Cmd swap rule extended to match Bluetooth too — earlier note that Karabiner drops all events when grabbing BT proved stale (Modify events ON for vendor 2007 works). If BT keys ever stop flowing: Modify events OFF for 2007, fall back to dongle.
```

with:

```
- **NuPhy Air75 V3, dual-mode as of 2026-07-23: two Karabiner profiles, "NuPhy Windows mode" and "NuPhy Mac mode", switched together with the keyboard's hardware Win/Mac switch.** Dongle (vendor 6645, product 4136) or Bluetooth (vendor 2007) both fine in either mode; Modify events ON for both device entries in both profiles. If BT keys ever stop flowing: Modify events OFF for 2007, fall back to dongle.
- Rules split into two files: `citrix-vdi/karabiner-citrix.json` (base — F-keys, Left-Cmd-as-Alt, needed by both profiles) and `citrix-vdi/karabiner-nuphy-windows-mode.json` (Ctrl/Cmd swap + Ctrl+Arrow desktop-switch fix, enabled only in the "NuPhy Windows mode" profile — Mac mode already sends native modifier codes outside Citrix, so it needs no swap rule). See `docs/superpowers/specs/2026-07-23-nuphy-mode-packages-design.md`.
```

Also update the line about Karabiner rules in the "Final architecture" bullet to say "outside Citrix, NuPhy Windows-mode profile only" instead of implying it always applies.

- [ ] **Step 2: Update the MEMORY.md index line**

Replace:

```
- [Citrix VDI keyboard context](citrix-vdi-keyboard-context.md) — NuPhy Windows-mode habit, left-Cmd-as-Alt rule, Citrix prefs gotcha
```

with:

```
- [Citrix VDI keyboard context](citrix-vdi-keyboard-context.md) — NuPhy dual-mode via 2 Karabiner profiles, left-Cmd-as-Alt rule, Citrix prefs gotcha
```

- [ ] **Step 3: No commit** — memory files live outside the dotfiles git repo (`~/.claude/projects/...`), not tracked by this repository's git. Nothing to stage here.

---

## Self-Review

**Spec coverage:**
- File split (base + extra) → Task 1. ✓
- `_post`/`_uninstall`/`_probe` generalized to 2 files → Task 2. ✓
- Karabiner profile setup (rename/duplicate, per-profile rule enable, Modify-events) → Task 3 Step 2. ✓
- "Switching NuPhy mode" daily procedure → Task 3 Step 3. ✓
- README setup/table/uninstall wording → Task 3 Steps 1, 5, 6. ✓
- Memory update → Task 4. ✓
- Spec's "Testing" section (install/uninstall idempotency, profile regression check) → Task 2 Step 6 (install dry run) + Task 3 covers the profile instructions the user will follow manually; uninstall idempotency re-run is called out in Task 2 Step 3's docstring behavior (unchanged from original, already exercised by the existing `remove_enabled_rules` tests) — full end-to-end uninstall dry run is left to Roj since it mutates his live `karabiner.json`, consistent with how the original uninstall design was verified (see 2026-07-09 spec's own "Testing" section, same live-machine caveat).

**Placeholder scan:** none — every step has literal code, exact commands, or exact markdown text to insert.

**Type consistency:** `_rules_srcs() -> list[Path]` (Task 1) is the only new interface; Task 2's `_asset_file_for(src: Path) -> Path` and its three call sites all consume it the same way. No naming drift between tasks.
