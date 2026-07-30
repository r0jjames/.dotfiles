# JetBrains Keymap Fanout Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Distribute `roj-keymap` to every JetBrains IDE on a machine (IntelliJ, PyCharm, GoLand) by renaming the `intellij` tool to `jetbrains`, widening config-dir discovery, and dropping IDE provisioning.

**Architecture:** One shared keymap XML per OS stays the source of truth. `lib/tools/intellij.py` becomes `lib/tools/jetbrains.py`, its `_PRODUCT_PREFIXES` allowlist gains `PyCharm` and `GoLand`, and its macOS Homebrew cask install is removed so the tool does exactly one thing — place `roj-keymap.xml` into `<product>/keymaps/` for every JetBrains config dir found.

**Tech Stack:** Python 3 stdlib (`pathlib`, `unittest`), repo-local `lib.core` helpers (`link_file`, `copy_file`, `unlink_file`, `uncopy_file`), Git.

## Global Constraints

- Test runner: `python3 -m unittest discover -s tests < /dev/null` (stdin must be redirected — a UI test prompts otherwise). No pytest in this environment.
- Every commit message uses Roj's git identity only. No `Co-Authored-By`, no `Claude-Session`, no "Generated with Claude" footers.
- Renames use `git mv` so history is preserved.
- Both keymap XML files must keep identical relocated chords (enforced by `test_mac_and_windows_bindings_are_identical`, case-insensitive).
- `_KEYMAP_TARGET` stays `"roj-keymap.xml"` — the installed filename does not change, only the repo path it points at.
- Existing `docs/superpowers/specs/*` and `docs/superpowers/plans/*` are historical; do not rewrite `intellij` references inside them.
- Spec: `docs/superpowers/specs/2026-07-30-jetbrains-keymap-fanout-design.md`

---

### Task 1: Widen product-prefix discovery to PyCharm and GoLand

Done first, before any rename, so the behaviour change lands in a small green commit that is easy to revert independently of the rename churn.

**Files:**
- Modify: `lib/tools/intellij.py:38` (`_PRODUCT_PREFIXES`)
- Test: `tests/test_intellij.py:174-188` (`FindConfigDirsTest`)

**Interfaces:**
- Consumes: nothing from earlier tasks.
- Produces: `intellij.find_config_dirs(base: Path) -> list[Path]` now returns dirs whose names start with any of `("IdeaIC", "IntelliJIdea", "PyCharm", "GoLand")`, sorted by name. Task 3 renames the module but keeps this signature.

- [ ] **Step 1: Rewrite the failing test**

Replace `test_matches_community_and_ultimate_ignores_others` in `tests/test_intellij.py`:

```python
    def test_matches_every_jetbrains_ide_ignores_non_ide_dirs(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            ide_dirs = ["GoLand2025.2", "IdeaIC2026.1", "IntelliJIdea2025.3",
                        "PyCharm2025.3", "PyCharmCE2024.1"]
            for name in ide_dirs + ["consentOptions", "Toolbox"]:
                (base / name).mkdir()
            (base / "somefile.txt").write_text("x")
            found = [d.name for d in intellij.find_config_dirs(base)]
            self.assertEqual(found, sorted(ide_dirs))
```

`PyCharmCE2024.1` is in the list deliberately: `"PyCharm"` as a `str.startswith`
prefix must cover the Community and Edu variants without extra entries.

- [ ] **Step 2: Run it and watch it fail**

Run: `python3 -m unittest tests.test_intellij -k jetbrains_ide -v`
Expected: FAIL — `Lists differ: ['IdeaIC2026.1', 'IntelliJIdea2025.3'] != ['GoLand2025.2', ...]`

- [ ] **Step 3: Widen the allowlist**

In `lib/tools/intellij.py`, replace the `_PRODUCT_PREFIXES` line and its comment:

```python
# Config-dir name prefixes, one per JetBrains product family. "PyCharm" as a
# str.startswith prefix also covers PyCharmCE* (Community) and PyCharmEdu*.
# Non-IDE siblings in the JetBrains base (consentOptions, Toolbox, the bl/crl
# files) match none of these.
_PRODUCT_PREFIXES = ("IdeaIC", "IntelliJIdea", "PyCharm", "GoLand")
```

- [ ] **Step 4: Run the test again**

Run: `python3 -m unittest tests.test_intellij -v`
Expected: PASS, 13 tests OK.

- [ ] **Step 5: Commit**

```bash
git add lib/tools/intellij.py tests/test_intellij.py
git commit -m "feat(intellij): install keymap into PyCharm and GoLand config dirs"
```

---

### Task 2: Drop IDE provisioning

**Files:**
- Modify: `lib/tools/intellij.py` (module docstring, `_CASK`/`_APP` constants and their NOTE comment, the install block in `_post()`)

**Interfaces:**
- Consumes: `find_config_dirs` from Task 1.
- Produces: `_post()` performs keymap placement only. `lib.core.brew_install` is no longer imported or called from this module.

- [ ] **Step 1: Delete the cask constants**

Remove this whole block from `lib/tools/intellij.py`:

```python
# NOTE: the `intellij-idea-ce` cask is deprecated upstream (disabled
# 2026-12-08) - JetBrains folded Community into the unified `intellij-idea`
# distribution's free tier. When CE stops installing, switch _CASK to
# "intellij-idea" and _APP to "/Applications/IntelliJ IDEA CE.app".
_CASK = "intellij-idea-ce"
_APP = Path("/Applications/IntelliJ IDEA CE.app")
```

- [ ] **Step 2: Delete the install step in `_post()`**

Remove:

```python
    # 1. Install the app (macOS only; Windows host assumed to have it).
    if core.detect_os() == "macos":
        if _APP.is_dir():
            core.ok("IntelliJ IDEA CE already installed.")
        else:
            core.brew_install(_CASK, cask=True)
```

Then renumber the surviving comment `# 2. Place the keymap...` to `# Place the keymap into every existing config dir.`

- [ ] **Step 3: Update the two stale messages in `_uninstall()`**

Replace:

```python
    core.info("IntelliJ app left installed - remove via brew/Finder if unwanted.")
```

with:

```python
    core.info("JetBrains IDEs are installed outside dotfiles - none were touched.")
```

- [ ] **Step 4: Rewrite the module docstring**

Replace the whole docstring at the top of `lib/tools/intellij.py`:

```python
"""JetBrains IDEs: the F-free cross-OS roj-keymap, distributed to all of them.

  macOS   - SYMLINK keymap-macos.xml into every
            ~/Library/Application Support/JetBrains/<product>/keymaps/
  Windows - (Git Bash) COPY keymap-windows.xml into every
            %APPDATA%/JetBrains/<product>/keymaps/ (symlinks need admin).

<product> is any dir named for a JetBrains IDE family - IntelliJ Community or
Ultimate, PyCharm (incl. CE/Edu), GoLand. This tool does NOT install IDEs: you
install them yourself via Toolbox or brew, and it distributes the keymap to
whichever ones are present. That keeps install idempotent across machines with
different IDE sets, and sidesteps the deprecated intellij-idea-ce cask
(disabled upstream 2026-12-08).

JetBrains config dirs are version-stamped (IdeaIC2026.1, PyCharm2025.3, ...),
unlike VS Code's stable Code/User - so we glob every matching dir and place the
keymap in each. If none exist yet, no IDE has ever launched: we warn to open one
once and re-run. The keymap only becomes *active* after you pick it in
Settings -> Keymap (see jetbrains/README.md). The VDI is not reachable here -
it gets the keymap via Settings Sync (Path A) or vdi-apply-keymap.ps1.
"""
```

- [ ] **Step 5: Run the full suite**

Run: `python3 -m unittest discover -s tests < /dev/null 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `Ran 90 tests`, `OK`.

- [ ] **Step 6: Commit**

```bash
git add lib/tools/intellij.py
git commit -m "refactor(intellij): stop provisioning the IDE, distribute the keymap only"
```

---

### Task 3: Rename intellij → jetbrains

One task, not three: the directory move, module move, test move and registry
edit are a single atomic rename — any subset committed alone leaves the repo
red.

**Files:**
- Move: `intellij/` → `jetbrains/` (carries `keymap-macos.xml`, `keymap-windows.xml`, `plugins.txt`, `README.md`, `vdi-apply-keymap.ps1`)
- Move: `lib/tools/intellij.py` → `lib/tools/jetbrains.py`
- Move: `tests/test_intellij.py` → `tests/test_jetbrains.py`
- Modify: `lib/tools/__init__.py:5-7` (import), `lib/tools/__init__.py:14` (registry tuple)

**Interfaces:**
- Consumes: the module from Task 2.
- Produces: `lib.tools.jetbrains.TOOL` with `name="jetbrains"`; `REGISTRY["jetbrains"]`; repo path `core.REPO_ROOT / "jetbrains"`. Task 4 modifies `jetbrains._post()`; Task 5 documents these names.

- [ ] **Step 1: Move the files**

```bash
git mv intellij jetbrains
git mv lib/tools/intellij.py lib/tools/jetbrains.py
git mv tests/test_intellij.py tests/test_jetbrains.py
```

- [ ] **Step 2: Run the suite and watch it fail**

Run: `python3 -m unittest discover -s tests < /dev/null 2>&1 | grep -E "^(OK|FAILED|Ran |ImportError)"`
Expected: FAIL — `ImportError: cannot import name 'intellij' from 'lib.tools'`.

- [ ] **Step 3: Point the module at the new path and name**

In `lib/tools/jetbrains.py`, change the header comment and `_src`, and the `TOOL` definition:

```python
# lib/tools/jetbrains.py
```

```python
def _src(filename: str) -> Path:
    return core.REPO_ROOT / "jetbrains" / filename
```

```python
TOOL = Tool(
    name="jetbrains",
    doc="roj-keymap for every JetBrains IDE (IntelliJ, PyCharm, GoLand)",
    platforms=frozenset({"macos", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

Also update the two user-facing strings in `_post()` and `_uninstall()` that
name the old paths:

```python
    core.ok("Keymap installed. One-time manual step: Settings -> Keymap -> "
            "select 'roj-keymap'. See jetbrains/README.md (plugins, VDI sync, "
            "cheatsheet).")
```

```python
    core.warn(f"No JetBrains config dir under {base}.")
    core.warn("Launch a JetBrains IDE once (so it creates its config), then "
              "re-run: ./install.py install jetbrains")
```

and in `_uninstall()`:

```python
    core.skip(f"No JetBrains config dir under {base} - nothing to remove.")
```

Rename `_jetbrains_dir`'s error message too:

```python
    raise core.DotfilesError("jetbrains: unsupported platform (macOS/Git Bash only).")
```

- [ ] **Step 4: Update the registry**

In `lib/tools/__init__.py`, change the import and the tuple entry:

```python
from lib.tools import (agent_skills, citrix_vdi, claude, ghostty, iterm2,
                       jetbrains, maven, nvim, rancher_desktop, starship,
                       terminal_macos, vscode, wezterm, zsh)
```

```python
    vscode.TOOL,
    jetbrains.TOOL,
```

- [ ] **Step 5: Update the test module**

In `tests/test_jetbrains.py`, change the header comment, the import, the path
constants, and every `intellij.` call site:

```python
# tests/test_jetbrains.py
```

```python
from lib.tools import jetbrains
```

```python
_JETBRAINS = core.REPO_ROOT / "jetbrains"
_MAC = _JETBRAINS / "keymap-macos.xml"
_WIN = _JETBRAINS / "keymap-windows.xml"
```

Then replace `intellij.find_config_dirs` with `jetbrains.find_config_dirs`
(two call sites, in `test_matches_every_jetbrains_ide_ignores_non_ide_dirs` and
`test_missing_base_returns_empty`) and `_INTELLIJ` with `_JETBRAINS` (one call
site, in `PluginsFileTest.test_vscode_keymap_plugin_listed`).

- [ ] **Step 6: Run the suite**

Run: `python3 -m unittest discover -s tests < /dev/null 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `Ran 90 tests`, `OK`.

- [ ] **Step 7: Verify the registry from the CLI**

Run: `python3 install.py status 2>&1 | grep -i -E "jetbrains|intellij"`
Expected: a `jetbrains` row, no `intellij` row.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "refactor: rename the intellij tool to jetbrains"
```

---

### Task 4: Clean up symlinks left dangling by the rename

Installed Macs have `IdeaIC2025.2/keymaps/roj-keymap.xml -> …/.dotfiles/intellij/keymap-macos.xml`, which points at a path that no longer exists. Without this, `core.link_file` renames the dangling link to `<target>.bak-YYYY-MM-DD`, and a later `core.unlink_file` would "restore" that broken link as if it were the user's own file.

**Files:**
- Modify: `lib/tools/jetbrains.py` (new `_STALE_SRC_DIR` constant, new cleanup in `_post()`)
- Test: `tests/test_jetbrains.py` (new `MigrationTest` class)

**Interfaces:**
- Consumes: `jetbrains._post()` from Task 3.
- Produces: `jetbrains._drop_pre_rename_link(target: Path) -> bool` — returns `True` when it removed a symlink pointing into the old `intellij/` repo dir, `False` otherwise. Called by `_post()` before `core.link_file`.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_jetbrains.py`, before the `if __name__` block:

```python
class MigrationTest(unittest.TestCase):
    def test_drops_symlink_into_old_intellij_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            old_src = Path(tmp) / "intellij" / "keymap-macos.xml"
            old_src.parent.mkdir(parents=True)
            old_src.write_text("<keymap/>")
            target = Path(tmp) / "keymaps" / "roj-keymap.xml"
            target.parent.mkdir(parents=True)
            target.symlink_to(old_src)

            self.assertTrue(jetbrains._drop_pre_rename_link(target))
            self.assertFalse(target.exists() or target.is_symlink())

    def test_drops_it_even_when_the_old_path_is_gone(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "roj-keymap.xml"
            target.symlink_to(Path(tmp) / "intellij" / "keymap-macos.xml")

            self.assertTrue(jetbrains._drop_pre_rename_link(target))
            self.assertFalse(target.is_symlink())

    def test_keeps_a_current_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "jetbrains" / "keymap-macos.xml"
            src.parent.mkdir(parents=True)
            src.write_text("<keymap/>")
            target = Path(tmp) / "roj-keymap.xml"
            target.symlink_to(src)

            self.assertFalse(jetbrains._drop_pre_rename_link(target))
            self.assertTrue(target.is_symlink())

    def test_keeps_a_real_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "roj-keymap.xml"
            target.write_text("<keymap/>")

            self.assertFalse(jetbrains._drop_pre_rename_link(target))
            self.assertTrue(target.is_file())
```

The second case matters most: after `git mv`, the old path is gone, so
`Path.resolve()` must be used in a way that works on a broken symlink —
`os.readlink` semantics, not `target.resolve()` on an existing file.

- [ ] **Step 2: Run it and watch it fail**

Run: `python3 -m unittest tests.test_jetbrains.MigrationTest -v`
Expected: FAIL — `AttributeError: module 'lib.tools.jetbrains' has no attribute '_drop_pre_rename_link'`.

- [ ] **Step 3: Implement it**

Add near `_STALE_KEYMAP_TARGET` in `lib/tools/jetbrains.py`:

```python
# Repo dir this tool used before the intellij -> jetbrains rename. Symlinks
# from a pre-rename install point into it and now dangle; we delete them
# rather than let link_file back them up, since unlink_file would later
# "restore" a broken link as if it were the user's own file.
_STALE_SRC_DIR = "intellij"


def _drop_pre_rename_link(target: Path) -> bool:
    """Delete target when it is a symlink into the pre-rename intellij/ dir.

    Uses readlink, not resolve(): after the rename the link is broken, so the
    destination cannot be stat'ed. Returns True when something was removed.
    """
    if not target.is_symlink():
        return False
    dest = Path(os.readlink(target))
    if _STALE_SRC_DIR not in dest.parts:
        return False
    target.unlink()
    core.info(f"Removed {target} from a pre-rename (intellij/) install.")
    return True
```

`os` is already imported at the top of the module.

- [ ] **Step 4: Call it from `_post()`**

In the per-dir loop in `_post()`, immediately after the existing
`_STALE_KEYMAP_TARGET` block and before `target = keymaps_dir / _KEYMAP_TARGET`
is used:

```python
        target = keymaps_dir / _KEYMAP_TARGET
        _drop_pre_rename_link(target)
        if mode == "link":
            core.link_file(src, target)
        else:
            core.copy_file(src, target)
```

- [ ] **Step 5: Run the suite**

Run: `python3 -m unittest discover -s tests < /dev/null 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `Ran 94 tests`, `OK`.

- [ ] **Step 6: Commit**

```bash
git add lib/tools/jetbrains.py tests/test_jetbrains.py
git commit -m "fix(jetbrains): drop symlinks left dangling by the intellij rename"
```

---

### Task 5: Documentation

**Files:**
- Modify: `jetbrains/README.md` (title, intro, Install section, new Product coverage section)
- Modify: `jetbrains/vdi-apply-keymap.ps1` (raw-URL path, config-dir glob)
- Modify: `README.md` (root — tool table row, copy-instead-of-symlink list)

**Interfaces:**
- Consumes: the `jetbrains` tool name and repo path from Task 3.
- Produces: no code. Docs referenced by `_post()`'s success message (`jetbrains/README.md`).

- [ ] **Step 1: Retitle `jetbrains/README.md` and rewrite its intro**

Replace the title and first paragraph:

```markdown
# jetbrains — one F-free keymap for every JetBrains IDE

Distributes a **custom keymap that uses no F1-F12 keys**, identical on macOS
and Windows, to every JetBrains IDE installed on the machine — IntelliJ IDEA
(Community or Ultimate), PyCharm (incl. CE/Edu) and GoLand. Same shortcuts on
your personal Mac, your work Windows laptop, and the Citrix Windows VDI —
without depending on the F-row (which the NuPhy Win/Mac switch and Citrix
mangle). See [`../citrix-vdi/README.md`](../citrix-vdi/README.md) for the
F-row hardware story; those Karabiner rules stay in place for other apps.

**This tool does not install IDEs.** Install them yourself (JetBrains Toolbox
or brew); the installer distributes the keymap to whichever ones it finds.
```

- [ ] **Step 2: Rewrite the Install section**

Replace the macOS and Windows install blocks so both read `./install.py install
jetbrains`, and delete the sentence about installing the `intellij-idea-ce`
cask. macOS text becomes:

```markdown
### macOS (personal) — *run on: Mac*

```sh
./install.py install jetbrains
```

**Symlinks** `keymap-macos.xml` into every
`~/Library/Application Support/JetBrains/<product>/keymaps/`.
```

Windows text keeps its copy-not-symlink explanation and the "No config dir"
callout, with `%APPDATA%\JetBrains\{IntelliJIdea*,IdeaIC*}\keymaps\` widened to
`%APPDATA%\JetBrains\{IntelliJIdea*,IdeaIC*,PyCharm*,GoLand*}\keymaps\` and the
command changed to `./install.py install jetbrains`.

- [ ] **Step 3: Add the Product coverage section**

Insert after the Install section:

```markdown
## Product coverage

Config dirs are matched by name prefix: `IdeaIC`, `IntelliJIdea`, `PyCharm`
(also catches `PyCharmCE`/`PyCharmEdu`), `GoLand`. A new JetBrains IDE
(WebStorm, DataGrip, RustRover) needs one line added to `_PRODUCT_PREFIXES`
in `lib/tools/jetbrains.py`.

One shared keymap serves every product. All 65 action ids in the keymap were
checked against PyCharm 2025.3's own action registrations (`Contents/lib/*.jar`
plus `Contents/plugins/*/lib/*.jar`) — none are missing, `CompileDirty`
included. Registered is not the same as useful, though: `Alt+B` (`CompileDirty`)
has nothing to compile in a pure-Python project, so treat it as inert there.
GoLand was not available to sweep. An id an IDE does not know is ignored
silently by the keymap reader — the chord is simply dead in that product,
nothing breaks and no warning appears.
```

- [ ] **Step 4: Update the uninstall section**

Replace the sentence about the IntelliJ app being left installed with:

```markdown
Removes the keymap file from every JetBrains config dir. The IDEs themselves
are installed outside dotfiles and are never touched. If `roj-keymap` is still
selected, switch back to a default keymap in Settings → Keymap.
```

Also change the command in that section to `./install.py uninstall jetbrains`.

- [ ] **Step 5: Update `vdi-apply-keymap.ps1`**

Change the raw-URL default so the path segment reads `jetbrains/keymap-windows.xml`
instead of `intellij/keymap-windows.xml`, and widen the config-dir discovery
glob to cover all four families (matching the tool's `_PRODUCT_PREFIXES`):

```powershell
$patterns = @('IntelliJIdea*', 'IdeaIC*', 'PyCharm*', 'GoLand*')
```

Read the script first — keep its existing structure, change only the URL path
segment, the glob, and any user-facing text naming IntelliJ specifically.

- [ ] **Step 6: Update the root `README.md`**

Line 65 — the tool table row:

```markdown
| [`jetbrains/`](jetbrains/README.md) | F-free cross-OS keymap for every JetBrains IDE — IntelliJ, PyCharm, GoLand (Mac/Windows/VDI) | macOS, Windows (Git Bash) |
```

Line 79 — the copy-instead-of-symlink list: change `` `intellij` `` to
`` `jetbrains` ``.

- [ ] **Step 7: Check no stale references survive outside the historical docs**

Run: `grep -rn "intellij" -il --include="*.py" --include="*.md" --include="*.ps1" . | grep -v __pycache__ | grep -v "docs/superpowers"`
Expected: only `jetbrains/README.md` (prose about IntelliJ the product, and
the `com.intellij.plugins.vscodekeymap` plugin id), `jetbrains/plugins.txt`
(same plugin id), `citrix-vdi/README.md` (prose), and `vscode/extensions.txt`
(`k--kato.intellij-idea-keybindings`). No `lib/`, no `tests/`, no root README.

- [ ] **Step 8: Commit**

```bash
git add -A
git commit -m "docs(jetbrains): document multi-IDE coverage and the rename"
```

---

### Task 6: Verify on real hardware and push

**Files:** none modified — this task runs the tool.

**Interfaces:**
- Consumes: everything from Tasks 1-5.
- Produces: a pushed `main`.

- [ ] **Step 1: Full suite, one more time**

Run: `python3 -m unittest discover -s tests < /dev/null 2>&1 | grep -E "^(OK|FAILED|Ran )"`
Expected: `Ran 94 tests`, `OK`.

- [ ] **Step 2: Install on this Mac**

Run: `python3 install.py install jetbrains`
Expected: reports 2 config dirs (`IdeaIC2025.2`, `PyCharm2025.3`), removes the
pre-rename symlink in `IdeaIC2025.2`, links both.

- [ ] **Step 3: Confirm the filesystem state**

```bash
ls -l ~/Library/Application\ Support/JetBrains/*/keymaps/
```

Expected: `roj-keymap.xml` in both `IdeaIC2025.2/keymaps/` and
`PyCharm2025.3/keymaps/`, each a symlink to
`/Users/roj/Dev/.dotfiles/jetbrains/keymap-macos.xml`. **No `.bak-*` file**
beside them — if one appeared, Task 4's cleanup did not fire.

- [ ] **Step 4: Confirm status**

Run: `python3 install.py status 2>&1 | grep -i jetbrains`
Expected: `jetbrains` reported installed.

- [ ] **Step 5: Push**

```bash
git push origin main
```

- [ ] **Step 6: Manual check, reported to Roj (not automatable)**

PyCharm must be **quit and relaunched** — a running IDE rewrites its keymap
files on exit. Then: Settings → Keymap → select `roj-keymap`, confirm `Alt+R`
(Rename) and `Alt+Z` (Soft-Wrap) fire, and scan for red conflict markers from
Python-specific plugins. Report any conflict as a follow-up, and note whether
`Alt+B` does anything in a Python project.

---

## Self-Review

**Spec coverage:** prefixes → Task 1. Provisioning removal → Task 2. Module,
dir, test and registry rename plus "no back-compat alias" → Task 3. Dangling
symlink migration → Task 4. Product-gap documentation, README, ps1, root README
→ Task 5. Verification steps 1-5 of the spec → Task 6. Out-of-scope VS Code
work is deliberately absent.

**Placeholders:** none — every code step carries the literal text to write.

**Type consistency:** `find_config_dirs(base: Path) -> list[Path]` is unchanged
throughout; `_drop_pre_rename_link(target: Path) -> bool` is defined in Task 4
and called only there; `TOOL.name == "jetbrains"` is set in Task 3 and used by
Tasks 5-6.
