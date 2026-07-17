# lib/tools/iterm2.py
"""iTerm2 (macOS only): app, shell integration, dynamic profile (theme + font)."""
from __future__ import annotations

import filecmp
from pathlib import Path

from lib import core
from lib.core import Tool

_GUID = "557036D3-EF41-4D30-A395-3F301A17D49B"


def _profile_src() -> Path:
    return core.REPO_ROOT / "iterm2" / "com.dotfiles.json"


def _profile_target() -> Path:
    return (Path.home() / "Library/Application Support/iTerm2/DynamicProfiles"
            / "com.dotfiles.json")


def _integration() -> Path:
    return Path.home() / ".iterm2_shell_integration.zsh"


def _post() -> None:
    if Path("/Applications/iTerm.app").is_dir():
        core.ok("iTerm2 already installed.")
    else:
        core.brew_install("iterm2", cask=True)
    core.brew_install("font-meslo-lg-nerd-font", cask=True)

    # ---- Shell integration (sourced by zsh/.zshrc when present) ----
    if _integration().exists():
        core.ok("iTerm2 shell integration already installed.")
    else:
        core.info("Installing iTerm2 shell integration...")
        core.run(["curl", "-fsSL", "https://iterm2.com/shell_integration/zsh",
                  "-o", str(_integration())])

    # ---- Dynamic profile (color theme + font) ----
    core.copy_file(_profile_src(), _profile_target())

    # ---- Default profile ----
    current = core.run(["defaults", "read", "com.googlecode.iterm2",
                        "Default Bookmark Guid"],
                       check=False, capture=True).stdout.strip()
    if current == _GUID:
        core.ok("iTerm2 default profile already set.")
    else:
        core.run(["defaults", "write", "com.googlecode.iterm2",
                  "Default Bookmark Guid", "-string", _GUID])
    core.ok("iTerm2 setup complete. Restart iTerm2 (Cmd+Q then relaunch).")


def _uninstall() -> None:
    core.uncopy_file(_profile_src(), _profile_target())
    if _integration().exists():
        _integration().unlink()
        core.ok(f"Removed {_integration()}")
    core.skip("iTerm2 app, fonts and defaults left alone.")


def _probe() -> bool:
    t = _profile_target()
    return t.exists() and filecmp.cmp(str(_profile_src()), str(t), shallow=False)


TOOL = Tool(
    name="iterm2",
    doc="iTerm2 + dynamic profile + shell integration",
    platforms=frozenset({"macos"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
