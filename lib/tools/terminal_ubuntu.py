# lib/tools/terminal_ubuntu.py
"""GNOME Terminal (Ubuntu only): the repo's theme + font on the stock terminal.

The Ubuntu counterpart to terminal_macos.py. Ghostty is the daily driver, but
the stock terminal is what opens from the Files context menu, from an IDE, or
when Ghostty is mid-upgrade, so it gets the same look.

Colors come from `ghostty/config` via lib/theme.py rather than being restated
here. The repo already carries this palette twice -- ghostty/config and
iterm2/com.dotfiles.json, each with a README note reminding you to keep them
in sync -- and a third hand-maintained copy would be a third thing to drift.

Settings are written with gsettings into the default profile under
`org.gnome.Terminal.Legacy.Profile`. GNOME Terminal has no config file to
symlink; dconf is the only interface, so this tool copies values in and
`gsettings reset` puts them back on uninstall.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from lib import core, fonts, theme
from lib.core import Tool

_PROFILE_LIST = "org.gnome.Terminal.ProfilesList"
_PROFILE_SCHEMA = "org.gnome.Terminal.Legacy.Profile"
_PROFILE_PATH = "/org/gnome/terminal/legacy/profiles:/:{uuid}/"


# ---- gsettings plumbing ----
def _gvariant_list(values: List[str]) -> str:
    return "[" + ", ".join(f"'{v}'" for v in values) + "]"


def available() -> bool:
    """True when this machine actually has GNOME Terminal's schemas.

    The profile schema is *relocatable* -- one instance per profile UUID --
    so it never appears in `gsettings list-schemas`, only in
    `list-relocatable-schemas`. Both are checked: the profile list proves
    GNOME Terminal is installed, the relocatable one that we can write."""
    if not core.have("gsettings"):
        return False
    fixed = core.run(["gsettings", "list-schemas"], check=False, capture=True)
    if fixed.returncode != 0 or _PROFILE_LIST not in fixed.stdout:
        return False
    reloc = core.run(["gsettings", "list-relocatable-schemas"],
                     check=False, capture=True)
    return reloc.returncode == 0 and _PROFILE_SCHEMA in reloc.stdout


def default_profile() -> Optional[str]:
    result = core.run(["gsettings", "get", _PROFILE_LIST, "default"],
                      check=False, capture=True)
    if result.returncode != 0:
        return None
    uuid = result.stdout.strip().strip("'")
    return uuid or None


def _schema_for(uuid: str) -> str:
    return f"{_PROFILE_SCHEMA}:{_PROFILE_PATH.format(uuid=uuid)}"


def _get(uuid: str, key: str) -> str:
    return core.run(["gsettings", "get", _schema_for(uuid), key],
                    check=False, capture=True).stdout.strip()


def _set(uuid: str, key: str, value: str) -> None:
    core.run(["gsettings", "set", _schema_for(uuid), key, value])


def _desired() -> Dict[str, str]:
    t = theme.load()
    return {
        "use-theme-colors": "false",
        "background-color": f"'{t.background}'",
        "foreground-color": f"'{t.foreground}'",
        "palette": _gvariant_list(list(t.palette)),
        "cursor-colors-set": "true",
        "cursor-background-color": f"'{t.cursor_bg}'",
        "cursor-foreground-color": f"'{t.cursor_fg}'",
        "bold-is-bright": "true" if t.bold_is_bright else "false",
        "cursor-shape": "'block'",
        "use-system-font": "false",
        "font": f"'{t.font_family} {t.font_size}'",
        "audible-bell": "false",
        "scrollback-unlimited": "true",
    }


# ---- Tool hooks ----
def _post() -> None:
    if core.is_wsl():
        core.skip("No GNOME Terminal under WSL — the Windows-side terminal "
                  "owns the theme there.")
        return
    if not available():
        core.skip("GNOME Terminal is not installed — skipping. "
                  "(Ghostty carries the same theme.)")
        return
    uuid = default_profile()
    if uuid is None:
        raise core.DotfilesError(
            "Could not read GNOME Terminal's default profile from gsettings.")

    # The font has to exist before the profile can name it.
    fonts.ensure(fonts.MESLO)

    core.info(f"Applying theme to GNOME Terminal profile {uuid}...")
    desired = _desired()
    for key, value in desired.items():
        if _get(uuid, key) == value:
            continue
        _set(uuid, key, value)
    core.ok("GNOME Terminal themed. Open a new window to see it.")


def _uninstall() -> None:
    if not available():
        return
    uuid = default_profile()
    if uuid is None:
        return
    for key in _desired():
        core.run(["gsettings", "reset", _schema_for(uuid), key], check=False)
    core.ok("GNOME Terminal profile reset to its defaults.")


def _probe() -> bool:
    if core.is_wsl() or not available():
        return False
    uuid = default_profile()
    if uuid is None:
        return False
    return all(_get(uuid, key) == value for key, value in _desired().items())


TOOL = Tool(
    name="terminal-ubuntu",
    doc="GNOME Terminal theme + font (shared with Ghostty)",
    platforms=frozenset({"linux"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
