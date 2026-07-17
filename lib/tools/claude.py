# lib/tools/claude.py
"""Claude Code: CLI install + global settings + statusline. Plugins install
themselves on next `claude` start from settings.json."""
from __future__ import annotations

from lib import core
from lib.core import Link, Tool


def _install_cli() -> None:
    if core.have("claude"):
        version = core.run(["claude", "--version"],
                           check=False, capture=True).stdout.strip()
        core.ok(f"Claude Code already installed: {version}")
        return
    core.info("Installing Claude Code CLI (native installer)...")
    result = core.run("curl -fsSL https://claude.ai/install.sh | bash",
                      shell=True, check=False)
    if result.returncode != 0:
        raise core.DotfilesError(
            "Installer failed. See https://claude.com/claude-code for options.")
    core.ok("Claude Code installed. Installer puts it in ~/.local/bin; "
            "open a new terminal if 'claude' is not found.")
    core.info("Plugins listed in settings.json install automatically on the "
              "next 'claude' start.")


TOOL = Tool(
    name="claude",
    doc="Claude Code CLI + global settings",
    platforms=frozenset({"macos", "linux"}),
    links=(Link("claude/settings.json", "~/.claude/settings.json"),
           Link("claude/statusline-command.sh", "~/.claude/statusline-command.sh"),
           Link("claude/CLAUDE.md", "~/.claude/CLAUDE.md")),
    post_install=_install_cli,
)
