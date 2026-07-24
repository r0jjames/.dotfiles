# lib/tools/intellij.py
"""IntelliJ IDEA Community: install + F-free cross-OS custom keymap.

  macOS   — brew cask intellij-idea-ce, then SYMLINK keymap-macos.xml into
            every ~/Library/Application Support/JetBrains/<IdeaIC*>/keymaps/
  Windows — (Git Bash) COPY keymap-windows.xml into every
            %APPDATA%/JetBrains/<IntelliJIdea*|IdeaIC*>/keymaps/ (symlinks
            need admin). Assumes IntelliJ already installed on the host.

JetBrains config dirs are version-stamped (IdeaIC2026.1, ...), unlike VS
Code's stable Code/User - so we glob every matching dir and place the keymap
in each. If none exist yet, the IDE has never launched: we warn to open it
once and re-run. The keymap only becomes *active* after you pick it in
Settings -> Keymap (see intellij/README.md). The VDI is not reachable here -
it gets the keymap via Settings Sync (Path A) or vdi-apply-keymap.ps1.
"""
from __future__ import annotations

import filecmp
import os
from pathlib import Path
from typing import Tuple

from lib import core
from lib.core import Tool

# File dropped into each keymaps/ dir. Name matches the <keymap name="..."> so
# the dropdown label and Settings Sync entry line up.
_KEYMAP_TARGET = "roj-keymap.xml"

# Filename used by installs from before the Roj-Ffree -> roj-keymap rename.
# Cleaned up on install so both don't linger in the Keymap dropdown.
_STALE_KEYMAP_TARGET = "Roj-Ffree.xml"

# Config-dir name prefixes: Community = "IdeaIC<ver>", Ultimate = "IntelliJIdea<ver>".
_PRODUCT_PREFIXES = ("IdeaIC", "IntelliJIdea")

# NOTE: the `intellij-idea-ce` cask is deprecated upstream (disabled
# 2026-12-08) - JetBrains folded Community into the unified `intellij-idea`
# distribution's free tier. When CE stops installing, switch _CASK to
# "intellij-idea" and _APP to "/Applications/IntelliJ IDEA.app".
_CASK = "intellij-idea-ce"
_APP = Path("/Applications/IntelliJ IDEA CE.app")


def _jetbrains_dir() -> Tuple[Path, str, str]:
    """Return (JetBrains config base, keymap source filename, mode)."""
    os_name = core.detect_os()
    if os_name == "macos":
        base = Path.home() / "Library/Application Support/JetBrains"
        return base, "keymap-macos.xml", "link"
    if os_name == "gitbash":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise core.DotfilesError("APPDATA not set; cannot locate JetBrains dir.")
        return Path(appdata) / "JetBrains", "keymap-windows.xml", "copy"
    raise core.DotfilesError("intellij: unsupported platform (macOS/Git Bash only).")


def find_config_dirs(base: Path) -> list[Path]:
    """Existing IntelliJ config dirs under the JetBrains base, newest last."""
    if not base.is_dir():
        return []
    dirs = [d for d in base.iterdir()
            if d.is_dir() and d.name.startswith(_PRODUCT_PREFIXES)]
    return sorted(dirs, key=lambda d: d.name)


def _src(filename: str) -> Path:
    return core.REPO_ROOT / "intellij" / filename


def _post() -> None:
    base, src_name, mode = _jetbrains_dir()
    src = _src(src_name)

    # 1. Install the app (macOS only; Windows host assumed to have it).
    if core.detect_os() == "macos":
        if _APP.is_dir():
            core.ok("IntelliJ IDEA CE already installed.")
        else:
            core.brew_install(_CASK, cask=True)

    # 2. Place the keymap into every existing config dir.
    dirs = find_config_dirs(base)
    if not dirs:
        core.warn(f"No IntelliJ config dir under {base}.")
        core.warn("Launch IntelliJ once (so it creates its config), then "
                  "re-run: ./install.py install intellij")
        return
    core.info(f"Applying F-free keymap to {len(dirs)} config dir(s) ({mode})...")
    for d in dirs:
        keymaps_dir = d / "keymaps"
        keymaps_dir.mkdir(parents=True, exist_ok=True)
        stale = keymaps_dir / _STALE_KEYMAP_TARGET
        if stale.exists() or stale.is_symlink():
            stale.unlink()
            core.info(f"Removed stale {stale} from a pre-rename install.")
        target = keymaps_dir / _KEYMAP_TARGET
        if mode == "link":
            core.link_file(src, target)
        else:
            core.copy_file(src, target)
    core.ok("Keymap installed. One-time manual step: Settings -> Keymap -> "
            "select 'roj-keymap'. See intellij/README.md (plugins, VDI sync, "
            "cheatsheet).")


def _uninstall() -> None:
    base, _, mode = _jetbrains_dir()
    src = _src("keymap-macos.xml" if mode == "link" else "keymap-windows.xml")
    dirs = find_config_dirs(base)
    if not dirs:
        core.skip(f"No IntelliJ config dir under {base} - nothing to remove.")
    for d in dirs:
        target = d / "keymaps" / _KEYMAP_TARGET
        if mode == "link":
            core.unlink_file(src, target)
        else:
            core.uncopy_file(src, target)
    core.info("IntelliJ app left installed - remove via brew/Finder if unwanted.")
    core.info("If 'roj-keymap' is still the active keymap, switch back in "
              "Settings -> Keymap.")


def _probe() -> bool:
    try:
        base, src_name, mode = _jetbrains_dir()
    except core.DotfilesError:
        return False
    src = _src(src_name)
    dirs = find_config_dirs(base)
    if not dirs:
        return False
    # Installed = keymap present+correct in *every* existing config dir.
    for d in dirs:
        target = d / "keymaps" / _KEYMAP_TARGET
        if mode == "link":
            if not (target.is_symlink() and target.resolve() == src.resolve()):
                return False
        else:
            if not (target.exists()
                    and filecmp.cmp(str(src), str(target), shallow=False)):
                return False
    return True


TOOL = Tool(
    name="intellij",
    doc="IntelliJ IDEA CE + F-free cross-OS keymap",
    platforms=frozenset({"macos", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
