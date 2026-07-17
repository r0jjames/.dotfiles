# lib/tools/nvim.py
"""Neovim DevOps IDE: neovim + DevOps CLIs, config symlinked to ~/.config/nvim."""
from __future__ import annotations

from lib import core
from lib.core import Link, Tool


def _post() -> None:
    # ---- Fonts (icons in the UI) ----
    if core.detect_os() == "macos":
        core.brew_install("fontconfig")
        fc = core.run(["fc-list"], check=False, capture=True).stdout
        if "nerd" in fc.lower():
            core.ok("Nerd Font already installed.")
        else:
            core.brew_install("font-jetbrains-mono-nerd-font", cask=True)
    else:
        core.skip("Fonts render from the Windows-side terminal on WSL — "
                  "install a Nerd Font on Windows (see README).")
    # ---- Plugins (headless) then Mason tools/servers ----
    core.info("Syncing Neovim plugins (lazy.nvim)...")
    core.run(["nvim", "--headless", "+Lazy! sync", "+qa"], check=False)
    core.info("Installing LSP servers, formatters, and linters (Mason)...")
    core.run(["nvim", "--headless",
              "-c", "autocmd User MasonToolsUpdateCompleted quitall",
              "-c", "MasonToolsInstall"], check=False)


TOOL = Tool(
    name="nvim",
    doc="Neovim DevOps IDE + CLIs",
    platforms=frozenset({"macos", "linux"}),
    brew=("git", "neovim", "kubectl", "helm", "ansible", "uv",
          "hadolint", "terraform"),
    links=(Link("nvim/config", "~/.config/nvim"),),
    post_install=_post,
)
