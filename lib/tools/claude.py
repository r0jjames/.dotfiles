# lib/tools/claude.py
"""Claude Code: CLI install + global settings + statusline. Plugins install
themselves on next `claude` start from settings.json.

  macOS/Linux        — symlinks into ~/.claude
  Windows (Git Bash) — copies into ~/.claude (symlinks need admin); re-run
                       after editing a config file to refresh them.
"""
from __future__ import annotations

import filecmp
from pathlib import Path
from typing import Tuple

from lib import core
from lib.core import Tool

_FILES = ("settings.json", "statusline-command.sh", "CLAUDE.md")


def _target() -> Tuple[Path, str]:
    """Return (config dir, mode) where mode is 'link' or 'copy'."""
    mode = "copy" if core.detect_os() == "gitbash" else "link"
    return Path.home() / ".claude", mode


def _install_cli() -> None:
    if core.have("claude"):
        version = core.run(["claude", "--version"],
                           check=False, capture=True).stdout.strip()
        core.ok(f"Claude Code already installed: {version}")
        return
    if core.detect_os() == "gitbash":
        _install_cli_windows()
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


def _install_cli_windows() -> None:
    """Git Bash: the Windows installer is a PowerShell script. A locked-down
    VDI may block it (execution policy, proxy) — fall back to instructions
    rather than failing the whole run."""
    core.info("Installing Claude Code CLI (Windows native installer)...")
    result = core.run(
        ["powershell", "-NoProfile", "-Command", "irm https://claude.ai/install.ps1 | iex"],
        check=False)
    if result.returncode != 0:
        core.warn("PowerShell installer failed (execution policy or proxy?).")
        core.warn("Install manually, then re-run this tool:")
        print('    powershell -c "irm https://claude.ai/install.ps1 | iex"')
        print("    npm install -g @anthropic-ai/claude-code   # alternative")
        return
    core.ok("Claude Code installed. Open a new terminal if 'claude' is not "
            "found.")
    core.info("Plugins listed in settings.json install automatically on the "
              "next 'claude' start.")


def _post() -> None:
    target_dir, mode = _target()
    core.info(f"Applying Claude Code settings ({mode})...")
    for name in _FILES:
        src = core.REPO_ROOT / "claude" / name
        if mode == "link":
            core.link_file(src, target_dir / name)
        else:
            core.copy_file(src, target_dir / name)
    _install_cli()


def _uninstall() -> None:
    target_dir, mode = _target()
    for name in _FILES:
        src = core.REPO_ROOT / "claude" / name
        if mode == "link":
            core.unlink_file(src, target_dir / name)
        else:
            core.uncopy_file(src, target_dir / name)
    core.info("Claude Code CLI left installed — remove manually if unwanted.")


def _probe() -> bool:
    target_dir, mode = _target()
    for name in _FILES:
        src = core.REPO_ROOT / "claude" / name
        t = target_dir / name
        if mode == "link":
            if not (t.is_symlink() and t.resolve() == src.resolve()):
                return False
        else:
            if not (t.exists()
                    and filecmp.cmp(str(src), str(t), shallow=False)):
                return False
    return True


TOOL = Tool(
    name="claude",
    doc="Claude Code CLI + global settings",
    platforms=frozenset({"macos", "linux", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
