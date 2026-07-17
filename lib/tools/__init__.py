"""Tool registry. Order here is menu/run order (mirrors old ALL_TOOLS)."""
from __future__ import annotations

from lib.tools import claude, starship, wezterm

_ALL = (
    starship.TOOL,
    wezterm.TOOL,
    claude.TOOL,
)

REGISTRY = {t.name: t for t in _ALL}
