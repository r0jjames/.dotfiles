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
