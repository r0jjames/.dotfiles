# lib/tools/ghostty.py
"""Ghostty: app + config (theme + font reused from iTerm2).

  macOS — cask, plus the font-meslo-lg-nerd-font cask.
  Linux — apt. Ghostty is in the official Ubuntu archive from 26.04 on; on
          24.04 it comes from the maintainer's PPA. Homebrew on Linux has no
          casks, so the Nerd Font is unpacked from the upstream release by
          lib/fonts.py instead. Linux also makes Ghostty the default
          terminal; see _set_default_terminal.

One config serves both. ~/.config/ghostty/config is already the correct path
on Linux as well as macOS, and the `macos-*` keys in it are defined on every
platform (they are inert off macOS), so the file needs no per-OS branching.
"""
from __future__ import annotations

import filecmp
import shutil
from pathlib import Path

from lib import core, fonts
from lib.core import Tool

_PPA = "ppa:mkasberg/ghostty-ubuntu"


def _config_src() -> Path:
    return core.REPO_ROOT / "ghostty" / "config"


def _config_target() -> Path:
    return Path.home() / ".config/ghostty/config"


# ---- Install: macOS ----
def _install_macos() -> None:
    if Path("/Applications/Ghostty.app").is_dir():
        core.ok("Ghostty already installed.")
    else:
        core.brew_install("ghostty", cask=True)
    # Same font cask as iTerm2; no-op if already installed.
    core.brew_install("font-meslo-lg-nerd-font", cask=True)


# ---- Install: Linux ----
def _apt_has_candidate() -> bool:
    """True when apt can already resolve a ghostty package (Ubuntu 26.04+)."""
    policy = core.run(["apt-cache", "policy", "ghostty"],
                      check=False, capture=True)
    if policy.returncode != 0:
        return False
    for line in policy.stdout.splitlines():
        if line.strip().startswith("Candidate:"):
            return line.split(":", 1)[1].strip() not in ("(none)", "")
    return False


def _install_linux() -> None:
    if core.have("ghostty"):
        version = core.run(["ghostty", "--version"],
                           check=False, capture=True).stdout.strip()
        core.ok(f"Ghostty already installed: {version.splitlines()[0]}"
                if version else "Ghostty already installed.")
    else:
        if not core.have("apt-get"):
            raise core.DotfilesError(
                "Ghostty on Linux is installed here via apt. On a non-Debian "
                "distro, install it yourself (https://ghostty.org/docs/install"
                "/binary) and re-run — the config step will still apply.")
        if not _apt_has_candidate():
            core.info(f"Adding {_PPA} (Ghostty is not in this Ubuntu's "
                      "archive)...")
            if not core.have("add-apt-repository"):
                core.run(["sudo", "apt-get", "install", "-y",
                          "software-properties-common"])
            core.run(["sudo", "add-apt-repository", "-y", _PPA])
        core.info("Installing Ghostty...")
        core.run(["sudo", "apt-get", "update"])
        core.run(["sudo", "apt-get", "install", "-y", "ghostty"])

    # No casks on Linux Homebrew — fetch the same family from upstream.
    fonts.ensure(fonts.MESLO)


_ALTERNATIVES_LINK = "x-terminal-emulator"
_GNOME_TERMINAL_APP = "org.gnome.desktop.default-applications.terminal"


def is_default_terminal() -> bool:
    """True when x-terminal-emulator already resolves to Ghostty."""
    if not core.have("update-alternatives"):
        return False
    query = core.run(["update-alternatives", "--query", _ALTERNATIVES_LINK],
                     check=False, capture=True)
    if query.returncode != 0:
        return False
    for line in query.stdout.splitlines():
        if line.startswith("Value:"):
            return line.split(":", 1)[1].strip().endswith("/ghostty")
    return False


def _set_default_terminal() -> None:
    """Make Ghostty the default terminal on a Debian/GNOME desktop.

    Two levers, because different callers read different ones:

      * `update-alternatives x-terminal-emulator` — what Debian-packaged
        apps resolve through, and what GNOME's own terminal setting points
        at by default. Ghostty's .deb registers itself here at priority 40,
        below gnome-terminal, so auto mode keeps picking GNOME's; `--set`
        pins it manually.
      * `org.gnome.desktop.default-applications.terminal` — read directly by
        some GNOME apps. Pointed straight at ghostty rather than left to
        resolve indirectly.

    There is no XDG-level lever: `xdg-settings` on Ubuntu 24.04 knows only
    default-web-browser and default-url-scheme-handler, no default-terminal.
    """
    ghostty = shutil.which("ghostty")
    if ghostty is None:
        core.warn("ghostty not on PATH — leaving the default terminal alone.")
        return

    if is_default_terminal():
        core.ok("Ghostty is already the default terminal.")
    elif core.have("update-alternatives"):
        core.info("Setting Ghostty as the default terminal (needs sudo)...")
        result = core.run(
            ["sudo", "update-alternatives", "--set", _ALTERNATIVES_LINK,
             ghostty], check=False)
        if result.returncode != 0:
            core.warn("Could not set the x-terminal-emulator alternative — "
                      f"run: sudo update-alternatives --set "
                      f"{_ALTERNATIVES_LINK} {ghostty}")
        else:
            core.ok(f"{_ALTERNATIVES_LINK} -> {ghostty}")

    # GNOME's own key, when this is a GNOME session.
    if core.have("gsettings"):
        schemas = core.run(["gsettings", "list-schemas"],
                           check=False, capture=True)
        if _GNOME_TERMINAL_APP in schemas.stdout:
            core.run(["gsettings", "set", _GNOME_TERMINAL_APP, "exec",
                      "ghostty"], check=False)
            # Ghostty takes the command to run after -e, like most terminals.
            core.run(["gsettings", "set", _GNOME_TERMINAL_APP, "exec-arg",
                      "-e"], check=False)
            core.ok("GNOME's default terminal set to Ghostty.")
    core.info("Ctrl+Alt+T and 'Open in Terminal' follow this. Already-open "
              "windows keep their old terminal until relaunched.")


def _post() -> None:
    if core.detect_os() == "macos":
        _install_macos()
    else:
        _install_linux()
        _set_default_terminal()

    # ---- Config (color theme + font) ----
    core.copy_file(_config_src(), _config_target())

    # Ghostty auto-injects shell integration; nothing to source in .zshrc.
    core.ok("Ghostty setup complete. Restart Ghostty to pick up the config.")


def _uninstall() -> None:
    core.uncopy_file(_config_src(), _config_target())
    core.skip("Ghostty app and fonts left alone.")


def _probe() -> bool:
    t = _config_target()
    return t.exists() and filecmp.cmp(str(_config_src()), str(t), shallow=False)


TOOL = Tool(
    name="ghostty",
    doc="Ghostty + config (theme + font)",
    platforms=frozenset({"macos", "linux"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
