# lib/tools/tmux.py
"""tmux: terminal multiplexer, with the whole config directory symlinked in.

The link is the directory (repo `tmux/` -> `~/.config/tmux`), not a single
file, because tmux.conf calls helper scripts that have to travel with it:
`scripts/status.sh` for the status-bar segments and `scripts/sessionizer.sh`
for the fzf project picker.

Those calls are absolute paths (`${HOME}/.config/tmux/scripts/...`). tmux's
config expansion has no default-value form -- a line containing
`${XDG_CONFIG_HOME:-$HOME/.config}` fails to parse outright, verified on
3.7c -- so the path cannot be derived inside tmux.conf. `~/.config/tmux` is
therefore always linked and always the path the config refers to.

XDG_CONFIG_HOME is still honoured, because tmux searches
`$XDG_CONFIG_HOME/tmux/tmux.conf` before `~/.config/tmux/tmux.conf`: when
that variable points somewhere else, a second link is made there so tmux
finds the config, while the scripts keep resolving through `~/.config/tmux`.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import List

from lib import core
from lib.core import Tool

_DIR = "tmux"


def _src() -> Path:
    return core.REPO_ROOT / _DIR


def _default_target() -> Path:
    return Path.home() / ".config" / _DIR


def _targets() -> List[Path]:
    """Link targets, always including ~/.config/tmux (the path tmux.conf
    hard-codes), plus the XDG location when it resolves somewhere else."""
    targets = [_default_target()]
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        xdg_target = Path(xdg).expanduser() / _DIR
        if xdg_target != targets[0]:
            targets.append(xdg_target)
    return targets


def _post() -> None:
    for target in _targets():
        core.link_file(_src(), target)


def _uninstall() -> None:
    for target in _targets():
        core.unlink_file(_src(), target)


def _probe() -> bool:
    src = _src().resolve()
    return all(t.is_symlink() and t.resolve() == src for t in _targets())


TOOL = Tool(
    name="tmux",
    doc="tmux + status bar, additive keys, fzf project picker",
    platforms=frozenset({"macos", "linux"}),
    brew=("tmux",),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
