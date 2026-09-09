# lib/apt.py
"""Package installation for Debian/Ubuntu.

macOS gets everything from Homebrew. A native Ubuntu desktop uses apt for
what the archive carries, because installing Homebrew there would mean a
second, redundant package manager for tools apt already has.

Three things Ubuntu 24.04's archive cannot supply are installed under
`~/.local` instead, which keeps them out of root's way and off apt's books:

  starship, lazygit  — not packaged at all
  neovim             — packaged, but 0.9.5; nvim/config's Mason,
                       nvim-lspconfig and treesitter plugins need >= 0.10

Two apt packages install under a different command name than everything else
in the world uses: `bat` ships `batcat` and `fd-find` ships `fdfind`, because
the obvious names collide with unrelated Debian packages. `zsh/.zshrc` and
`tmux/scripts/sessionizer.sh` both call `bat`/`fd` directly, so `shim()`
puts the expected names on PATH rather than scattering per-machine aliases.
"""
from __future__ import annotations

import os
import platform
import shutil
import tarfile
import tempfile
import urllib.error
import urllib.request
from pathlib import Path
from typing import Optional

from lib import core

# Release channels for the three tools apt cannot provide. Resolved at run
# time rather than pinned: these are leaf CLI tools, and a stale pin here
# would be a worse failure than a surprise minor bump.
_NEOVIM_REPO = "neovim/neovim"
_LAZYGIT_REPO = "jesseduffield/lazygit"
_STARSHIP_INSTALLER = "https://starship.rs/install.sh"


def local_bin() -> Path:
    return Path.home() / ".local" / "bin"


def local_opt() -> Path:
    return Path.home() / ".local" / "share" / "dotfiles-opt"


def arch() -> str:
    """Release-asset architecture for this machine."""
    machine = platform.machine()
    return {"x86_64": "x86_64", "amd64": "x86_64",
            "aarch64": "arm64", "arm64": "arm64"}.get(machine, machine)


# ---- apt ----
def installed(pkg: str) -> bool:
    result = core.run(["dpkg-query", "-W", "-f=${Status}", pkg],
                      check=False, capture=True)
    return result.returncode == 0 and "install ok installed" in result.stdout


def install(*pkgs: str) -> None:
    """apt-get install the packages that are missing. No-op when all present,
    so a re-run costs one dpkg-query per package and no sudo prompt."""
    missing = [p for p in pkgs if not installed(p)]
    if not missing:
        core.ok(f"apt: already installed: {', '.join(pkgs)}")
        return
    core.info(f"Installing via apt: {', '.join(missing)}...")
    core.run(["sudo", "apt-get", "update"])
    core.run(["sudo", "apt-get", "install", "-y", *missing])
    core.ok(f"apt: installed {', '.join(missing)}")


# ---- PATH shims for Debian's renamed binaries ----
def shim(name: str, target: str) -> None:
    """Put `name` on PATH in ~/.local/bin pointing at `target`.

    Only ever replaces a symlink this function could have made; a real
    binary of that name found earlier on PATH wins and is left alone."""
    if shutil.which(name) and not (local_bin() / name).is_symlink():
        core.ok(f"{name} already on PATH.")
        return
    target_path = shutil.which(target)
    if target_path is None:
        core.warn(f"{target} not found — cannot shim {name}.")
        return
    local_bin().mkdir(parents=True, exist_ok=True)
    link = local_bin() / name
    if link.is_symlink() or link.exists():
        if link.is_symlink() and os.readlink(link) == target_path:
            core.ok(f"{name} -> {target} already linked.")
            return
        if not link.is_symlink():
            core.skip(f"{link} is a real file — leaving alone.")
            return
        link.unlink()
    link.symlink_to(target_path)
    core.ok(f"Linked {link} -> {target_path}")


def unshim(name: str) -> None:
    link = local_bin() / name
    if link.is_symlink():
        link.unlink()
        core.ok(f"Removed shim {link}")


# ---- Downloads ----
def _latest_tag(repo: str) -> str:
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            import json
            return json.load(resp)["tag_name"]
    except (urllib.error.URLError, OSError, KeyError, ValueError) as exc:
        raise core.DotfilesError(
            f"Could not resolve the latest release of {repo}: {exc}") from exc


def _download(url: str, dest: Path) -> None:
    try:
        with urllib.request.urlopen(url, timeout=300) as resp, \
                dest.open("wb") as out:
            shutil.copyfileobj(resp, out)
    except (urllib.error.URLError, OSError) as exc:
        raise core.DotfilesError(f"Download failed: {url} ({exc})") from exc


def _extract_tar(archive: Path, dest: Path, strip_root: bool = False) -> Path:
    """Unpack a tarball into dest. With strip_root, drop the single top-level
    directory the archive wraps everything in. Returns the payload root."""
    dest.mkdir(parents=True, exist_ok=True)
    with tarfile.open(archive) as tar:
        members = tar.getmembers()
        for m in members:
            # Never trust a path out of a tarball.
            if m.name.startswith("/") or ".." in Path(m.name).parts:
                raise core.DotfilesError(
                    f"Refusing unsafe path in {archive.name}: {m.name}")
        tar.extractall(dest, members=members)
    if not strip_root:
        return dest
    entries = [p for p in dest.iterdir()]
    return entries[0] if len(entries) == 1 and entries[0].is_dir() else dest


def _version_of(cmd: str) -> str:
    """First line of `cmd --version`, or "" when cmd is not installed.

    check=False does not cover a missing executable -- subprocess raises
    FileNotFoundError before there is any exit status to ignore."""
    if not core.have(cmd):
        return ""
    out = core.run([cmd, "--version"], check=False, capture=True).stdout
    return out.strip().splitlines()[0] if out.strip() else ""


# ---- Tools apt cannot provide ----
def install_neovim(minimum: Optional[str] = "0.10") -> None:
    """Neovim from the upstream tarball into ~/.local.

    Ubuntu 24.04 ships 0.9.5, which nvim/config's plugin set does not
    support, so an apt neovim is upgraded rather than accepted."""
    current = _version_of("nvim")
    if current and _at_least(current, minimum):
        core.ok(f"Neovim already current enough: {current}")
        return
    if current:
        core.info(f"Neovim {current} is older than {minimum} — installing "
                  "the upstream build into ~/.local.")

    tag = _latest_tag(_NEOVIM_REPO)
    asset = f"nvim-linux-{arch()}.tar.gz"
    url = f"https://github.com/{_NEOVIM_REPO}/releases/download/{tag}/{asset}"
    core.info(f"Installing Neovim {tag} ({asset})...")

    target = local_opt() / "nvim"
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / asset
        _download(url, archive)
        staged = _extract_tar(archive, Path(tmp) / "x", strip_root=True)
        if target.exists():
            shutil.rmtree(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(staged), str(target))

    local_bin().mkdir(parents=True, exist_ok=True)
    link = local_bin() / "nvim"
    if link.is_symlink() or link.exists():
        link.unlink()
    link.symlink_to(target / "bin" / "nvim")
    core.ok(f"Neovim {tag} -> {link}")


def install_lazygit() -> None:
    if core.have("lazygit"):
        core.ok(f"lazygit already installed: {_version_of('lazygit')[:60]}")
        return
    tag = _latest_tag(_LAZYGIT_REPO)
    version = tag.lstrip("v")
    asset = f"lazygit_{version}_linux_{arch()}.tar.gz"
    url = f"https://github.com/{_LAZYGIT_REPO}/releases/download/{tag}/{asset}"
    core.info(f"Installing lazygit {tag}...")
    local_bin().mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        archive = Path(tmp) / asset
        _download(url, archive)
        payload = _extract_tar(archive, Path(tmp) / "x")
        binary = payload / "lazygit"
        if not binary.exists():
            raise core.DotfilesError(
                f"lazygit binary not found inside {asset}")
        shutil.copy2(binary, local_bin() / "lazygit")
    (local_bin() / "lazygit").chmod(0o755)
    core.ok(f"lazygit {tag} -> {local_bin() / 'lazygit'}")


def install_starship() -> None:
    if core.have("starship"):
        core.ok(f"starship already installed: {_version_of('starship')}")
        return
    core.info("Installing starship (official installer, ~/.local/bin)...")
    local_bin().mkdir(parents=True, exist_ok=True)
    result = core.run(
        f'curl -fsSL {_STARSHIP_INSTALLER} | sh -s -- --yes --bin-dir '
        f'"{local_bin()}"', shell=True, check=False)
    if result.returncode != 0 or not core.have("starship"):
        raise core.DotfilesError(
            "starship install failed. See https://starship.rs/guide/")
    core.ok("starship installed.")


def install_uv() -> None:
    """uv from the upstream installer into ~/.local/bin.

    Ubuntu 24.04 marks its Python EXTERNALLY-MANAGED (PEP 668), so
    `pip install --user` is refused outright and there is no pip or pipx on
    a stock desktop anyway. uv installs as a single static binary needing no
    Python of its own, and `uv tool install` is what
    agent-skills/install.py reaches for first when bootstrapping an external
    skill's CLI."""
    if core.have("uv"):
        core.ok(f"uv already installed: {_version_of('uv')}")
        return
    core.info("Installing uv (official installer, ~/.local/bin)...")
    local_bin().mkdir(parents=True, exist_ok=True)
    result = core.run(
        'curl -LsSf https://astral.sh/uv/install.sh | '
        f'env UV_INSTALL_DIR="{local_bin()}" INSTALLER_NO_MODIFY_PATH=1 sh',
        shell=True, check=False)
    if result.returncode != 0 or not (local_bin() / "uv").exists():
        raise core.DotfilesError(
            "uv install failed. See https://docs.astral.sh/uv/")
    core.ok(f"uv -> {local_bin() / 'uv'}")


def _at_least(version_text: str, minimum: str) -> bool:
    """Compare the first x.y found in `version_text` against `minimum`."""
    import re
    found = re.search(r"(\d+)\.(\d+)", version_text)
    if not found:
        return False
    want = tuple(int(p) for p in minimum.split(".")[:2])
    have = (int(found.group(1)), int(found.group(2)))
    return have >= want


def warn_if_local_bin_not_on_path() -> None:
    """~/.local/bin is on PATH by default in Ubuntu's ~/.profile, but only
    for login shells that sourced it — say so rather than fail silently."""
    entries = os.environ.get("PATH", "").split(os.pathsep)
    if str(local_bin()) not in entries:
        core.warn(f"{local_bin()} is not on PATH in this shell. zsh/.zshrc "
                  "adds it; open a new terminal after the install finishes.")
