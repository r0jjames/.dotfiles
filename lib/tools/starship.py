# lib/tools/starship.py
"""Starship prompt: install + link config. Init line lives in zsh/.zshrc.

Not in Ubuntu's archive, so on Linux the upstream installer drops the binary
into ~/.local/bin (see lib/apt.py) rather than pulling in Homebrew for it.
"""
from __future__ import annotations

from lib import core
from lib.core import Link, Tool


def _post() -> None:
    if core.detect_os() == "linux":
        from lib import apt
        apt.install_starship()


TOOL = Tool(
    name="starship",
    doc="Starship prompt + config",
    platforms=frozenset({"macos", "linux"}),
    brew=("starship",),
    links=(Link("starship/starship.toml", "~/.config/starship.toml"),),
    post_install=_post,
)
