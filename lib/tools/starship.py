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
