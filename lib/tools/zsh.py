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
