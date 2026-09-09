# lib/tools/nvim.py
"""Neovim DevOps IDE: neovim + DevOps CLIs, config symlinked to ~/.config/nvim.

Ubuntu packages neovim, but 24.04 ships 0.9.5 and this config's plugin set
(Mason, nvim-lspconfig, treesitter) needs >= 0.10 -- so on Linux the upstream
tarball goes into ~/.local instead of the apt build. See lib/apt.py.

The cloud CLIs in `brew` below are macOS-only for now: each would need its
own third-party apt repository or release binary on Ubuntu, which is a
bigger commitment than a terminal setup calls for. `LINUX_EXTRA_CLIS` records
what is missing so it is a deliberate gap rather than an oversight.
"""
from __future__ import annotations

from lib import core, fonts
from lib.core import Link, Tool

# Installed by brew on macOS; not yet wired up on Linux (see module
# docstring). uv is not here: it installs as a single static binary with no
# apt repo needed, and agent-skills needs it to bootstrap external skills.
LINUX_EXTRA_CLIS = ("kubectl", "helm", "terraform", "hadolint")


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
        # On WSL this skips (the Windows terminal draws the glyphs); on a
        # Linux desktop it unpacks the same family the macOS cask provides.
        fonts.ensure(fonts.JETBRAINS_MONO)

    # ---- Neovim itself ----
    if core.detect_os() == "linux":
        from lib import apt
        apt.install_neovim(minimum="0.10")
        apt.install_uv()
        missing = [c for c in LINUX_EXTRA_CLIS if not core.have(c)]
        if missing:
            core.skip(f"Not installed on Linux: {', '.join(missing)} — "
                      "install from their own apt repos if you need them.")

    if not core.have("nvim"):
        core.warn("nvim not on PATH — skipping plugin sync. Open a new "
                  "terminal and re-run: ./install.py install nvim")
        return

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
    # neovim is deliberately absent: apt's 0.9.5 is too old, _post fetches it.
    apt=("git", "ansible"),
    links=(Link("nvim/config", "~/.config/nvim"),),
    post_install=_post,
)
