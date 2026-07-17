# lib/tools/terminal_macos.py
"""Terminal.app (macOS only): Solarized themes + MesloLGS NF font defaults."""
from __future__ import annotations

import time
from pathlib import Path

from lib import core
from lib.core import Tool

_THEMES_URL = ("https://github.com/lysyi3m/macos-terminal-themes/"
               "archive/refs/heads/master.zip")


def _default_theme() -> str:
    return core.run(["defaults", "read", "com.apple.Terminal",
                     "Default Window Settings"],
                    check=False, capture=True).stdout.strip()


def _post() -> None:
    core.brew_install("font-meslo-lg-nerd-font", cask=True)

    # ---- Download themes if not already downloaded ----
    themes_dir = Path.home() / "Downloads" / "macos-terminal-themes-master"
    if themes_dir.is_dir():
        core.ok("Terminal themes already downloaded.")
    else:
        core.info("Downloading Terminal.app themes...")
        zip_path = Path.home() / "Downloads" / "terminal-themes.zip"
        core.run(["curl", "-L", _THEMES_URL, "-o", str(zip_path)])
        core.run(["unzip", "-o", str(zip_path),
                  "-d", str(Path.home() / "Downloads")])
        zip_path.unlink()

    # ---- Load themes into Terminal if not already loaded ----
    core.run(["osascript", "-e", 'quit app "Terminal"'], check=False)
    time.sleep(2)
    loaded = core.run(["defaults", "read", "com.apple.Terminal",
                       "Window Settings"], check=False, capture=True).stdout
    for theme in sorted((themes_dir / "themes").glob("*.terminal")):
        if theme.stem not in loaded:
            core.run(["open", str(theme)])
    time.sleep(5)
    core.run(["osascript", "-e", 'quit app "Terminal"'], check=False)

    # ---- Default theme + font ----
    if "Solarized Dark" in _default_theme():
        core.ok("Terminal default theme already set.")
    else:
        core.run(["defaults", "write", "com.apple.Terminal",
                  "Default Window Settings", "-string", "Solarized Dark"])
        core.run(["defaults", "write", "com.apple.Terminal",
                  "Startup Window Settings", "-string", "Solarized Dark"])
    core.ok("Terminal.app setup complete. Restart Terminal for all changes.")


def _uninstall() -> None:
    core.skip("Terminal.app defaults and downloaded themes left alone — "
              "change theme in Terminal preferences if desired.")


def _probe() -> bool:
    return "Solarized Dark" in _default_theme()


TOOL = Tool(
    name="terminal-macos",
    doc="Terminal.app Solarized theme + font",
    platforms=frozenset({"macos"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
