# lib/tools/copilot.py
"""GitHub Copilot: personal instruction files.

  macOS/Linux        — symlinks into ~/.copilot/instructions
  Windows (Git Bash) — copies into ~/.copilot/instructions (symlinks need
                       admin); re-run after editing a file to refresh them.

Instructions in ~/.copilot/instructions apply to every repository on the
machine, so work repos need no commit, and they are read by all three Copilot
surfaces: the CLI, VS Code and JetBrains. VS Code's docs are explicit that
these Agent Host folders do NOT roam through Settings Sync, which is why
dotfiles installs them per machine.

The Copilot extension itself is not installed here: from VS Code 1.139 it
ships built in (see vscode/extensions.txt). Its *settings* live in
vscode/settings.json, which is VS Code-specific; this module is the part that
serves every surface.
"""
from __future__ import annotations

import filecmp
from pathlib import Path
from typing import Tuple

from lib import core
from lib.core import Tool

# Every *.instructions.md in the repo's copilot/ directory is installed.
_SRC_DIR = "copilot"
_SUFFIX = ".instructions.md"


def _sources() -> list[Path]:
    """Instruction files shipped by this repo, sorted for stable output."""
    return sorted((core.REPO_ROOT / _SRC_DIR).glob(f"*{_SUFFIX}"))


def _target() -> Tuple[Path, str]:
    """Return (instructions dir, mode) where mode is 'link' or 'copy'."""
    mode = "copy" if core.detect_os() == "gitbash" else "link"
    return Path.home() / ".copilot" / "instructions", mode


def _post() -> None:
    target_dir, mode = _target()
    sources = _sources()
    if not sources:
        core.warn(f"No {_SUFFIX} files in {_SRC_DIR}/ — nothing to install.")
        return
    core.info(f"Applying Copilot instructions ({mode})...")
    target_dir.mkdir(parents=True, exist_ok=True)
    for src in sources:
        if mode == "link":
            core.link_file(src, target_dir / src.name)
        else:
            core.copy_file(src, target_dir / src.name)
    core.info("These apply to every repository. Scoped rules belong in their "
              "own file with a narrower applyTo.")


def _uninstall() -> None:
    target_dir, mode = _target()
    for src in _sources():
        if mode == "link":
            core.unlink_file(src, target_dir / src.name)
        else:
            core.uncopy_file(src, target_dir / src.name)


def _probe() -> bool:
    target_dir, mode = _target()
    sources = _sources()
    if not sources:
        return False
    for src in sources:
        t = target_dir / src.name
        if mode == "link":
            if not (t.is_symlink() and t.resolve() == src.resolve()):
                return False
        elif not (t.exists()
                  and filecmp.cmp(str(src), str(t), shallow=False)):
            return False
    return True


TOOL = Tool(
    name="copilot",
    doc="Copilot personal instruction files (~/.copilot/instructions)",
    platforms=frozenset({"macos", "linux", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
