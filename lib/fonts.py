# lib/fonts.py
"""Nerd Font installation for Linux desktops.

macOS installs fonts as Homebrew casks (`font-meslo-lg-nerd-font`). Homebrew
on Linux has no cask support at all, so there is no equivalent: the release
tarball from ryanoasis/nerd-fonts is unpacked into the XDG user font dir
instead. That needs no sudo -- ~/.local/share/fonts is per-user.

The `family` on each font is the name a config file has to reference, and it
is not guessable from the archive name. The Nerd Fonts release yields
"MesloLGS Nerd Font Mono"; the MesloLGS NF files mirrored in
romkatv/powerlevel10k-media -- the download the top-level README points at
for Windows -- yield the *different* family "MesloLGS NF". ghostty/config
asks for the former, so the former is what gets installed here.

WSL is deliberately excluded: there the terminal renders on the Windows side
and the font has to be installed there, so a Linux-side install would be
invisible. Callers use `applicable()` to make that decision.
"""
from __future__ import annotations

import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

from lib import core

# Pinned rather than "latest": the family names below are only guaranteed
# for a release that has actually been checked against them.
NERD_FONTS_VERSION = "v3.5.1"
_RELEASE_URL = ("https://github.com/ryanoasis/nerd-fonts/releases/download/"
                f"{NERD_FONTS_VERSION}")


@dataclass(frozen=True)
class NerdFont:
    archive: str          # release asset stem, e.g. "Meslo" -> Meslo.tar.xz
    family: str           # fc-list family name, as configs reference it
    keep_prefix: str      # only extract members starting with this

    @property
    def url(self) -> str:
        return f"{_RELEASE_URL}/{self.archive}.tar.xz"

    @property
    def install_dir(self) -> Path:
        return font_dir() / f"{self.archive}NerdFont"


# Ghostty + iTerm2 both ask for "MesloLGS Nerd Font Mono" (ghostty/config).
# Meslo.tar.xz also carries LGL/LGM/LGSDZ cuts nothing here references.
MESLO = NerdFont("Meslo", "MesloLGS Nerd Font Mono", "MesloLGSNerdFont")
# Neovim's UI icons; macOS installs font-jetbrains-mono-nerd-font for this.
JETBRAINS_MONO = NerdFont("JetBrainsMono", "JetBrainsMono Nerd Font",
                          "JetBrainsMonoNerdFont")


def font_dir() -> Path:
    return Path.home() / ".local" / "share" / "fonts"


def applicable() -> bool:
    """True only on a Linux machine that draws its own glyphs."""
    return core.detect_os() == "linux" and not core.is_wsl()


def have_family(family: str) -> bool:
    """True when fontconfig can already resolve `family` by that exact name.

    fc-list is matched rather than fc-match because fc-match always answers
    with *some* font -- it substitutes silently, which is the failure this
    check exists to catch."""
    if not core.have("fc-list"):
        return False
    listed = core.run(["fc-list", "--format", "%{family}\\n"],
                      check=False, capture=True)
    if listed.returncode != 0:
        return False
    families = {name.strip()
                for line in listed.stdout.splitlines()
                for name in line.split(",")}
    return family in families


def _members(tar: tarfile.TarFile, prefix: str) -> list:
    keep = []
    for member in tar.getmembers():
        name = Path(member.name).name
        if not member.isfile() or not name.startswith(prefix):
            continue
        if not name.lower().endswith((".ttf", ".otf")):
            continue
        # Flatten: the archives are flat today, but never trust a path
        # out of a tarball.
        member.name = name
        keep.append(member)
    return keep


def install(font: NerdFont) -> None:
    """Download and install one Nerd Font, then refresh the font cache.

    Idempotent: a family fontconfig already resolves is left alone."""
    if have_family(font.family):
        core.ok(f"{font.family} already installed.")
        return

    core.info(f"Installing {font.family} ({NERD_FONTS_VERSION})...")
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / f"{font.archive}.tar.xz"
        try:
            with urllib.request.urlopen(font.url, timeout=120) as resp, \
                    archive.open("wb") as out:
                shutil.copyfileobj(resp, out)
        except (urllib.error.URLError, OSError) as exc:
            raise core.DotfilesError(
                f"Could not download {font.archive} from {font.url}: {exc}") \
                from exc

        font.install_dir.mkdir(parents=True, exist_ok=True)
        with tarfile.open(archive, "r:xz") as tar:
            members = _members(tar, font.keep_prefix)
            if not members:
                raise core.DotfilesError(
                    f"No '{font.keep_prefix}*' faces inside {font.archive}"
                    ".tar.xz — the release layout changed.")
            tar.extractall(font.install_dir, members=members)
    core.ok(f"Installed {len(members)} faces -> {font.install_dir}")

    if core.have("fc-cache"):
        core.run(["fc-cache", "-f", str(font_dir())], check=False)
    if have_family(font.family):
        core.ok(f"{font.family} is resolvable by fontconfig.")
    else:
        core.warn(f"{font.family} installed but fontconfig does not resolve "
                  "it yet — log out and back in, or run 'fc-cache -f'.")


def ensure(font: NerdFont) -> None:
    """install() on a Linux desktop; explain the skip anywhere else."""
    if core.detect_os() == "macos":
        return
    if core.is_wsl():
        core.skip("Fonts render from the Windows-side terminal on WSL — "
                  "install a Nerd Font on Windows (see README).")
        return
    if core.detect_os() != "linux":
        return
    install(font)


def installed_families() -> Tuple[str, ...]:
    """Which of our fonts are present — used by status probes."""
    return tuple(f.family for f in (MESLO, JETBRAINS_MONO)
                 if have_family(f.family))
