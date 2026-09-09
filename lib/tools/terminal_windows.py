# lib/tools/terminal_windows.py
"""Windows Terminal (Git Bash only): the repo's theme + font.

The Windows counterpart to terminal_macos.py and terminal_ubuntu.py, for the
work machine where WSL Ubuntu runs inside Windows Terminal. Colors come from
`ghostty/config` through lib/theme.py, so all three stay in step.

Windows Terminal keeps everything in one settings.json that the user also
edits by hand, so this **merges** rather than writes the file: our scheme is
added to (or refreshed in) `schemes`, and `profiles.defaults` is pointed at
it. Every other key is left exactly as found, and the file is backed up
first.

Two things make that merge fiddly, and both are handled below:

  * The file is JSONC — Windows Terminal ships it with `//` comments, which
    json.loads rejects. Comments are stripped for reading. They cannot
    survive the round trip, which is why the backup matters.
  * There are three possible install locations (Store, Preview, unpackaged),
    and only one of them exists on any given machine.

The font is NOT installed from here. On Windows a Nerd Font has to be
installed system-side (right-click the .ttf -> Install for all users); the
top-level README covers it. Naming a font Windows does not have would fall
back silently, so `_post` says so rather than pretending.
"""
from __future__ import annotations

import json
import os
import re
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

from lib import core, theme
from lib.core import Tool

SCHEME_NAME = "Dotfiles Tango"

# Store, Preview, then the unpackaged/scoop build. Order is preference.
_RELATIVE_LOCATIONS = (
    "Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState/settings.json",
    "Packages/Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe/LocalState/"
    "settings.json",
    "Microsoft/Windows Terminal/settings.json",
)


# ---- Locating settings.json ----
def _local_appdata() -> Optional[Path]:
    """%LOCALAPPDATA%, which Git Bash passes through unchanged."""
    value = os.environ.get("LOCALAPPDATA")
    return Path(value) if value else None


def settings_candidates() -> List[Path]:
    base = _local_appdata()
    if base is None:
        return []
    return [base / rel for rel in _RELATIVE_LOCATIONS]


def settings_path() -> Optional[Path]:
    for candidate in settings_candidates():
        if candidate.is_file():
            return candidate
    return None


# ---- JSONC ----
_COMMENTS = re.compile(
    r'"(?:\\.|[^"\\])*"'        # a string literal, matched so it is skipped
    r'|//[^\n]*'                # line comment
    r'|/\*.*?\*/',              # block comment
    re.DOTALL)


def strip_jsonc(text: str) -> str:
    """Remove // and /* */ comments, leaving string literals untouched.

    Windows Terminal ships settings.json with comments. A naive strip would
    also gut any value containing "//" -- a URL, a Windows path -- so string
    literals are matched by the same pass and handed back verbatim."""
    def replace(match: re.Match) -> str:
        token = match.group(0)
        return token if token.startswith('"') else ""
    return _COMMENTS.sub(replace, text)


def load_settings(path: Path) -> Dict[str, Any]:
    text = strip_jsonc(path.read_text(encoding="utf-8-sig"))
    try:
        loaded = json.loads(text)
    except json.JSONDecodeError as exc:
        raise core.DotfilesError(
            f"Could not parse {path} even after stripping comments: {exc}. "
            "Fix the file in Windows Terminal, then re-run.") from exc
    if not isinstance(loaded, dict):
        raise core.DotfilesError(f"{path} is not a JSON object.")
    return loaded


# ---- The scheme ----
def scheme() -> Dict[str, str]:
    """Our palette in Windows Terminal's scheme shape."""
    t = theme.load()
    built = {
        "name": SCHEME_NAME,
        "background": t.background,
        "foreground": t.foreground,
        "cursorColor": t.cursor_bg,
        "selectionBackground": t.selection_bg,
    }
    built.update(t.ansi())
    return built


def merge(settings: Dict[str, Any]) -> bool:
    """Add/refresh our scheme and point the default profile at it.

    Returns True when anything actually changed, so a no-op re-run does not
    rewrite the user's file (and drop their comments) for nothing."""
    t = theme.load()
    changed = False

    schemes = settings.setdefault("schemes", [])
    if not isinstance(schemes, list):
        raise core.DotfilesError("settings.json 'schemes' is not a list.")
    wanted = scheme()
    for index, existing in enumerate(schemes):
        if isinstance(existing, dict) and existing.get("name") == SCHEME_NAME:
            if existing != wanted:
                schemes[index] = wanted
                changed = True
            break
    else:
        schemes.append(wanted)
        changed = True

    profiles = settings.setdefault("profiles", {})
    if isinstance(profiles, list):
        # Very old schema: profiles was a bare list, with no defaults block.
        raise core.DotfilesError(
            "settings.json uses the pre-1.0 'profiles' list format; open "
            "Windows Terminal once to migrate it, then re-run.")
    defaults = profiles.setdefault("defaults", {})

    for key, value in (("colorScheme", SCHEME_NAME),
                       ("font", {"face": t.font_family, "size": t.font_size})):
        if defaults.get(key) != value:
            defaults[key] = value
            changed = True

    return changed


def _is_applied(settings: Dict[str, Any]) -> bool:
    t = theme.load()
    schemes = settings.get("schemes")
    if not isinstance(schemes, list):
        return False
    if not any(isinstance(s, dict) and s == scheme() for s in schemes):
        return False
    profiles = settings.get("profiles")
    if not isinstance(profiles, dict):
        return False
    defaults = profiles.get("defaults", {})
    return (defaults.get("colorScheme") == SCHEME_NAME
            and defaults.get("font") == {"face": t.font_family,
                                         "size": t.font_size})


# ---- Tool hooks ----
def _post() -> None:
    if _local_appdata() is None:
        core.skip("LOCALAPPDATA is not set — not a Windows shell, skipping.")
        return
    path = settings_path()
    if path is None:
        core.skip("Windows Terminal settings.json not found in any of: "
                  + ", ".join(str(p) for p in settings_candidates())
                  + ". Launch Windows Terminal once, then re-run.")
        return

    settings = load_settings(path)
    if not merge(settings):
        core.ok("Windows Terminal already themed.")
        return

    backup = path.with_name(path.name + ".bak-" + date.today().isoformat())
    if not backup.exists():
        core.info(f"Backing up {path} -> {backup}")
        backup.write_bytes(path.read_bytes())

    path.write_text(json.dumps(settings, indent=4, ensure_ascii=False) + "\n",
                    encoding="utf-8")
    core.ok(f"Applied '{SCHEME_NAME}' to {path}")
    core.warn("Comments in settings.json are not preserved by this rewrite — "
              f"the original is at {backup.name}.")
    core.info(f"Install the {theme.load().font_family} font on the Windows "
              "side if you have not: right-click the .ttf -> Install for all "
              "users. See the top-level README.")


def _uninstall() -> None:
    path = settings_path()
    if path is None:
        return
    settings = load_settings(path)
    schemes = settings.get("schemes")
    changed = False
    if isinstance(schemes, list):
        kept = [s for s in schemes
                if not (isinstance(s, dict) and s.get("name") == SCHEME_NAME)]
        if len(kept) != len(schemes):
            settings["schemes"] = kept
            changed = True
    profiles = settings.get("profiles")
    if isinstance(profiles, dict):
        defaults = profiles.get("defaults", {})
        if defaults.get("colorScheme") == SCHEME_NAME:
            defaults.pop("colorScheme", None)
            defaults.pop("font", None)
            changed = True
    if changed:
        path.write_text(
            json.dumps(settings, indent=4, ensure_ascii=False) + "\n",
            encoding="utf-8")
        core.ok(f"Removed '{SCHEME_NAME}' from {path}")
    else:
        core.skip("Windows Terminal was not themed by this repo.")


def _probe() -> bool:
    path = settings_path()
    if path is None:
        return False
    try:
        return _is_applied(load_settings(path))
    except (core.DotfilesError, OSError):
        return False


TOOL = Tool(
    name="terminal-windows",
    doc="Windows Terminal theme + font (shared with Ghostty)",
    platforms=frozenset({"gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
