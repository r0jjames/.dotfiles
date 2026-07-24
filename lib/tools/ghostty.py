# lib/tools/ghostty.py
"""Ghostty (macOS only): app + config (theme + font reused from iTerm2)."""
from __future__ import annotations

import filecmp
from pathlib import Path

from lib import core
from lib.core import Tool


def _config_src() -> Path:
    return core.REPO_ROOT / "ghostty" / "config"


def _config_target() -> Path:
    return Path.home() / ".config/ghostty/config"


def _post() -> None:
    if Path("/Applications/Ghostty.app").is_dir():
        core.ok("Ghostty already installed.")
    else:
        core.brew_install("ghostty", cask=True)
    # Same font cask as iTerm2; no-op if already installed.
    core.brew_install("font-meslo-lg-nerd-font", cask=True)

    # ---- Config (color theme + font) ----
    core.copy_file(_config_src(), _config_target())

    # Ghostty auto-injects shell integration; nothing to source in .zshrc.
    core.ok("Ghostty setup complete. Restart Ghostty to pick up the config.")


def _uninstall() -> None:
    core.uncopy_file(_config_src(), _config_target())
    core.skip("Ghostty app and fonts left alone.")


def _probe() -> bool:
    t = _config_target()
    return t.exists() and filecmp.cmp(str(_config_src()), str(t), shallow=False)


TOOL = Tool(
    name="ghostty",
    doc="Ghostty + config (theme + font)",
    platforms=frozenset({"macos"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
