"""Tool registry. Order here is menu/run order (mirrors old ALL_TOOLS)."""
from __future__ import annotations

from lib.tools import claude, nvim, starship, vscode, wezterm, zsh

_ALL = (
    zsh.TOOL,
    starship.TOOL,
    nvim.TOOL,
    wezterm.TOOL,
    vscode.TOOL,
    claude.TOOL,
)

REGISTRY = {t.name: t for t in _ALL}
