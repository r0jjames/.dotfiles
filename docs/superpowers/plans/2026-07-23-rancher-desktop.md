# Rancher Desktop Tool Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `rancher-desktop` as a dotfiles-managed tool (cask install + setup reminders), retire Docker Desktop and OrbStack on this machine, and actually run the install.

**Architecture:** One new file, `lib/tools/rancher_desktop.py`, registered in `lib/tools/__init__.py`, following the existing `maven.py`/`iterm2.py` shape (`Tool` dataclass with `casks`, `post_install`, `extra_uninstall`, `status_probe`). No config files to symlink, so no dedicated subfolder.

**Tech Stack:** Python 3.9+ stdlib only (matches `lib/core.py`), Homebrew casks, `rdctl` (Rancher Desktop's bundled CLI).

## Global Constraints

- macOS only (`platforms=frozenset({"macos"})`) — spec scope is this machine.
- Never auto-remove other software (Docker Desktop, OrbStack) — print instructions only, per repo convention (`maven.py`'s uninstall leaves SDKMAN candidates in place).
- Engine mode: moby/dockerd. Kubernetes: disabled. Both set via `rdctl set --container-engine.name moby --kubernetes.enabled=false`, confirmed against Rancher Desktop's official `rdctl` command reference (not guessed).
- Test runner for this repo: `python3 -m unittest discover -s tests` (52 tests pass on main before this work; no pytest installed).

---

### Task 1: `rancher-desktop` tool module + registry entry

**Files:**
- Create: `lib/tools/rancher_desktop.py`
- Modify: `lib/tools/__init__.py`

**Interfaces:**
- Consumes: `lib.core.Tool`, `lib.core.Link` (unused here), `lib.core.run`, `lib.core.ensure_brew`, `lib.core.info`, `lib.core.warn`, `lib.core.skip` — all existing, signatures per `lib/core.py`.
- Produces: `lib.tools.rancher_desktop.TOOL` (a `Tool` instance), consumed by `lib/tools/__init__.py`'s `_ALL` tuple and `REGISTRY` dict. Later tasks don't depend on any new symbol beyond `TOOL`.

- [ ] **Step 1: Write `lib/tools/rancher_desktop.py`**

```python
# lib/tools/rancher_desktop.py
"""Rancher Desktop: container engine (dockerd/moby), Kubernetes disabled.
Replaces Docker Desktop and OrbStack as the local Docker-compatible engine
on this machine; neither was ever a dotfiles-managed tool."""
from __future__ import annotations

from pathlib import Path

from lib import core
from lib.core import Tool

_APP_PATH = Path("/Applications/Rancher Desktop.app")
_DOCKER_APP_PATH = Path("/Applications/Docker.app")

_RDCTL_SET_CMD = (
    "rdctl set --container-engine.name moby --kubernetes.enabled=false")


def _post() -> None:
    if _DOCKER_APP_PATH.is_dir():
        core.skip(
            f"{_DOCKER_APP_PATH} is not brew-managed — quit Docker "
            "Desktop and remove it manually (drag to Trash) when ready.")

    brew = core.ensure_brew()
    orbstack_listed = core.run([brew, "list", "--cask", "orbstack"],
                               check=False, capture=True)
    if orbstack_listed.returncode == 0:
        core.skip("orbstack cask still installed — remove it yourself "
                  "with: brew uninstall --cask orbstack")

    pgrep = core.run(["pgrep", "-x", "Docker"], check=False, capture=True)
    if pgrep.returncode == 0:
        core.warn("Docker Desktop is running — quit it before starting "
                  "Rancher Desktop (both bind the same docker socket path).")

    core.info(
        "Launch Rancher Desktop, complete the first-run setup, then run:\n"
        f"    {_RDCTL_SET_CMD}\n"
        "to set the container engine to moby and disable Kubernetes "
        "(rdctl's backend API isn't reachable until after first launch, "
        "so this can't be scripted here).")


def _uninstall() -> None:
    core.skip("Rancher Desktop app left installed — remove the "
              "rancher-desktop cask yourself if desired.")


def _probe() -> bool:
    return _APP_PATH.is_dir()


TOOL = Tool(
    name="rancher-desktop",
    doc="Rancher Desktop (dockerd/moby engine, Kubernetes disabled)",
    platforms=frozenset({"macos"}),
    casks=("rancher-desktop",),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

- [ ] **Step 2: Register it in `lib/tools/__init__.py`**

Current file:

```python
"""Tool registry. Order here is menu/run order (mirrors old ALL_TOOLS)."""
from __future__ import annotations

from lib.tools import (agent_skills, citrix_vdi, claude, iterm2, maven, nvim,
                       starship, terminal_macos, vscode, wezterm, zsh)

_ALL = (
    zsh.TOOL,
    starship.TOOL,
    nvim.TOOL,
    wezterm.TOOL,
    vscode.TOOL,
    claude.TOOL,
    agent_skills.TOOL,
    maven.TOOL,
    terminal_macos.TOOL,
    iterm2.TOOL,
    citrix_vdi.TOOL,
)

REGISTRY = {t.name: t for t in _ALL}
```

Change the import line and `_ALL` tuple (add `rancher_desktop` alphabetically to the import, append `rancher_desktop.TOOL` at the end of `_ALL` since it's the newest/most niche tool, matching how `citrix_vdi` was appended last):

```python
"""Tool registry. Order here is menu/run order (mirrors old ALL_TOOLS)."""
from __future__ import annotations

from lib.tools import (agent_skills, citrix_vdi, claude, iterm2, maven, nvim,
                       rancher_desktop, starship, terminal_macos, vscode,
                       wezterm, zsh)

_ALL = (
    zsh.TOOL,
    starship.TOOL,
    nvim.TOOL,
    wezterm.TOOL,
    vscode.TOOL,
    claude.TOOL,
    agent_skills.TOOL,
    maven.TOOL,
    terminal_macos.TOOL,
    iterm2.TOOL,
    citrix_vdi.TOOL,
    rancher_desktop.TOOL,
)

REGISTRY = {t.name: t for t in _ALL}
```

- [ ] **Step 3: Run the test suite to verify the new tool passes generic registry checks**

Run: `python3 -m unittest discover -s tests`
Expected: `Ran 53 tests in ...s` / `OK` (one more test than the current 52, since `test_registry.py`'s per-tool checks now iterate over `rancher-desktop` too — no new test file needed, matching `maven`/`iterm2` which also have no dedicated test file).

- [ ] **Step 4: Manually confirm status output**

Run: `./install.py status`
Expected: a line for `rancher-desktop` reading `not installed` (cask not yet installed) with doc text `Rancher Desktop (dockerd/moby engine, Kubernetes disabled)`.

- [ ] **Step 5: Commit**

```bash
git add lib/tools/rancher_desktop.py lib/tools/__init__.py
git commit -m "feat(rancher-desktop): add tool for cask install + engine setup reminder"
```

---

### Task 2: Docs — README table row + CLAUDE.md MCP_DOCKER note

**Files:**
- Modify: `README.md` (tool table, currently line 65 is the `maven` row)
- Modify: `claude/CLAUDE.md:10-11`

**Interfaces:**
- Consumes: nothing from Task 1's code (doc-only change, but references the `rancher-desktop` name chosen there).
- Produces: nothing consumed by later tasks.

- [ ] **Step 1: Add a README table row**

In `README.md`, the table (around line 65) has this row for `maven`:

```
| `maven` | Maven build tool, via SDKMAN | macOS, WSL |
```

Add a new row directly after the `citrix-vdi` row (line 68), keeping the same no-folder-link style as `maven`'s row since `rancher-desktop` has no dedicated subfolder:

```
| `rancher-desktop` | Rancher Desktop (dockerd engine, Kubernetes disabled) — replaces Docker Desktop/OrbStack | macOS only |
```

- [ ] **Step 2: Reword the MCP_DOCKER note in `claude/CLAUDE.md`**

Current text (lines 10-11):

```
- The `MCP_DOCKER` MCP server only connects when Docker Desktop is running;
  a failed connection there is expected, not a config bug.
```

Replace with:

```
- The `MCP_DOCKER` MCP server only connects when Rancher Desktop is
  running; a failed connection there is expected, not a config bug.
```

- [ ] **Step 3: Verify the symlink still resolves correctly**

Run: `readlink ~/.claude/CLAUDE.md`
Expected: points at `/Users/roj/Dev/.dotfiles/claude/CLAUDE.md` (editing the repo file is sufficient — no copy step needed, this confirms the edit is live without a separate deploy action).

- [ ] **Step 4: Commit**

```bash
git add README.md claude/CLAUDE.md
git commit -m "docs(rancher-desktop): note in README table, update MCP_DOCKER reference"
```

---

### Task 3: Run the install on this machine

**Files:** none (no code changes — this is the actual migration execution the user asked for).

**Interfaces:**
- Consumes: `./install.py install rancher-desktop` (CLI entry point from `install.py`, unchanged by this plan).
- Produces: nothing for later tasks — this is the terminal task.

- [ ] **Step 1: Run the installer for the new tool**

Run: `./install.py install rancher-desktop`
Expected output includes: `===== rancher-desktop =====`, a Homebrew cask install of `rancher-desktop` (may take a few minutes), the Docker.app-not-brew-managed skip line, the orbstack skip line (orbstack is currently installed per `brew list --cask`), and the "Launch Rancher Desktop..." reminder with the exact `rdctl set` command. Ends with `All done. Open a new terminal for shell changes to take effect.`

- [ ] **Step 2: Quit Docker Desktop if it's running**

Run: `pgrep -x Docker && osascript -e 'quit app "Docker"' || echo "not running"`
Expected: either quits Docker Desktop or prints `not running`.

- [ ] **Step 3: Launch Rancher Desktop and complete first-run setup**

Run: `open -a "Rancher Desktop"`
Expected: app opens; manually step through its first-run wizard (license, admin access prompt for networking helper) in the GUI — this part is inherently interactive and can't be scripted.

- [ ] **Step 4: Set engine mode and disable Kubernetes**

Run: `rdctl set --container-engine.name moby --kubernetes.enabled=false`
Expected: command exits 0 (may take a few seconds while the backend restarts the engine).

- [ ] **Step 5: Verify the docker context**

Run: `docker context ls`
Expected: a `rancher-desktop` row present, `unix:///Users/roj/.rd/docker.sock` (or similar `.rd` path) as its endpoint, marked as current (`*`) once Rancher Desktop finishes switching it.

- [ ] **Step 6: Remove OrbStack**

Run: `brew uninstall --cask orbstack`
Expected: OrbStack cask removed. Confirm with `brew list --cask | grep -i orbstack` returning nothing.

- [ ] **Step 7: Remove Docker Desktop**

Docker.app is not brew-managed, so this is manual: quit it if still running, then move `/Applications/Docker.app` to Trash. Confirm with `ls /Applications | grep -i docker` returning nothing.

- [ ] **Step 8: Final status check**

Run: `./install.py status`
Expected: `rancher-desktop` now shows `installed`.
