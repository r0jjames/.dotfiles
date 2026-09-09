# lib/theme.py
"""The repo's terminal theme, parsed from `ghostty/config`.

`ghostty/config` is the single source of truth for the palette. Every other
terminal this repo themes reads it through here rather than keeping a copy:

  terminal_ubuntu  — GNOME Terminal, via gsettings
  terminal_windows — Windows Terminal, via a scheme in settings.json

The palette already lives in two files that must be hand-synced --
ghostty/config and iterm2/com.dotfiles.json, each carrying a README note
saying so. Anything further that restated all sixteen colors would be one
more thing to drift, so it is derived instead.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

from lib import core

# Ghostty palette index -> Windows Terminal's key name for that slot.
ANSI_NAMES: Tuple[str, ...] = (
    "black", "red", "green", "yellow", "blue", "purple", "cyan", "white",
    "brightBlack", "brightRed", "brightGreen", "brightYellow", "brightBlue",
    "brightPurple", "brightCyan", "brightWhite",
)


@dataclass(frozen=True)
class Theme:
    background: str
    foreground: str
    cursor_bg: str
    cursor_fg: str
    selection_bg: str
    selection_fg: str
    palette: Tuple[str, ...]      # 16 entries, "#RRGGBB", index order
    font_family: str
    font_size: int
    bold_is_bright: bool

    def ansi(self) -> Dict[str, str]:
        """The 16 slots keyed the way Windows Terminal names them."""
        return dict(zip(ANSI_NAMES, self.palette))


def config_path() -> Path:
    return core.REPO_ROOT / "ghostty" / "config"


def _hex(value: str) -> str:
    """Normalise Ghostty's colors (`300a24` or `#300a24`) to `#300A24`."""
    return "#" + value.strip().lstrip("#").upper()


def _parse(text: str) -> Tuple[Dict[str, str], Dict[int, str]]:
    simple: Dict[str, str] = {}
    palette: Dict[int, str] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip()
        if key == "palette":
            index, _, color = value.partition("=")
            if index.strip().isdigit():
                palette[int(index.strip())] = _hex(color)
        else:
            simple[key] = value
    return simple, palette


def load() -> Theme:
    """Read ghostty/config into a Theme, or raise if it is not usable."""
    simple, palette = _parse(config_path().read_text())

    missing: List[int] = [i for i in range(16) if i not in palette]
    if missing:
        raise core.DotfilesError(
            f"ghostty/config is missing palette slots {missing} — a terminal "
            "theme needs all 16.")
    for required in ("background", "foreground"):
        if required not in simple:
            raise core.DotfilesError(
                f"ghostty/config has no '{required}' — cannot build a theme.")

    background = _hex(simple["background"])
    foreground = _hex(simple["foreground"])
    return Theme(
        background=background,
        foreground=foreground,
        cursor_bg=_hex(simple.get("cursor-color", foreground)),
        cursor_fg=_hex(simple.get("cursor-text", background)),
        selection_bg=_hex(simple.get("selection-background", foreground)),
        selection_fg=_hex(simple.get("selection-foreground", background)),
        palette=tuple(palette[i] for i in range(16)),
        font_family=simple.get("font-family", "MesloLGS Nerd Font Mono"),
        font_size=int(float(simple.get("font-size", "13"))),
        bold_is_bright=simple.get("bold-is-bright", "true") == "true",
    )
