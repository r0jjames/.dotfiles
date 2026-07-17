# Python Interactive Installer Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the bash install layer with a single stdlib-only Python 3 installer (`install.py`) that installs and uninstalls every tool symmetrically, with an interactive checkbox menu.

**Architecture:** Declarative `Tool` specs (one module per tool in `lib/tools/`) consumed by a shared engine (`lib/core.py`). Install = brew → links → `post_install`; uninstall = `extra_uninstall` → remove links → restore backups. Interactive UI in `lib/ui.py`. Behavior ports 1:1 from the existing `setup.sh` scripts.

**Tech Stack:** Python 3.9+ stdlib only. `unittest` for tests. Spec: `docs/superpowers/specs/2026-07-17-python-installer-design.md`.

## Global Constraints

- **Stdlib only** — no pip/uv packages anywhere.
- **Python 3.9 compatible** (macOS system `/usr/bin/python3`). Use `from __future__ import annotations` in every module; no 3.10-only syntax (no `match`, no runtime `X | Y` types).
- **Port 1:1** — no behavior changes vs the shell scripts. Same log emoji (`📦 ✅ ⏭️ ⚠️`), same backup scheme (`<target>.bak-YYYY-MM-DD`, one per day), same messages where practical.
- **Uninstall never removes brew packages** and never touches a target that isn't a repo symlink / identical repo copy.
- Tests run with: `python3 -m unittest discover -s tests -v` from repo root.
- Repo root = `/Users/roj/Dev/.dotfiles`. All commits conventional style, terse.

---

### Task 1: Core engine — logging, OS detect, link/copy operations

**Files:**
- Create: `lib/__init__.py` (empty)
- Create: `lib/core.py`
- Test: `tests/__init__.py` (empty), `tests/test_core.py`

**Interfaces:**
- Produces: `info/ok/skip/warn(msg)`, `detect_os() -> str` ("macos"|"linux"|"gitbash"), `is_wsl() -> bool`, `DotfilesError(Exception)`, `REPO_ROOT: Path`, `link_file(src: Path, target: Path)`, `unlink_file(src: Path, target: Path) -> bool`, `copy_file(src: Path, target: Path)`, `uncopy_file(src: Path, target: Path) -> bool`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_core.py
from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from lib import core


class LinkFileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "repo" / "conf"
        self.src.parent.mkdir()
        self.src.write_text("repo content")
        self.target = self.root / "home" / ".conf"

    def bak(self):
        return self.target.with_name(self.target.name + ".bak-" + date.today().isoformat())

    def test_creates_symlink(self):
        core.link_file(self.src, self.target)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.target.resolve(), self.src.resolve())

    def test_idempotent(self):
        core.link_file(self.src, self.target)
        core.link_file(self.src, self.target)  # no error, still linked
        self.assertEqual(self.target.resolve(), self.src.resolve())

    def test_backs_up_existing_file(self):
        self.target.parent.mkdir()
        self.target.write_text("old content")
        core.link_file(self.src, self.target)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.bak().read_text(), "old content")

    def test_second_backup_same_day_not_overwritten(self):
        self.target.parent.mkdir()
        self.target.write_text("original")
        core.link_file(self.src, self.target)
        self.target.unlink()
        self.target.write_text("newer stale")
        core.link_file(self.src, self.target)
        self.assertEqual(self.bak().read_text(), "original")
        self.assertTrue(self.target.is_symlink())

    def test_missing_source_raises(self):
        with self.assertRaises(core.DotfilesError):
            core.link_file(self.root / "nope", self.target)


class UnlinkFileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "repo" / "conf"
        self.src.parent.mkdir()
        self.src.write_text("repo content")
        self.target = self.root / "home" / ".conf"

    def test_removes_our_link_and_restores_backup(self):
        self.target.parent.mkdir()
        self.target.write_text("old content")
        core.link_file(self.src, self.target)
        removed = core.unlink_file(self.src, self.target)
        self.assertTrue(removed)
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_text(), "old content")

    def test_removes_link_no_backup(self):
        core.link_file(self.src, self.target)
        self.assertTrue(core.unlink_file(self.src, self.target))
        self.assertFalse(self.target.exists())

    def test_leaves_foreign_file(self):
        self.target.parent.mkdir()
        self.target.write_text("mine, not yours")
        self.assertFalse(core.unlink_file(self.src, self.target))
        self.assertEqual(self.target.read_text(), "mine, not yours")

    def test_leaves_foreign_symlink(self):
        other = self.root / "other"
        other.write_text("x")
        self.target.parent.mkdir()
        self.target.symlink_to(other)
        self.assertFalse(core.unlink_file(self.src, self.target))
        self.assertTrue(self.target.is_symlink())

    def test_missing_target_ok(self):
        self.assertFalse(core.unlink_file(self.src, self.target))


class CopyFileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "repo.json"
        self.src.write_text("repo content")
        self.target = self.root / "deployed.json"

    def test_copies_and_backs_up(self):
        self.target.write_text("old")
        core.copy_file(self.src, self.target)
        self.assertEqual(self.target.read_text(), "repo content")
        bak = self.target.with_name(
            self.target.name + ".bak-" + date.today().isoformat())
        self.assertEqual(bak.read_text(), "old")

    def test_uncopy_removes_identical_and_restores(self):
        self.target.write_text("old")
        core.copy_file(self.src, self.target)
        self.assertTrue(core.uncopy_file(self.src, self.target))
        self.assertEqual(self.target.read_text(), "old")

    def test_uncopy_leaves_modified_target(self):
        core.copy_file(self.src, self.target)
        self.target.write_text("user edited this")
        self.assertFalse(core.uncopy_file(self.src, self.target))
        self.assertEqual(self.target.read_text(), "user edited this")


class DetectOsTest(unittest.TestCase):
    def test_returns_known_value(self):
        self.assertIn(core.detect_os(), ("macos", "linux", "gitbash"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_core -v`
Expected: FAIL/ERROR with `ModuleNotFoundError: No module named 'lib.core'` (or `lib` not a package).

- [ ] **Step 3: Implement `lib/core.py`** (create empty `lib/__init__.py` and `tests/__init__.py` too)

```python
# lib/core.py
"""Engine for the dotfiles installer: logging, OS detection, link/copy ops.

Ported 1:1 from lib/common.sh. Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import filecmp
import platform as _platform
import shutil
import sys
from datetime import date
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


class DotfilesError(Exception):
    """Fatal for the current tool; the batch runner catches it and continues."""


# ---- Logging (same emoji as lib/common.sh) ----
def info(msg: str) -> None:
    print(f"📦 {msg}")


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def skip(msg: str) -> None:
    print(f"⏭️  {msg}")


def warn(msg: str) -> None:
    print(f"⚠️  {msg}", file=sys.stderr)


# ---- OS detection ----
def detect_os() -> str:
    """Return "macos", "linux" or "gitbash"; raise on anything else."""
    system = _platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Linux":
        return "linux"
    if system == "Windows" or system.startswith(("MINGW", "MSYS")):
        return "gitbash"
    raise DotfilesError(
        f"Unsupported OS: {system}. Only macOS, Linux (WSL Ubuntu) and "
        "Git Bash (VS Code settings only) are supported.")


def is_wsl() -> bool:
    proc = Path("/proc/version")
    try:
        return "microsoft" in proc.read_text().lower()
    except OSError:
        return False


# ---- Backups ----
def _backup_path(target: Path) -> Path:
    return target.with_name(target.name + ".bak-" + date.today().isoformat())


def _restore_newest_backup(target: Path) -> None:
    backups = sorted(target.parent.glob(target.name + ".bak-*"))
    if backups:
        newest = backups[-1]
        newest.rename(target)
        ok(f"Restored backup {newest} -> {target}")


# ---- Symlinking (port of link_file in common.sh) ----
def link_file(src: Path, target: Path) -> None:
    """Symlink target -> src. Skip when already linked; back up a real
    file/dir to <target>.bak-YYYY-MM-DD first (one backup per day; a stale
    same-day target is dropped)."""
    if not src.exists():
        raise DotfilesError(f"link_file: source does not exist: {src}")

    if target.is_symlink() and target.resolve() == src.resolve():
        ok(f"{target} already linked.")
        return

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() or target.is_symlink():
        backup = _backup_path(target)
        if backup.exists() or backup.is_symlink():
            # already backed up today; drop the stale copy
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        else:
            info(f"Backing up {target} -> {backup}")
            target.rename(backup)

    target.symlink_to(src)
    ok(f"Linked {target} -> {src}")


def unlink_file(src: Path, target: Path) -> bool:
    """Remove target only when it is a symlink to src; restore the newest
    .bak-* sibling. Foreign files/links are left alone. True when removed."""
    if not target.is_symlink():
        if target.exists():
            skip(f"{target} is not a dotfiles symlink — leaving alone.")
        return False
    if target.resolve() != src.resolve():
        skip(f"{target} points elsewhere — leaving alone.")
        return False
    target.unlink()
    ok(f"Removed link {target}")
    _restore_newest_backup(target)
    return True


# ---- Copying (port of copy_file in vscode/setup.sh, shared now) ----
def copy_file(src: Path, target: Path) -> None:
    """Copy with dated backup; skip when identical."""
    if target.exists() and filecmp.cmp(str(src), str(target), shallow=False):
        ok(f"{target} already up to date.")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup = _backup_path(target)
        if not backup.exists():
            info(f"Backing up {target} -> {backup}")
            shutil.copy2(target, backup)
    shutil.copy2(src, target)
    ok(f"Copied {src} -> {target}")


def uncopy_file(src: Path, target: Path) -> bool:
    """Remove target only when identical to src; restore newest backup.
    A target the user modified is left alone. True when removed."""
    if not target.exists():
        return False
    if not filecmp.cmp(str(src), str(target), shallow=False):
        skip(f"{target} differs from repo copy — leaving alone.")
        return False
    target.unlink()
    ok(f"Removed {target}")
    _restore_newest_backup(target)
    return True
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_core -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add lib/__init__.py lib/core.py tests/__init__.py tests/test_core.py
git commit -m "feat(installer): core engine — logging, OS detect, link/copy ops"
```

---

### Task 2: Core engine — subprocess/brew helpers, Tool/Link dataclasses, install/uninstall/status

**Files:**
- Modify: `lib/core.py` (append)
- Test: `tests/test_core.py` (append)

**Interfaces:**
- Consumes: Task 1 functions.
- Produces:
  - `run(cmd, check=True, capture=False, shell=False) -> subprocess.CompletedProcess`
  - `have(name: str) -> bool`
  - `ensure_brew() -> str` (returns brew executable path), `brew_install(pkg: str, cask: bool = False)`
  - `Link(src: str, target: str)` with `.src_path() -> Path` (repo-relative unless absolute — absolute allowed for tests) and `.target_path() -> Path` (expanduser)
  - `Tool(name, doc, platforms, brew=(), casks=(), links=(), post_install=None, extra_uninstall=None, status_probe=None)`
  - `link_ok(link: Link) -> bool`
  - `tool_status(tool: Tool) -> str` returning `core.INSTALLED` ("installed") / `core.PARTIAL` ("partial") / `core.NOT_INSTALLED` ("not installed")
  - `install_tool(tool: Tool)`, `uninstall_tool(tool: Tool)`

- [ ] **Step 1: Write the failing tests** (append to `tests/test_core.py`)

```python
from unittest import mock


class ToolStatusTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "a").write_text("a")
        (self.root / "b").write_text("b")
        self.tool = core.Tool(
            name="fake", doc="fake tool", platforms=frozenset({"macos", "linux"}),
            links=(core.Link(str(self.root / "a"), str(self.root / "home_a")),
                   core.Link(str(self.root / "b"), str(self.root / "home_b"))))

    def test_not_installed(self):
        self.assertEqual(core.tool_status(self.tool), core.NOT_INSTALLED)

    def test_partial_then_installed(self):
        core.link_file(self.root / "a", self.root / "home_a")
        self.assertEqual(core.tool_status(self.tool), core.PARTIAL)
        core.link_file(self.root / "b", self.root / "home_b")
        self.assertEqual(core.tool_status(self.tool), core.INSTALLED)

    def test_probe_used_when_no_links(self):
        probed = core.Tool(name="p", doc="", platforms=frozenset({"macos"}),
                           status_probe=lambda: True)
        self.assertEqual(core.tool_status(probed), core.INSTALLED)


class InstallUninstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "conf").write_text("repo")
        self.target = self.root / ".conf"
        self.events = []
        self.tool = core.Tool(
            name="fake", doc="", platforms=frozenset({"macos", "linux"}),
            brew=("somepkg",),
            links=(core.Link(str(self.root / "conf"), str(self.target)),),
            post_install=lambda: self.events.append("post"),
            extra_uninstall=lambda: self.events.append("cleanup"))

    def test_install_orders_brew_links_post(self):
        with mock.patch.object(core, "brew_install") as bi, \
             mock.patch.object(core, "ensure_brew", return_value="brew"):
            core.install_tool(self.tool)
        bi.assert_called_once_with("somepkg", cask=False)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.events, ["post"])

    def test_uninstall_symmetry(self):
        self.target.write_text("pre-existing")
        with mock.patch.object(core, "brew_install"), \
             mock.patch.object(core, "ensure_brew", return_value="brew"):
            core.install_tool(self.tool)
        core.uninstall_tool(self.tool)
        self.assertEqual(self.events, ["post", "cleanup"])
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_text(), "pre-existing")
        self.assertEqual(core.tool_status(self.tool), core.NOT_INSTALLED)
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_core -v`
Expected: ERROR — `AttributeError: module 'lib.core' has no attribute 'Tool'`.

- [ ] **Step 3: Implement** (append to `lib/core.py`; add `import subprocess` and `from dataclasses import dataclass, field` and `from typing import Callable, Optional, Tuple` to the imports)

```python
# ---- Subprocess ----
def run(cmd, check: bool = True, capture: bool = False, shell: bool = False):
    """Thin subprocess.run wrapper. cmd is a list, or a string when shell=True."""
    return subprocess.run(cmd, check=check, shell=shell,
                          capture_output=capture, text=True)


def have(name: str) -> bool:
    return shutil.which(name) is not None


# ---- Homebrew (port of ensure_brew/brew_install in common.sh) ----
_BREW_PATHS = (
    "/opt/homebrew/bin/brew",
    "/usr/local/bin/brew",
    "/home/linuxbrew/.linuxbrew/bin/brew",
)
_brew_cache: Optional[str] = None


def _find_brew() -> Optional[str]:
    found = shutil.which("brew")
    if found:
        return found
    for p in _BREW_PATHS:
        if Path(p).exists():
            return p
    return None


def ensure_brew() -> str:
    """Return the brew executable, installing Homebrew when missing."""
    global _brew_cache
    if _brew_cache:
        return _brew_cache
    brew = _find_brew()
    if brew is None:
        info("Installing Homebrew...")
        run('/bin/bash -c "$(curl -fsSL '
            'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True)
        brew = _find_brew()
        if brew is None:
            raise DotfilesError(
                "Homebrew install failed or brew not on PATH. See https://brew.sh")
    _brew_cache = brew
    return brew


def brew_install(pkg: str, cask: bool = False) -> None:
    """Install pkg via brew only if missing (brew list check, as before)."""
    brew = ensure_brew()
    listed = run([brew, "list", pkg], check=False, capture=True)
    if listed.returncode == 0:
        ok(f"{pkg} already installed.")
        return
    info(f"Installing {pkg}...")
    cmd = [brew, "install"]
    if cask:
        cmd.append("--cask")
    cmd.append(pkg)
    run(cmd)


# ---- Tool model ----
@dataclass(frozen=True)
class Link:
    src: str      # repo-relative path (absolute allowed, used by tests)
    target: str   # target path, ~ expanded

    def src_path(self) -> Path:
        p = Path(self.src)
        return p if p.is_absolute() else REPO_ROOT / p

    def target_path(self) -> Path:
        return Path(self.target).expanduser()


@dataclass(frozen=True)
class Tool:
    name: str
    doc: str
    platforms: frozenset
    brew: tuple = ()
    casks: tuple = ()
    links: tuple = ()                       # tuple[Link, ...]
    post_install: Optional[Callable[[], None]] = None
    extra_uninstall: Optional[Callable[[], None]] = None
    status_probe: Optional[Callable[[], bool]] = None  # tools without links


INSTALLED = "installed"
PARTIAL = "partial"
NOT_INSTALLED = "not installed"


def link_ok(link: Link) -> bool:
    t = link.target_path()
    return t.is_symlink() and t.resolve() == link.src_path().resolve()


def tool_status(tool: Tool) -> str:
    if tool.links:
        done = sum(1 for l in tool.links if link_ok(l))
        if done == len(tool.links):
            return INSTALLED
        return PARTIAL if done else NOT_INSTALLED
    if tool.status_probe is not None:
        return INSTALLED if tool.status_probe() else NOT_INSTALLED
    return NOT_INSTALLED


def install_tool(tool: Tool) -> None:
    """brew packages -> links -> post_install."""
    if tool.brew or tool.casks:
        ensure_brew()
    for pkg in tool.brew:
        brew_install(pkg, cask=False)
    for pkg in tool.casks:
        brew_install(pkg, cask=True)
    for link in tool.links:
        link_file(link.src_path(), link.target_path())
    if tool.post_install is not None:
        tool.post_install()


def uninstall_tool(tool: Tool) -> None:
    """extra_uninstall -> remove links -> restore backups. Brew untouched."""
    if tool.extra_uninstall is not None:
        tool.extra_uninstall()
    for link in tool.links:
        unlink_file(link.src_path(), link.target_path())
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_core -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add lib/core.py tests/test_core.py
git commit -m "feat(installer): brew helpers, Tool/Link model, install/uninstall engine"
```

---

### Task 3: Interactive UI

**Files:**
- Create: `lib/ui.py`
- Test: `tests/test_ui.py`

**Interfaces:**
- Consumes: nothing from core (pure I/O module).
- Produces:
  - `MenuItem(label: str, status: str, enabled: bool)` dataclass
  - `parse_numbers(raw: str, count: int) -> Optional[set]` — 1-based indices from "3 7" / "3,7"; None on any invalid token
  - `interactive_select(items, input_fn=input, print_fn=print) -> list` — returns selected 0-based indices; empty list = quit
  - `choose_action(input_fn=input, print_fn=print) -> str` — returns "install" | "uninstall" | "quit"
  - `confirm(prompt: str, input_fn=input) -> bool`

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_ui.py
from __future__ import annotations

import unittest

from lib import ui


def scripted(*lines):
    it = iter(lines)
    return lambda prompt="": next(it)


ITEMS = [
    ui.MenuItem("zsh", "installed", True),
    ui.MenuItem("nvim", "not installed", True),
    ui.MenuItem("citrix-vdi", "macOS only", False),
]


class ParseNumbersTest(unittest.TestCase):
    def test_spaces_and_commas(self):
        self.assertEqual(ui.parse_numbers("1 3", 3), {1, 3})
        self.assertEqual(ui.parse_numbers("1,2", 3), {1, 2})
        self.assertEqual(ui.parse_numbers("1, 2", 3), {1, 2})

    def test_out_of_range_or_junk_is_none(self):
        self.assertIsNone(ui.parse_numbers("0", 3))
        self.assertIsNone(ui.parse_numbers("4", 3))
        self.assertIsNone(ui.parse_numbers("x", 3))


class InteractiveSelectTest(unittest.TestCase):
    def test_toggle_then_confirm(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("1 2", ""), print_fn=lambda *a: None)
        self.assertEqual(sel, [0, 1])

    def test_toggle_twice_removes(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("1", "1", "2", ""), print_fn=lambda *a: None)
        self.assertEqual(sel, [1])

    def test_all_skips_disabled(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("a", ""), print_fn=lambda *a: None)
        self.assertEqual(sel, [0, 1])

    def test_disabled_not_toggleable(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("3", ""), print_fn=lambda *a: None)
        self.assertEqual(sel, [])

    def test_quit(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("1", "q"), print_fn=lambda *a: None)
        self.assertEqual(sel, [])

    def test_empty_with_no_selection_quits(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted(""), print_fn=lambda *a: None)
        self.assertEqual(sel, [])


class ChooseActionTest(unittest.TestCase):
    def test_actions(self):
        self.assertEqual(ui.choose_action(input_fn=scripted("i")), "install")
        self.assertEqual(ui.choose_action(input_fn=scripted("u")), "uninstall")
        self.assertEqual(ui.choose_action(input_fn=scripted("q")), "quit")

    def test_reprompts_on_junk(self):
        self.assertEqual(ui.choose_action(input_fn=scripted("z", "i")), "install")


class ConfirmTest(unittest.TestCase):
    def test_yes_no_default_no(self):
        self.assertTrue(ui.confirm("?", input_fn=scripted("y")))
        self.assertFalse(ui.confirm("?", input_fn=scripted("n")))
        self.assertFalse(ui.confirm("?", input_fn=scripted("")))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_ui -v`
Expected: ERROR — `ModuleNotFoundError: No module named 'lib.ui'`.

- [ ] **Step 3: Implement `lib/ui.py`**

```python
# lib/ui.py
"""Interactive checkbox menu and prompts. Stdlib only; I/O injectable for tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Set

MARK_ON = "[x]"
MARK_OFF = "[ ]"


@dataclass(frozen=True)
class MenuItem:
    label: str
    status: str
    enabled: bool


def parse_numbers(raw: str, count: int) -> Optional[Set[int]]:
    """Parse 1-based indices from '3 7' or '3,7'. None on any invalid token."""
    tokens = [t for t in raw.replace(",", " ").split() if t]
    if not tokens:
        return None
    out = set()
    for t in tokens:
        if not t.isdigit():
            return None
        n = int(t)
        if not 1 <= n <= count:
            return None
        out.add(n)
    return out


def _draw(items: List[MenuItem], selected: Set[int], print_fn) -> None:
    print_fn("")
    for i, item in enumerate(items):
        if not item.enabled:
            print_fn(f"   –  [{i + 1}] {item.label:<15} {item.status}")
        else:
            mark = MARK_ON if i in selected else MARK_OFF
            print_fn(f"  {mark} [{i + 1}] {item.label:<15} {item.status}")
    print_fn("")
    print_fn("Toggle: numbers (space/comma separated), a=all, n=none, "
             "enter=confirm, q=quit")


def interactive_select(items: List[MenuItem],
                       input_fn: Callable = input,
                       print_fn: Callable = print) -> List[int]:
    """Checkbox selection loop. Returns selected 0-based indices ([] = quit)."""
    selected: Set[int] = set()
    while True:
        _draw(items, selected, print_fn)
        raw = input_fn("> ").strip().lower()
        if raw == "":
            return sorted(selected)
        if raw == "q":
            return []
        if raw == "a":
            selected = {i for i, item in enumerate(items) if item.enabled}
            continue
        if raw == "n":
            selected = set()
            continue
        nums = parse_numbers(raw, len(items))
        if nums is None:
            print_fn("Invalid selection.")
            continue
        for n in nums:
            i = n - 1
            if not items[i].enabled:
                print_fn(f"{items[i].label}: {items[i].status} — not selectable.")
                continue
            selected.symmetric_difference_update({i})


def choose_action(input_fn: Callable = input,
                  print_fn: Callable = print) -> str:
    while True:
        raw = input_fn("[i]nstall / [u]ninstall / [q]uit > ").strip().lower()
        if raw in ("i", "install"):
            return "install"
        if raw in ("u", "uninstall"):
            return "uninstall"
        if raw in ("q", "quit", ""):
            return "quit"
        print_fn("Please answer i, u or q.")


def confirm(prompt: str, input_fn: Callable = input) -> bool:
    return input_fn(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_ui -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add lib/ui.py tests/test_ui.py
git commit -m "feat(installer): interactive checkbox menu + prompts"
```

---

### Task 4: Tool registry + simple specs (starship, wezterm, claude)

**Files:**
- Create: `lib/tools/__init__.py`, `lib/tools/starship.py`, `lib/tools/wezterm.py`, `lib/tools/claude.py`
- Test: `tests/test_registry.py`

**Interfaces:**
- Consumes: `core.Tool`, `core.Link`, `core.run`, `core.have`, `core.ok/info`, `core.DotfilesError`.
- Produces: `lib.tools.REGISTRY` — ordered `dict[str, Tool]` keyed by tool name. Each tool module exports `TOOL: core.Tool`. Later tasks append imports to `lib/tools/__init__.py` and entries to `_ALL`.

- [ ] **Step 1: Write the failing registry sanity test** (it grows automatically as later tasks register more tools)

```python
# tests/test_registry.py
from __future__ import annotations

import unittest

from lib import core
from lib import tools


class RegistrySanityTest(unittest.TestCase):
    def test_names_unique_and_match_keys(self):
        names = [t.name for t in tools.REGISTRY.values()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names, list(tools.REGISTRY.keys()))

    def test_platforms_valid(self):
        for tool in tools.REGISTRY.values():
            self.assertTrue(tool.platforms, f"{tool.name}: empty platforms")
            self.assertTrue(
                tool.platforms <= {"macos", "linux", "gitbash"},
                f"{tool.name}: bad platforms {tool.platforms}")

    def test_link_sources_exist_in_repo(self):
        for tool in tools.REGISTRY.values():
            for link in tool.links:
                self.assertFalse(
                    link.src.startswith("/"),
                    f"{tool.name}: absolute link src {link.src}")
                self.assertTrue(
                    link.src_path().exists(),
                    f"{tool.name}: missing link source {link.src_path()}")

    def test_status_never_crashes(self):
        for tool in tools.REGISTRY.values():
            self.assertIn(core.tool_status(tool),
                          (core.INSTALLED, core.PARTIAL, core.NOT_INSTALLED))

    def test_docs_present(self):
        for tool in tools.REGISTRY.values():
            self.assertTrue(tool.doc, f"{tool.name}: empty doc")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_registry -v`
Expected: ERROR — `ModuleNotFoundError: No module named 'lib.tools'`.

- [ ] **Step 3: Implement the three specs and the registry**

```python
# lib/tools/starship.py
"""Starship prompt: install + link config. Init line lives in zsh/.zshrc."""
from __future__ import annotations

from lib.core import Link, Tool

TOOL = Tool(
    name="starship",
    doc="Starship prompt + config",
    platforms=frozenset({"macos", "linux"}),
    brew=("starship",),
    links=(Link("starship/starship.toml", "~/.config/starship.toml"),),
)
```

```python
# lib/tools/wezterm.py
"""WezTerm (macOS): app + fonts + config. On WSL, WezTerm runs on the
Windows host — see wezterm/README.md."""
from __future__ import annotations

from lib.core import Link, Tool

TOOL = Tool(
    name="wezterm",
    doc="WezTerm terminal + config",
    platforms=frozenset({"macos"}),
    casks=("wezterm", "font-go-mono-nerd-font"),
    links=(Link("wezterm/wezterm.lua", "~/.config/wezterm/wezterm.lua"),
           Link("wezterm/events.lua", "~/.config/wezterm/events.lua")),
)
```

```python
# lib/tools/claude.py
"""Claude Code: CLI install + global settings + statusline. Plugins install
themselves on next `claude` start from settings.json."""
from __future__ import annotations

from lib import core
from lib.core import Link, Tool


def _install_cli() -> None:
    if core.have("claude"):
        version = core.run(["claude", "--version"],
                           check=False, capture=True).stdout.strip()
        core.ok(f"Claude Code already installed: {version}")
        return
    core.info("Installing Claude Code CLI (native installer)...")
    result = core.run("curl -fsSL https://claude.ai/install.sh | bash",
                      shell=True, check=False)
    if result.returncode != 0:
        raise core.DotfilesError(
            "Installer failed. See https://claude.com/claude-code for options.")
    core.ok("Claude Code installed. Installer puts it in ~/.local/bin; "
            "open a new terminal if 'claude' is not found.")
    core.info("Plugins listed in settings.json install automatically on the "
              "next 'claude' start.")


TOOL = Tool(
    name="claude",
    doc="Claude Code CLI + global settings",
    platforms=frozenset({"macos", "linux"}),
    links=(Link("claude/settings.json", "~/.claude/settings.json"),
           Link("claude/statusline-command.sh", "~/.claude/statusline-command.sh"),
           Link("claude/CLAUDE.md", "~/.claude/CLAUDE.md")),
    post_install=_install_cli,
)
```

```python
# lib/tools/__init__.py
"""Tool registry. Order here is menu/run order (mirrors old ALL_TOOLS)."""
from __future__ import annotations

from lib.tools import claude, starship, wezterm

_ALL = (
    starship.TOOL,
    wezterm.TOOL,
    claude.TOOL,
)

REGISTRY = {t.name: t for t in _ALL}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python3 -m unittest tests.test_registry -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add lib/tools tests/test_registry.py
git commit -m "feat(installer): tool registry + starship/wezterm/claude specs"
```

---

### Task 5: zsh and nvim specs

**Files:**
- Create: `lib/tools/zsh.py`, `lib/tools/nvim.py`
- Modify: `lib/tools/__init__.py`

**Interfaces:**
- Consumes: `core` helpers, registry pattern from Task 4.
- Produces: `zsh.TOOL`, `nvim.TOOL` registered; final `_ALL` order starts `zsh, starship, nvim, wezterm, ...`.

- [ ] **Step 1: Implement `lib/tools/zsh.py`** (port of `zsh/setup.sh`)

```python
# lib/tools/zsh.py
"""Zsh shell stack: zsh, modern CLI tools, plugins, ~/.zshrc (symlinked)."""
from __future__ import annotations

import os
import shutil

from lib import core
from lib.core import Link, Tool


def _linux_zsh() -> None:
    """Linux only: install zsh via apt (brew zsh as login shell is fragile)
    and make it the login shell."""
    if core.detect_os() != "linux":
        return
    if core.have("zsh"):
        core.ok("zsh already installed.")
    else:
        core.info("Installing zsh via apt...")
        core.run(["sudo", "apt-get", "update"])
        core.run(["sudo", "apt-get", "install", "-y", "zsh"])
    if os.path.basename(os.environ.get("SHELL", "")) != "zsh":
        core.info("Setting zsh as login shell...")
        core.run(["chsh", "-s", shutil.which("zsh")])
    else:
        core.ok("zsh is already the login shell.")


TOOL = Tool(
    name="zsh",
    doc="Zsh + CLI tools + plugins + .zshrc",
    platforms=frozenset({"macos", "linux"}),
    brew=("bat", "eza", "fzf", "zoxide", "ripgrep", "fd", "htop",
          "zsh-autosuggestions", "zsh-syntax-highlighting"),
    links=(Link("zsh/.zshrc", "~/.zshrc"),),
    post_install=_linux_zsh,
)
```

- [ ] **Step 2: Implement `lib/tools/nvim.py`** (port of `nvim/setup.sh`)

```python
# lib/tools/nvim.py
"""Neovim DevOps IDE: neovim + DevOps CLIs, config symlinked to ~/.config/nvim."""
from __future__ import annotations

from lib import core
from lib.core import Link, Tool


def _post() -> None:
    # ---- Fonts (icons in the UI) ----
    if core.detect_os() == "macos":
        core.brew_install("fontconfig")
        fc = core.run(["fc-list"], check=False, capture=True).stdout
        if "nerd" in fc.lower():
            core.ok("Nerd Font already installed.")
        else:
            core.brew_install("font-jetbrains-mono-nerd-font", cask=True)
    else:
        core.skip("Fonts render from the Windows-side terminal on WSL — "
                  "install a Nerd Font on Windows (see README).")
    # ---- Plugins (headless) then Mason tools/servers ----
    core.info("Syncing Neovim plugins (lazy.nvim)...")
    core.run(["nvim", "--headless", "+Lazy! sync", "+qa"], check=False)
    core.info("Installing LSP servers, formatters, and linters (Mason)...")
    core.run(["nvim", "--headless",
              "-c", "autocmd User MasonToolsUpdateCompleted quitall",
              "-c", "MasonToolsInstall"], check=False)


TOOL = Tool(
    name="nvim",
    doc="Neovim DevOps IDE + CLIs",
    platforms=frozenset({"macos", "linux"}),
    brew=("git", "neovim", "kubectl", "helm", "ansible", "uv",
          "hadolint", "terraform"),
    links=(Link("nvim/config", "~/.config/nvim"),),
    post_install=_post,
)
```

- [ ] **Step 3: Register both** — replace the body of `lib/tools/__init__.py`:

```python
"""Tool registry. Order here is menu/run order (mirrors old ALL_TOOLS)."""
from __future__ import annotations

from lib.tools import claude, nvim, starship, wezterm, zsh

_ALL = (
    zsh.TOOL,
    starship.TOOL,
    nvim.TOOL,
    wezterm.TOOL,
    claude.TOOL,
)

REGISTRY = {t.name: t for t in _ALL}
```

- [ ] **Step 4: Run full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS (registry sanity now covers zsh/nvim; `nvim/config` and `zsh/.zshrc` must exist — they do).

- [ ] **Step 5: Commit**

```bash
git add lib/tools
git commit -m "feat(installer): zsh + nvim specs"
```

---

### Task 6: vscode spec

**Files:**
- Create: `lib/tools/vscode.py`
- Modify: `lib/tools/__init__.py`

**Interfaces:**
- Consumes: `core.link_file/unlink_file/copy_file/uncopy_file`, `core.detect_os`, `core.have`, `core.run`, `core.REPO_ROOT`.
- Produces: `vscode.TOOL` (platforms macos+gitbash; all logic in hooks + `status_probe` since deploy mode differs per platform).

- [ ] **Step 1: Implement `lib/tools/vscode.py`** (port of `vscode/setup.sh`)

```python
# lib/tools/vscode.py
"""VS Code: settings, keybindings, extensions.
  macOS              — symlinks into ~/Library/Application Support/Code/User
  Windows (Git Bash) — copies into $APPDATA/Code/User (symlinks need admin)
  WSL                — VS Code lives on the Windows host; run from Git Bash
"""
from __future__ import annotations

import filecmp
import os
from pathlib import Path
from typing import Tuple

from lib import core
from lib.core import Tool

_FILES = ("settings.json", "keybindings.json")


def _target() -> Tuple[Path, str]:
    """Return (user dir, mode) where mode is 'link' or 'copy'."""
    os_name = core.detect_os()
    if os_name == "macos":
        return Path.home() / "Library/Application Support/Code/User", "link"
    if os_name == "gitbash":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise core.DotfilesError("APPDATA not set; cannot locate VS Code user dir.")
        return Path(appdata) / "Code/User", "copy"
    raise core.DotfilesError("vscode: unsupported platform (macOS/Git Bash only).")


def _install_extensions() -> None:
    if not core.have("code"):
        core.warn("'code' CLI not found — skipping extension install.")
        core.warn("In VS Code: Cmd/Ctrl+Shift+P -> 'Shell Command: Install "
                  "code command in PATH', then re-run.")
        return
    core.info("Installing extensions (skipping already installed)...")
    installed = {line.strip().lower() for line in
                 core.run(["code", "--list-extensions"],
                          capture=True).stdout.splitlines()}
    ext_file = core.REPO_ROOT / "vscode" / "extensions.txt"
    for line in ext_file.read_text().splitlines():
        ext = line.split("#", 1)[0].strip()
        if not ext:
            continue
        if ext.lower() in installed:
            core.ok(f"{ext} already installed.")
            continue
        core.info(f"Installing {ext}...")
        result = core.run(["code", "--install-extension", ext], check=False)
        if result.returncode != 0:
            core.warn(f"Failed to install {ext} (continuing).")


def _post() -> None:
    target_dir, mode = _target()
    core.info(f"Applying VS Code settings + keybindings ({mode})...")
    for name in _FILES:
        src = core.REPO_ROOT / "vscode" / name
        if mode == "link":
            core.link_file(src, target_dir / name)
        else:
            core.copy_file(src, target_dir / name)
    _install_extensions()


def _uninstall() -> None:
    target_dir, mode = _target()
    for name in _FILES:
        src = core.REPO_ROOT / "vscode" / name
        if mode == "link":
            core.unlink_file(src, target_dir / name)
        else:
            core.uncopy_file(src, target_dir / name)
    core.info("Extensions left installed — remove in VS Code if unwanted.")


def _probe() -> bool:
    try:
        target_dir, mode = _target()
    except core.DotfilesError:
        return False
    for name in _FILES:
        src = core.REPO_ROOT / "vscode" / name
        t = target_dir / name
        if mode == "link":
            if not (t.is_symlink() and t.resolve() == src.resolve()):
                return False
        else:
            if not (t.exists() and filecmp.cmp(str(src), str(t), shallow=False)):
                return False
    return True


TOOL = Tool(
    name="vscode",
    doc="VS Code settings + keybindings + extensions",
    platforms=frozenset({"macos", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

- [ ] **Step 2: Register** — in `lib/tools/__init__.py` add `vscode` to the import and `vscode.TOOL` after `wezterm.TOOL`:

```python
from lib.tools import claude, nvim, starship, vscode, wezterm, zsh

_ALL = (
    zsh.TOOL,
    starship.TOOL,
    nvim.TOOL,
    wezterm.TOOL,
    vscode.TOOL,
    claude.TOOL,
)
```

- [ ] **Step 3: Run full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/tools
git commit -m "feat(installer): vscode spec (link on macOS, copy on Git Bash)"
```

---

### Task 7: agent-skills spec

**Files:**
- Create: `lib/tools/agent_skills.py`
- Modify: `lib/tools/__init__.py`

**Interfaces:**
- Consumes: `core.run`, `core.REPO_ROOT`; shells out to the untouched standalone `agent-skills/install.py`.
- Produces: `agent_skills.TOOL` named `"agent-skills"`.

- [ ] **Step 1: Implement `lib/tools/agent_skills.py`** (port of `agent-skills/setup.sh`)

```python
# lib/tools/agent_skills.py
"""Agent skills: symlink custom skills into ~/.claude/skills via the
standalone agent-skills/install.py (kept separate — it also handles community
skill fetching and the Copilot target on the work machine)."""
from __future__ import annotations

import sys
from pathlib import Path

from lib import core
from lib.core import Tool


def _skills_dir() -> Path:
    return Path.home() / ".claude" / "skills"


def _repo_symlinks():
    d = _skills_dir()
    if not d.is_dir():
        return
    for entry in d.iterdir():
        if not entry.is_symlink():
            continue
        try:
            dest = entry.resolve()
        except OSError:
            continue
        if core.REPO_ROOT in dest.parents:
            yield entry


def _post() -> None:
    core.run([sys.executable,
              str(core.REPO_ROOT / "agent-skills" / "install.py"),
              "--target", "claude", "--skills-only"])
    core.ok("Agent skills setup complete.")


def _uninstall() -> None:
    for entry in list(_repo_symlinks()):
        entry.unlink()
        core.ok(f"Removed {entry}")


def _probe() -> bool:
    return next(iter(_repo_symlinks()), None) is not None


TOOL = Tool(
    name="agent-skills",
    doc="Custom agent skills into ~/.claude/skills",
    platforms=frozenset({"macos", "linux"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

- [ ] **Step 2: Register** — add `agent_skills` import and `agent_skills.TOOL` after `claude.TOOL` in `lib/tools/__init__.py`.

- [ ] **Step 3: Run full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS.

- [ ] **Step 4: Commit**

```bash
git add lib/tools
git commit -m "feat(installer): agent-skills spec (delegates to standalone install.py)"
```

---

### Task 8: terminal-macos and iterm2 specs

**Files:**
- Create: `lib/tools/terminal_macos.py`, `lib/tools/iterm2.py`
- Modify: `lib/tools/__init__.py`

**Interfaces:**
- Consumes: `core.brew_install`, `core.run`, `core.copy_file/uncopy_file`, `core.REPO_ROOT`.
- Produces: `terminal_macos.TOOL` named `"terminal-macos"`, `iterm2.TOOL` named `"iterm2"`; both macOS-only, hook-driven, with `status_probe`.

- [ ] **Step 1: Implement `lib/tools/terminal_macos.py`** (port of `terminal-macos/setup.sh`; `defaults` left alone on uninstall, as decided)

```python
# lib/tools/terminal_macos.py
"""Terminal.app (macOS only): Solarized themes + MesloLGS NF font defaults."""
from __future__ import annotations

import time
from pathlib import Path

from lib import core
from lib.core import Tool

_THEMES_URL = ("https://github.com/lysyi3m/macos-terminal-themes/"
               "archive/refs/heads/master.zip")


def _default_theme() -> str:
    return core.run(["defaults", "read", "com.apple.Terminal",
                     "Default Window Settings"],
                    check=False, capture=True).stdout.strip()


def _post() -> None:
    core.brew_install("font-meslo-lg-nerd-font", cask=True)

    # ---- Download themes if not already downloaded ----
    themes_dir = Path.home() / "Downloads" / "macos-terminal-themes-master"
    if themes_dir.is_dir():
        core.ok("Terminal themes already downloaded.")
    else:
        core.info("Downloading Terminal.app themes...")
        zip_path = Path.home() / "Downloads" / "terminal-themes.zip"
        core.run(["curl", "-L", _THEMES_URL, "-o", str(zip_path)])
        core.run(["unzip", "-o", str(zip_path),
                  "-d", str(Path.home() / "Downloads")])
        zip_path.unlink()

    # ---- Load themes into Terminal if not already loaded ----
    core.run(["osascript", "-e", 'quit app "Terminal"'], check=False)
    time.sleep(2)
    loaded = core.run(["defaults", "read", "com.apple.Terminal",
                       "Window Settings"], check=False, capture=True).stdout
    for theme in sorted((themes_dir / "themes").glob("*.terminal")):
        if theme.stem not in loaded:
            core.run(["open", str(theme)])
    time.sleep(5)
    core.run(["osascript", "-e", 'quit app "Terminal"'], check=False)

    # ---- Default theme + font ----
    if "Solarized Dark" in _default_theme():
        core.ok("Terminal default theme already set.")
    else:
        core.run(["defaults", "write", "com.apple.Terminal",
                  "Default Window Settings", "-string", "Solarized Dark"])
        core.run(["defaults", "write", "com.apple.Terminal",
                  "Startup Window Settings", "-string", "Solarized Dark"])
    core.ok("Terminal.app setup complete. Restart Terminal for all changes.")


def _uninstall() -> None:
    core.skip("Terminal.app defaults and downloaded themes left alone — "
              "change theme in Terminal preferences if desired.")


def _probe() -> bool:
    return "Solarized Dark" in _default_theme()


TOOL = Tool(
    name="terminal-macos",
    doc="Terminal.app Solarized theme + font",
    platforms=frozenset({"macos"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

- [ ] **Step 2: Implement `lib/tools/iterm2.py`** (port of `iterm2/setup.sh`)

```python
# lib/tools/iterm2.py
"""iTerm2 (macOS only): app, shell integration, dynamic profile (theme + font)."""
from __future__ import annotations

import filecmp
from pathlib import Path

from lib import core
from lib.core import Tool

_GUID = "557036D3-EF41-4D30-A395-3F301A17D49B"


def _profile_src() -> Path:
    return core.REPO_ROOT / "iterm2" / "com.dotfiles.json"


def _profile_target() -> Path:
    return (Path.home() / "Library/Application Support/iTerm2/DynamicProfiles"
            / "com.dotfiles.json")


def _integration() -> Path:
    return Path.home() / ".iterm2_shell_integration.zsh"


def _post() -> None:
    if Path("/Applications/iTerm.app").is_dir():
        core.ok("iTerm2 already installed.")
    else:
        core.brew_install("iterm2", cask=True)
    core.brew_install("font-meslo-lg-nerd-font", cask=True)

    # ---- Shell integration (sourced by zsh/.zshrc when present) ----
    if _integration().exists():
        core.ok("iTerm2 shell integration already installed.")
    else:
        core.info("Installing iTerm2 shell integration...")
        core.run(["curl", "-fsSL", "https://iterm2.com/shell_integration/zsh",
                  "-o", str(_integration())])

    # ---- Dynamic profile (color theme + font) ----
    core.copy_file(_profile_src(), _profile_target())

    # ---- Default profile ----
    current = core.run(["defaults", "read", "com.googlecode.iterm2",
                        "Default Bookmark Guid"],
                       check=False, capture=True).stdout.strip()
    if current == _GUID:
        core.ok("iTerm2 default profile already set.")
    else:
        core.run(["defaults", "write", "com.googlecode.iterm2",
                  "Default Bookmark Guid", "-string", _GUID])
    core.ok("iTerm2 setup complete. Restart iTerm2 (Cmd+Q then relaunch).")


def _uninstall() -> None:
    core.uncopy_file(_profile_src(), _profile_target())
    if _integration().exists():
        _integration().unlink()
        core.ok(f"Removed {_integration()}")
    core.skip("iTerm2 app, fonts and defaults left alone.")


def _probe() -> bool:
    t = _profile_target()
    return t.exists() and filecmp.cmp(str(_profile_src()), str(t), shallow=False)


TOOL = Tool(
    name="iterm2",
    doc="iTerm2 + dynamic profile + shell integration",
    platforms=frozenset({"macos"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

- [ ] **Step 3: Register** — add `terminal_macos.TOOL` then `iterm2.TOOL` after `agent_skills.TOOL` in `lib/tools/__init__.py`.

- [ ] **Step 4: Run full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS.

- [ ] **Step 5: Commit**

```bash
git add lib/tools
git commit -m "feat(installer): terminal-macos + iterm2 specs"
```

---

### Task 9: citrix-vdi spec (with tested Karabiner rule removal)

**Files:**
- Create: `lib/tools/citrix_vdi.py`
- Modify: `lib/tools/__init__.py`
- Test: `tests/test_citrix.py`

**Interfaces:**
- Consumes: `core.brew_install`, `core.copy_file/uncopy_file`, `core.REPO_ROOT`.
- Produces: `citrix_vdi.TOOL` named `"citrix-vdi"`; pure function `remove_enabled_rules(rules_file: Path, config_file: Path) -> int` (port of the python embedded in `citrix-vdi/uninstall.sh`).

- [ ] **Step 1: Write the failing test**

```python
# tests/test_citrix.py
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from lib.tools import citrix_vdi


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data))


class RemoveEnabledRulesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.rules = root / "karabiner-citrix.json"
        self.config = root / "karabiner.json"
        write(self.rules, {"rules": [{"description": "Citrix VDI rule A"},
                                     {"description": "NuPhy rule B"}]})

    def test_removes_only_our_rules(self):
        write(self.config, {"profiles": [{"complex_modifications": {"rules": [
            {"description": "Citrix VDI rule A"},
            {"description": "user's own rule"},
            {"description": "NuPhy rule B"},
        ]}}]})
        removed = citrix_vdi.remove_enabled_rules(self.rules, self.config)
        self.assertEqual(removed, 2)
        config = json.loads(self.config.read_text())
        kept = config["profiles"][0]["complex_modifications"]["rules"]
        self.assertEqual(kept, [{"description": "user's own rule"}])

    def test_no_rules_enabled_leaves_file_untouched(self):
        write(self.config, {"profiles": [{"complex_modifications": {"rules": [
            {"description": "user's own rule"}]}}]})
        before = self.config.read_text()
        self.assertEqual(citrix_vdi.remove_enabled_rules(self.rules, self.config), 0)
        self.assertEqual(self.config.read_text(), before)

    def test_profile_without_complex_modifications(self):
        write(self.config, {"profiles": [{"name": "bare"}]})
        self.assertEqual(citrix_vdi.remove_enabled_rules(self.rules, self.config), 0)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python3 -m unittest tests.test_citrix -v`
Expected: ERROR — `ImportError: cannot import name 'citrix_vdi'`.

- [ ] **Step 3: Implement `lib/tools/citrix_vdi.py`** (ports `citrix-vdi/setup.sh` + `uninstall.sh`)

```python
# lib/tools/citrix_vdi.py
"""Citrix VDI (macOS only): Karabiner-Elements + a Citrix-scoped rule so
Windows IDE shortcuts (Alt+F1, Alt+F7, Shift+F6, ...) reach the VDI intact.
Runs on the Mac — nothing is installed inside the VDI."""
from __future__ import annotations

import filecmp
import json
import shutil
from datetime import date
from pathlib import Path

from lib import core
from lib.core import Tool


def _rules_src() -> Path:
    return core.REPO_ROOT / "citrix-vdi" / "karabiner-citrix.json"


def _assets_file() -> Path:
    return (Path.home() / ".config/karabiner/assets/complex_modifications"
            / "karabiner-citrix.json")


def _karabiner_config() -> Path:
    return Path.home() / ".config/karabiner/karabiner.json"


def remove_enabled_rules(rules_file: Path, config_file: Path) -> int:
    """Remove our rules (matched by description) from every profile in the
    live karabiner.json. Returns the number of rules removed; the file is
    rewritten only when something was removed."""
    ours = {r["description"] for r in
            json.loads(rules_file.read_text())["rules"]}
    config = json.loads(config_file.read_text())
    removed = 0
    for profile in config.get("profiles", []):
        rules = profile.get("complex_modifications", {}).get("rules", [])
        kept = [r for r in rules if r.get("description") not in ours]
        removed += len(rules) - len(kept)
        if len(kept) != len(rules):
            profile["complex_modifications"]["rules"] = kept
    if removed:
        config_file.write_text(json.dumps(config, indent=4) + "\n")
    return removed


def _post() -> None:
    if Path("/Applications/Karabiner-Elements.app").is_dir():
        core.ok("Karabiner-Elements already installed.")
    else:
        core.brew_install("karabiner-elements", cask=True)
    core.copy_file(_rules_src(), _assets_file())
    core.ok("citrix-vdi setup complete. One-time manual steps remain "
            "(Karabiner rule enable + Citrix keyboard preferences) — "
            "see citrix-vdi/README.md.")


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
        removed = remove_enabled_rules(_rules_src(), config)
        if removed:
            core.ok(f"Removed {removed} enabled rule(s) from karabiner.json "
                    "(Karabiner reloads automatically).")
        else:
            core.ok("No Citrix/NuPhy rules enabled in karabiner.json.")
    # ---- 2. Remove the rule file from the assets folder ----
    if _assets_file().exists():
        _assets_file().unlink()
        core.ok(f"Removed {_assets_file()}")
    else:
        core.ok("Rule file already absent from assets folder.")
    # ---- 3. Manual follow-ups ----
    core.ok("citrix-vdi uninstall complete. Remaining manual steps:")
    print("  1. Citrix Workspace -> Preferences -> Keyboard -> Keyboard input"
          " mode -> Automatic (then reconnect the VDI session).")
    print("  2. NuPhy: free to use any mode and connection again.")
    print("  3. Optional, if Karabiner-Elements is otherwise unused: "
          "Karabiner-Elements -> Settings -> uninstall section, or "
          "brew uninstall --cask karabiner-elements")


def _probe() -> bool:
    t = _assets_file()
    return t.exists() and filecmp.cmp(str(_rules_src()), str(t), shallow=False)


TOOL = Tool(
    name="citrix-vdi",
    doc="Karabiner Citrix/NuPhy keyboard rules",
    platforms=frozenset({"macos"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

- [ ] **Step 4: Register** — add `citrix_vdi.TOOL` last in `_ALL`. Final registry order: `zsh, starship, nvim, wezterm, vscode, claude, agent-skills, terminal-macos, iterm2, citrix-vdi`.

- [ ] **Step 5: Run full suite**

Run: `python3 -m unittest discover -s tests -v`
Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add lib/tools tests/test_citrix.py
git commit -m "feat(installer): citrix-vdi spec with tested karabiner rule removal"
```

---

### Task 10: CLI entry point `install.py`

**Files:**
- Create: `install.py` (repo root, executable)
- Test: `tests/test_cli.py`

**Interfaces:**
- Consumes: `lib.core`, `lib.ui`, `lib.tools.REGISTRY`.
- Produces: `main(argv: Optional[list] = None) -> int`; commands `install [tool...]`, `uninstall <tool...>`, `status`, `list`; no args → interactive; `--yes` skips confirmations.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_cli.py
from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock

import install
from lib import core, tools


def run_main(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = install.main(argv)
    return code, out.getvalue()


class CliTest(unittest.TestCase):
    def test_list(self):
        code, out = run_main(["list"])
        self.assertEqual(code, 0)
        for name in tools.REGISTRY:
            self.assertIn(name, out)

    def test_status_lists_all_tools(self):
        code, out = run_main(["status"])
        self.assertEqual(code, 0)
        for name in tools.REGISTRY:
            self.assertIn(name, out)

    def test_unknown_tool_fails(self):
        code, _ = run_main(["install", "nosuchtool"])
        self.assertEqual(code, 1)

    def test_uninstall_requires_tools(self):
        code, _ = run_main(["uninstall"])
        self.assertEqual(code, 1)

    def test_install_runs_batch(self):
        with mock.patch.object(core, "install_tool") as it:
            code, _ = run_main(["install", "starship"])
        self.assertEqual(code, 0)
        it.assert_called_once_with(tools.REGISTRY["starship"])

    def test_uninstall_with_yes_skips_prompt(self):
        with mock.patch.object(core, "uninstall_tool") as ut:
            code, _ = run_main(["--yes", "uninstall", "starship"])
        self.assertEqual(code, 0)
        ut.assert_called_once_with(tools.REGISTRY["starship"])

    def test_batch_failure_continues_and_exits_1(self):
        with mock.patch.object(core, "install_tool",
                               side_effect=core.DotfilesError("boom")):
            code, out = run_main(["install", "starship", "claude"])
        self.assertEqual(code, 1)
        self.assertIn("starship", out)
        self.assertIn("claude", out)

    def test_not_applicable_tool_skipped_on_install_all(self):
        with mock.patch.object(core, "install_tool") as it, \
             mock.patch.object(install, "current_os", return_value="linux"):
            code, _ = run_main(["install"])
        self.assertEqual(code, 0)
        installed = {call.args[0].name for call in it.call_args_list}
        self.assertNotIn("citrix-vdi", installed)
        self.assertIn("zsh", installed)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `python3 -m unittest tests.test_cli -v`
Expected: ERROR — `ModuleNotFoundError: No module named 'install'`.

- [ ] **Step 3: Implement `install.py`**

```python
#!/usr/bin/env python3
"""Dotfiles installer. Interactive:
    ./install.py
Non-interactive:
    ./install.py install [tool...]     # no tools = all applicable
    ./install.py uninstall <tool...>   # explicit tools required
    ./install.py status | list
    ./install.py --yes ...             # skip confirmation prompts
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import core, ui                     # noqa: E402
from lib.tools import REGISTRY               # noqa: E402


def current_os() -> str:
    return core.detect_os()


def applicable(tool: core.Tool, os_name: str) -> bool:
    return os_name in tool.platforms


def resolve_tools(names: List[str], os_name: str) -> List[core.Tool]:
    """Map CLI names to Tools; raise DotfilesError on unknown names."""
    unknown = [n for n in names if n not in REGISTRY]
    if unknown:
        raise core.DotfilesError(
            f"Unknown tool(s): {', '.join(unknown)}. "
            f"Available: {' '.join(REGISTRY)}")
    return [REGISTRY[n] for n in names]


def run_batch(action: str, batch: List[core.Tool], os_name: str) -> int:
    failures = []
    for tool in batch:
        if not applicable(tool, os_name):
            core.skip(f"{tool.name} is not applicable on {os_name}, skipping.")
            continue
        print(f"\n===== {tool.name} =====")
        try:
            if action == "install":
                core.install_tool(tool)
            else:
                core.uninstall_tool(tool)
        except (core.DotfilesError, subprocess.CalledProcessError,
                OSError) as exc:
            core.warn(f"{tool.name} failed: {exc}")
            failures.append(tool.name)
    print()
    if failures:
        core.warn(f"Failed: {', '.join(failures)}")
        return 1
    if action == "install":
        core.ok("All done. Open a new terminal for shell changes to take effect.")
    else:
        core.ok("Uninstall done. Brew packages were left installed — "
                "remove manually if unwanted.")
    return 0


def cmd_status(os_name: str) -> int:
    for tool in REGISTRY.values():
        if applicable(tool, os_name):
            status = core.tool_status(tool)
        else:
            status = f"{'/'.join(sorted(tool.platforms))} only"
        print(f"  {tool.name:<15} {status:<15} {tool.doc}")
    return 0


def interactive(os_name: str, assume_yes: bool) -> int:
    print(f"Dotfiles installer — {os_name}")
    items = []
    for tool in REGISTRY.values():
        if applicable(tool, os_name):
            items.append(ui.MenuItem(tool.name, core.tool_status(tool), True))
        else:
            items.append(ui.MenuItem(
                tool.name, f"{'/'.join(sorted(tool.platforms))} only", False))
    selected = ui.interactive_select(items)
    if not selected:
        print("Nothing selected.")
        return 0
    batch = [list(REGISTRY.values())[i] for i in selected]
    action = ui.choose_action()
    if action == "quit":
        return 0
    names = ", ".join(t.name for t in batch)
    if action == "uninstall" and not assume_yes:
        if not ui.confirm(f"Remove links/configs for: {names}?"):
            print("Aborted.")
            return 0
    return run_batch(action, batch, os_name)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Dotfiles installer")
    parser.add_argument("--yes", action="store_true",
                        help="skip confirmation prompts")
    sub = parser.add_subparsers(dest="command")
    p_install = sub.add_parser("install", help="install tools (default: all)")
    p_install.add_argument("tools", nargs="*")
    p_uninstall = sub.add_parser("uninstall", help="uninstall tools")
    p_uninstall.add_argument("tools", nargs="+")
    sub.add_parser("status", help="show per-tool status")
    sub.add_parser("list", help="list tool names")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse errors (e.g. uninstall w/o tools)
        return 1 if exc.code else 0

    try:
        os_name = current_os()
    except core.DotfilesError as exc:
        core.warn(str(exc))
        return 1

    try:
        if args.command is None:
            return interactive(os_name, args.yes)
        if args.command == "list":
            for name in REGISTRY:
                print(name)
            return 0
        if args.command == "status":
            return cmd_status(os_name)
        if args.command == "install":
            batch = (resolve_tools(args.tools, os_name) if args.tools
                     else list(REGISTRY.values()))
            return run_batch("install", batch, os_name)
        # uninstall
        batch = resolve_tools(args.tools, os_name)
        names = ", ".join(t.name for t in batch)
        if not args.yes and sys.stdin.isatty():
            if not ui.confirm(f"Remove links/configs for: {names}?"):
                print("Aborted.")
                return 0
        return run_batch("uninstall", batch, os_name)
    except core.DotfilesError as exc:
        core.warn(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Make executable and run tests**

Run: `chmod +x install.py && python3 -m unittest discover -s tests -v`
Expected: all PASS.

- [ ] **Step 5: Manual smoke**

Run: `./install.py list && ./install.py status`
Expected: 10 tools listed; status column shows real link state (zsh/starship/etc. likely `installed`).

- [ ] **Step 6: Commit**

```bash
git add install.py tests/test_cli.py
git commit -m "feat(installer): CLI entry point with interactive menu"
```

---

### Task 11: Delete shell layer, update docs, final verification

**Files:**
- Delete: `install.sh`, `lib/common.sh`, `zsh/setup.sh`, `starship/setup.sh`, `nvim/setup.sh`, `wezterm/setup.sh`, `vscode/setup.sh`, `claude/setup.sh`, `agent-skills/setup.sh`, `terminal-macos/setup.sh`, `iterm2/setup.sh`, `citrix-vdi/setup.sh`, `citrix-vdi/uninstall.sh`
- Modify: `README.md` and any per-tool `README.md` referencing the deleted scripts

**Interfaces:**
- Consumes: everything prior; repo must be fully functional through `install.py` alone.

- [ ] **Step 1: Verify nothing else calls the shell scripts**

Run: `grep -rn --include="*.sh" --include="*.py" --include="*.md" -e "setup.sh" -e "install.sh" -e "common.sh" -e "uninstall.sh" . | grep -v docs/superpowers | grep -v archived | grep -v .git/`
Expected: hits only in the files being deleted and in READMEs (updated next). Note: `claude/settings.json` or hooks referencing `statusline-command.sh` are fine — that file stays.

- [ ] **Step 2: Delete**

```bash
git rm install.sh lib/common.sh \
  zsh/setup.sh starship/setup.sh nvim/setup.sh wezterm/setup.sh \
  vscode/setup.sh claude/setup.sh agent-skills/setup.sh \
  terminal-macos/setup.sh iterm2/setup.sh citrix-vdi/setup.sh \
  citrix-vdi/uninstall.sh
```

- [ ] **Step 3: Update `README.md`** — replace the quick-start section's `./install.sh [tool...]` usage with:

```markdown
## Install

```bash
git clone <this repo> ~/Dev/.dotfiles && cd ~/Dev/.dotfiles
./install.py            # interactive: pick tools, install or uninstall
```

Non-interactive:

```bash
./install.py install            # everything applicable to this OS
./install.py install zsh nvim   # subset
./install.py uninstall vscode   # remove links/configs (brew packages stay)
./install.py status             # what's installed
```

Requires only the system `python3` (3.9+). Uninstall removes symlinks and
repo-copied configs and restores `.bak-*` backups; brew packages are listed
for manual removal.
```

Then update every per-tool `README.md` line found in Step 1 that says `./<tool>/setup.sh` or `bash setup.sh` to the equivalent `./install.py install <tool>` (and `./install.py uninstall citrix-vdi` in `citrix-vdi/README.md`).

- [ ] **Step 4: Full suite + smoke + real round-trip on one safe tool**

```bash
python3 -m unittest discover -s tests -v
./install.py status
./install.py install starship
./install.py --yes uninstall starship
./install.py install starship
```

Expected: tests PASS; starship uninstall removes `~/.config/starship.toml` link (restoring any backup), reinstall relinks. Confirm with `ls -la ~/.config/starship.toml` after each step.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "feat(installer)!: replace shell install layer with install.py

BREAKING CHANGE: install.sh and per-tool setup.sh removed; use ./install.py"
```

---

## Self-Review Notes

- Spec coverage: engine (Tasks 1–2), UI (3), all ten tools (4–9), CLI + interactive + batch error handling (10), shell deletion + docs (11). Uninstall symmetry tested in Task 2; foreign-file safety in Task 1; registry sanity in Task 4 grows to cover every later spec.
- `PARTIAL` status appears in `status`/menu output via `tool_status`; no extra handling needed.
- Interfaces consistent: `core.Link(src, target)` strings; hooks are zero-arg callables; `REGISTRY` is name→Tool ordered dict; `install.main(argv) -> int`.
- Git Bash support is best-effort parity with the old vscode/setup.sh (`detect_os` maps Windows→"gitbash"); not smoke-testable on this machine — noted, acceptable.
