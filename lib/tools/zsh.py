# lib/tools/zsh.py
"""Zsh shell stack: zsh, modern CLI tools, plugins, ~/.zshrc (symlinked).

Ubuntu packages every one of these, so apt covers the whole list -- including
the two zsh plugins, which land in /usr/share instead of Homebrew's prefix
(.zshrc looks in both). Two of them install under a different command name
than the rest of the world uses, and get shimmed onto PATH: see lib/apt.py.
"""
from __future__ import annotations

import os
import shutil

from lib import core
from lib.core import Link, Tool

# Debian renames these two binaries to dodge package-name collisions.
_RENAMED = (("bat", "batcat"), ("fd", "fdfind"))


def _linux_post() -> None:
    """Linux only: PATH shims for Debian's renamed binaries, then make zsh
    the login shell."""
    if core.detect_os() != "linux":
        return
    from lib import apt

    for name, packaged in _RENAMED:
        apt.shim(name, packaged)
    apt.warn_if_local_bin_not_on_path()

    zsh_path = shutil.which("zsh")
    if zsh_path is None:
        core.warn("zsh not found after install — skipping login-shell change.")
        return
    if os.path.basename(os.environ.get("SHELL", "")) == "zsh":
        core.ok("zsh is already the login shell.")
        return
    core.info("Setting zsh as login shell (chsh asks for your password)...")
    result = core.run(["chsh", "-s", zsh_path], check=False)
    if result.returncode != 0:
        core.warn(f"chsh failed — run it yourself: chsh -s {zsh_path}")
    else:
        core.ok(f"Login shell set to {zsh_path}. Takes effect on next login.")


def _linux_uninstall() -> None:
    if core.detect_os() != "linux":
        return
    from lib import apt
    for name, _ in _RENAMED:
        apt.unshim(name)


TOOL = Tool(
    name="zsh",
    doc="Zsh + CLI tools + plugins + .zshrc",
    platforms=frozenset({"macos", "linux"}),
    brew=("bat", "eza", "fzf", "zoxide", "ripgrep", "fd", "htop",
          "zsh-autosuggestions", "zsh-syntax-highlighting"),
    # zsh itself is in this list on Linux only: macOS already ships a modern
    # zsh as the default shell, while Ubuntu's default is bash.
    apt=("zsh", "bat", "eza", "fzf", "zoxide", "ripgrep", "fd-find", "htop",
         "zsh-autosuggestions", "zsh-syntax-highlighting"),
    links=(Link("zsh/.zshrc", "~/.zshrc"),),
    post_install=_linux_post,
    extra_uninstall=_linux_uninstall,
)
