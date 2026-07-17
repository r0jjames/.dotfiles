# lib/tools/agent_skills.py
"""Agent skills: symlink custom skills into ~/.claude/skills via the
standalone agent-skills/install.py (kept separate — it also handles community
skill fetching and the Copilot target on the work machine)."""
from __future__ import annotations

import sys
from pathlib import Path

from lib import core
from lib.core import Tool


def _skills_dir() -> Path:
    return Path.home() / ".claude" / "skills"


def _repo_symlinks():
    d = _skills_dir()
    if not d.is_dir():
        return
    for entry in d.iterdir():
        if not entry.is_symlink():
            continue
        try:
            dest = entry.resolve()
        except OSError:
            continue
        if core.REPO_ROOT in dest.parents:
            yield entry


def _post() -> None:
    core.run([sys.executable,
              str(core.REPO_ROOT / "agent-skills" / "install.py"),
              "--target", "claude", "--skills-only"])
    core.ok("Agent skills setup complete.")


def _uninstall() -> None:
    for entry in list(_repo_symlinks()):
        entry.unlink()
        core.ok(f"Removed {entry}")


def _probe() -> bool:
    return next(iter(_repo_symlinks()), None) is not None


TOOL = Tool(
    name="agent-skills",
    doc="Custom agent skills into ~/.claude/skills",
    platforms=frozenset({"macos", "linux"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
