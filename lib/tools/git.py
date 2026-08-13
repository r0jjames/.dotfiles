# lib/tools/git.py
"""Git: the global excludes file (~/.config/git/ignore).

Patterns that should never be committed in ANY repository live here —
per-repo .gitignore edits are avoided that way. Notably `.tours/`, where
the walkthrough skills write CodeTour files.

  macOS/Linux        — symlink into ~/.config/git
  Windows (Git Bash) — copy (symlinks need admin); re-run after editing.

core.excludesFile is pointed at the installed file only when unset, so an
existing git configuration is never overwritten.
"""
from __future__ import annotations

import filecmp
from pathlib import Path
from typing import Tuple

from lib import core
from lib.core import Tool

_NAME = "ignore"
_CONFIG_KEY = "core.excludesFile"


def _src() -> Path:
    return core.REPO_ROOT / "git" / _NAME


def _target() -> Tuple[Path, str]:
    """Return (excludes file, mode) where mode is 'link' or 'copy'."""
    mode = "copy" if core.detect_os() == "gitbash" else "link"
    return Path.home() / ".config" / "git" / _NAME, mode


def _git_config(*args: str) -> str:
    """Run `git config --global ...`; empty string when git is missing or
    the key is unset (git exits 1 for an unset key)."""
    if not core.have("git"):
        return ""
    result = core.run(["git", "config", "--global", *args],
                      check=False, capture=True)
    return result.stdout.strip() if result.returncode == 0 else ""


def _point_git_at(target: Path) -> None:
    current = _git_config("--get", _CONFIG_KEY)
    if not core.have("git"):
        core.warn("git not found — set core.excludesFile manually:")
        print(f"    git config --global {_CONFIG_KEY} {target}")
        return
    if not current:
        core.run(["git", "config", "--global", _CONFIG_KEY, str(target)])
        core.ok(f"Set {_CONFIG_KEY} -> {target}")
        return
    if Path(current).expanduser() == target:
        core.ok(f"{_CONFIG_KEY} already points at {target}.")
        return
    core.warn(f"{_CONFIG_KEY} points at {current} — leaving it alone.")
    core.warn("Point it at the repo copy yourself if that is what you want:")
    print(f"    git config --global {_CONFIG_KEY} {target}")


def _post() -> None:
    target, mode = _target()
    core.info(f"Applying global git ignore ({mode})...")
    if mode == "link":
        core.link_file(_src(), target)
    else:
        core.copy_file(_src(), target)
    _point_git_at(target)


def _uninstall() -> None:
    target, mode = _target()
    if mode == "link":
        core.unlink_file(_src(), target)
    else:
        core.uncopy_file(_src(), target)
    core.info(f"{_CONFIG_KEY} left as is — unset it manually if unwanted:")
    print(f"    git config --global --unset {_CONFIG_KEY}")


def _probe() -> bool:
    target, mode = _target()
    if mode == "link":
        return target.is_symlink() and target.resolve() == _src().resolve()
    return target.exists() and filecmp.cmp(str(_src()), str(target),
                                           shallow=False)


TOOL = Tool(
    name="git",
    doc="Global git ignore (.tours/, agent leftovers)",
    platforms=frozenset({"macos", "linux", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
