"""Tool registry. Order here is menu/run order (mirrors old ALL_TOOLS)."""
from __future__ import annotations

from lib.tools import (agent_skills, citrix_vdi, claude, ghostty, git, iterm2,
                       jetbrains, lazygit, maven, nvim, rancher_desktop,
                       starship, terminal_macos, vscode, wezterm, zsh)

_ALL = (
    zsh.TOOL,
    starship.TOOL,
    git.TOOL,
    lazygit.TOOL,
    nvim.TOOL,
    wezterm.TOOL,
    vscode.TOOL,
    jetbrains.TOOL,
    claude.TOOL,
    agent_skills.TOOL,
    maven.TOOL,
    terminal_macos.TOOL,
    iterm2.TOOL,
    ghostty.TOOL,
    citrix_vdi.TOOL,
    rancher_desktop.TOOL,
)

REGISTRY = {t.name: t for t in _ALL}
