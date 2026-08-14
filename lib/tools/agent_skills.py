# lib/tools/agent_skills.py
"""Agent skills: install custom skills into the agent skill dirs via the
standalone agent-skills/install.py (kept separate — it also handles community
skill fetching and the Copilot target).

  macOS/Linux — Claude only, symlinked into ~/.claude/skills.
  Git Bash    — Claude and Copilot (~/.claude/skills, ~/.copilot/skills).
                Windows symlinks need Developer Mode or admin, so the
                installer falls back to copies there; re-run after editing
                a skill to refresh them.

~/.copilot/skills is personal scope: it serves Copilot in JetBrains IDEs as
well as VS Code. The Copilot target also generates one skill per prompt file
into that directory, so the /create-sb-style commands reach every JetBrains
project as /skill:create-sb — prompt files themselves have no personal scope
outside VS Code and would otherwise need per-repo seeding
(`agent-skills/install.py --repo <path>`).
"""
from __future__ import annotations

import sys
from pathlib import Path

from lib import core
from lib.core import Tool

SKILLS_SRC = core.REPO_ROOT / "agent-skills" / "skills"
INSTALLER = core.REPO_ROOT / "agent-skills" / "install.py"


def _targets() -> list:
    """Skill targets for this OS. The work Windows box drives both agents."""
    return ["copilot", "claude"] if core.detect_os() == "gitbash" else ["claude"]


def _skills_dir(target: str) -> Path:
    return Path.home() / (".copilot" if target == "copilot" else ".claude") / "skills"


def _custom_names() -> set:
    if not SKILLS_SRC.is_dir():
        return set()
    return {p.name for p in SKILLS_SRC.iterdir() if p.is_dir()}


def _installed() -> list:
    """Paths of our custom skills present in any target dir, as symlinks
    (macOS/Linux) or copies (Windows fallback)."""
    names = _custom_names()
    found = []
    for target in _targets():
        d = _skills_dir(target)
        if not d.is_dir():
            continue
        for entry in d.iterdir():
            if entry.name not in names:
                continue
            if entry.is_symlink():
                try:
                    if core.REPO_ROOT.resolve() in entry.resolve().parents:
                        found.append(entry)
                except OSError:
                    continue
            elif entry.is_dir():
                found.append(entry)
    return found


def _post() -> None:
    targets = _targets()
    core.run([sys.executable, str(INSTALLER), "--skills-only",
              "--target", "both" if len(targets) > 1 else targets[0]])
    core.ok("Agent skills setup complete.")
    if core.detect_os() == "gitbash":
        core.info("Community skills and VS Code prompt files are not part of "
                  "this step — run 'python agent-skills/install.py' directly "
                  "for the interactive picker.")


def _uninstall() -> None:
    names = sorted(_custom_names())
    if not names:
        return
    targets = _targets()
    core.run([sys.executable, str(INSTALLER), "--uninstall", ",".join(names),
              "--target", "both" if len(targets) > 1 else targets[0]])


def _probe() -> bool:
    return bool(_installed())


TOOL = Tool(
    name="agent-skills",
    doc="Custom agent skills into ~/.claude (+ ~/.copilot on Windows)",
    platforms=frozenset({"macos", "linux", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
