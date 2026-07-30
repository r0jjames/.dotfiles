# lib/tools/jetbrains.py
"""JetBrains IDEs: the F-free cross-OS roj-keymap, distributed to all of them.

  macOS   - SYMLINK keymap-macos.xml into every
            ~/Library/Application Support/JetBrains/<product>/keymaps/
  Windows - (Git Bash) COPY keymap-windows.xml into every
            %APPDATA%/JetBrains/<product>/keymaps/ (symlinks need admin).

<product> is any dir named for a JetBrains IDE family - IntelliJ Community or
Ultimate, PyCharm (incl. CE/Edu), GoLand. This tool does NOT install IDEs: you
install them yourself via Toolbox or brew, and it distributes the keymap to
whichever ones are present. That keeps install idempotent across machines with
different IDE sets, and sidesteps the deprecated intellij-idea-ce cask
(disabled upstream 2026-12-08).

JetBrains config dirs are version-stamped (IdeaIC2026.1, PyCharm2025.3, ...),
unlike VS Code's stable Code/User - so we glob every matching dir and place the
keymap in each. If none exist yet, no IDE has ever launched: we warn to open one
once and re-run. The keymap only becomes *active* after you pick it in
Settings -> Keymap (see jetbrains/README.md). The VDI is not reachable here -
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

# Repo dir this tool used before the intellij -> jetbrains rename. Symlinks
# from a pre-rename install point into it and now dangle; we delete them
# rather than let link_file back them up, since unlink_file would later
# "restore" a broken link as if it were the user's own file.
_STALE_SRC_DIR = "intellij"

# Config-dir name prefixes, one per JetBrains product family. "PyCharm" as a
# str.startswith prefix also covers PyCharmCE* (Community) and PyCharmEdu*.
# Non-IDE siblings in the JetBrains base (consentOptions, Toolbox, the bl/crl
# files) match none of these.
_PRODUCT_PREFIXES = ("IdeaIC", "IntelliJIdea", "PyCharm", "GoLand")

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
    raise core.DotfilesError("jetbrains: unsupported platform (macOS/Git Bash only).")


def find_config_dirs(base: Path) -> list[Path]:
    """Existing JetBrains IDE config dirs under the JetBrains base, newest last."""
    if not base.is_dir():
        return []
    dirs = [d for d in base.iterdir()
            if d.is_dir() and d.name.startswith(_PRODUCT_PREFIXES)]
    return sorted(dirs, key=lambda d: d.name)


def _src(filename: str) -> Path:
    return core.REPO_ROOT / "jetbrains" / filename


def _drop_pre_rename_link(target: Path) -> bool:
    """Delete target when it is a symlink into the pre-rename intellij/ dir.

    Uses readlink, not resolve(): after the rename the link is broken, so the
    destination cannot be stat'ed. Returns True when something was removed.
    """
    if not target.is_symlink():
        return False
    dest = Path(os.readlink(target))
    if _STALE_SRC_DIR not in dest.parts:
        return False
    target.unlink()
    core.info(f"Removed {target} from a pre-rename (intellij/) install.")
    return True


def _post() -> None:
    base, src_name, mode = _jetbrains_dir()
    src = _src(src_name)

    # Place the keymap into every existing config dir.
    dirs = find_config_dirs(base)
    if not dirs:
        core.warn(f"No JetBrains config dir under {base}.")
        core.warn("Launch a JetBrains IDE once (so it creates its config), "
                  "then re-run: ./install.py install jetbrains")
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
        _drop_pre_rename_link(target)
        if mode == "link":
            core.link_file(src, target)
        else:
            core.copy_file(src, target)
    core.ok("Keymap installed. One-time manual step: Settings -> Keymap -> "
            "select 'roj-keymap'. See jetbrains/README.md (plugins, VDI sync, "
            "cheatsheet).")


def _uninstall() -> None:
    base, _, mode = _jetbrains_dir()
    src = _src("keymap-macos.xml" if mode == "link" else "keymap-windows.xml")
    dirs = find_config_dirs(base)
    if not dirs:
        core.skip(f"No JetBrains config dir under {base} - nothing to remove.")
    for d in dirs:
        target = d / "keymaps" / _KEYMAP_TARGET
        if mode == "link":
            core.unlink_file(src, target)
        else:
            core.uncopy_file(src, target)
    core.info("JetBrains IDEs are installed outside dotfiles - none were touched.")
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
    name="jetbrains",
    doc="roj-keymap for every JetBrains IDE (IntelliJ, PyCharm, GoLand)",
    platforms=frozenset({"macos", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
