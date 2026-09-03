# lib/tools/lazygit.py
"""lazygit: terminal UI for git, with the repo config symlinked in.

lazygit is not macOS-only — brew covers macOS and Linux/WSL, which is the
same pair every other shell tool in this repo targets. (On the Windows side
proper it ships via winget/scoop; that is out of scope here, same as zsh.)

The config directory is not the same everywhere, so the link target is
resolved at install time instead of being a static Link:

  $XDG_CONFIG_HOME set   — $XDG_CONFIG_HOME/lazygit/config.yml (any OS)
  macOS                  — ~/Library/Application Support/lazygit/config.yml
  Linux/WSL              — ~/.config/lazygit/config.yml

`lazygit --print-config-dir` reports the same path, so it is the check to run
when a future lazygit changes this.
"""
from __future__ import annotations

import os
from pathlib import Path

from lib import core
from lib.core import Tool

_NAME = "config.yml"


def _src() -> Path:
    return core.REPO_ROOT / "lazygit" / _NAME


def _config_dir() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        return Path(xdg).expanduser() / "lazygit"
    if core.detect_os() == "macos":
        return Path.home() / "Library" / "Application Support" / "lazygit"
    return Path.home() / ".config" / "lazygit"


def _target() -> Path:
    return _config_dir() / _NAME


def _post() -> None:
    core.link_file(_src(), _target())


def _uninstall() -> None:
    core.unlink_file(_src(), _target())


def _probe() -> bool:
    target = _target()
    return target.is_symlink() and target.resolve() == _src().resolve()


TOOL = Tool(
    name="lazygit",
    doc="lazygit terminal UI + config",
    platforms=frozenset({"macos", "linux"}),
    brew=("lazygit",),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
