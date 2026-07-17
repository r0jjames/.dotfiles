# lib/core.py
"""Engine for the dotfiles installer: logging, OS detection, link/copy ops.

Ported 1:1 from lib/common.sh. Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import filecmp
import platform as _platform
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Callable, Optional

REPO_ROOT = Path(__file__).resolve().parent.parent


class DotfilesError(Exception):
    """Fatal for the current tool; the batch runner catches it and continues."""


# ---- Logging (same emoji as lib/common.sh) ----
def info(msg: str) -> None:
    print(f"📦 {msg}")


def ok(msg: str) -> None:
    print(f"✅ {msg}")


def skip(msg: str) -> None:
    print(f"⏭️  {msg}")


def warn(msg: str) -> None:
    print(f"⚠️  {msg}", file=sys.stderr)


# ---- OS detection ----
def detect_os() -> str:
    """Return "macos", "linux" or "gitbash"; raise on anything else."""
    system = _platform.system()
    if system == "Darwin":
        return "macos"
    if system == "Linux":
        return "linux"
    if system == "Windows" or system.startswith(("MINGW", "MSYS")):
        return "gitbash"
    raise DotfilesError(
        f"Unsupported OS: {system}. Only macOS, Linux (WSL Ubuntu) and "
        "Git Bash (VS Code settings only) are supported.")


def is_wsl() -> bool:
    proc = Path("/proc/version")
    try:
        return "microsoft" in proc.read_text().lower()
    except OSError:
        return False


# ---- Backups ----
def _backup_path(target: Path) -> Path:
    return target.with_name(target.name + ".bak-" + date.today().isoformat())


def _restore_newest_backup(target: Path) -> None:
    backups = sorted(target.parent.glob(target.name + ".bak-*"))
    if backups:
        newest = backups[-1]
        newest.rename(target)
        ok(f"Restored backup {newest} -> {target}")


# ---- Symlinking (port of link_file in common.sh) ----
def link_file(src: Path, target: Path) -> None:
    """Symlink target -> src. Skip when already linked; back up a real
    file/dir to <target>.bak-YYYY-MM-DD first (one backup per day; a stale
    same-day target is dropped)."""
    if not src.exists():
        raise DotfilesError(f"link_file: source does not exist: {src}")

    if target.is_symlink() and target.resolve() == src.resolve():
        ok(f"{target} already linked.")
        return

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists() or target.is_symlink():
        backup = _backup_path(target)
        if backup.exists() or backup.is_symlink():
            # already backed up today; drop the stale copy
            if target.is_dir() and not target.is_symlink():
                shutil.rmtree(target)
            else:
                target.unlink()
        else:
            info(f"Backing up {target} -> {backup}")
            target.rename(backup)

    target.symlink_to(src)
    ok(f"Linked {target} -> {src}")


def unlink_file(src: Path, target: Path) -> bool:
    """Remove target only when it is a symlink to src; restore the newest
    .bak-* sibling. Foreign files/links are left alone. True when removed."""
    if not target.is_symlink():
        if target.exists():
            skip(f"{target} is not a dotfiles symlink — leaving alone.")
        return False
    if target.resolve() != src.resolve():
        skip(f"{target} points elsewhere — leaving alone.")
        return False
    target.unlink()
    ok(f"Removed link {target}")
    _restore_newest_backup(target)
    return True


# ---- Copying (port of copy_file in vscode/setup.sh, shared now) ----
def copy_file(src: Path, target: Path) -> None:
    """Copy with dated backup; skip when identical."""
    if target.exists() and filecmp.cmp(str(src), str(target), shallow=False):
        ok(f"{target} already up to date.")
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        backup = _backup_path(target)
        if not backup.exists():
            info(f"Backing up {target} -> {backup}")
            shutil.copy2(target, backup)
    shutil.copy2(src, target)
    ok(f"Copied {src} -> {target}")


def uncopy_file(src: Path, target: Path) -> bool:
    """Remove target only when identical to src; restore newest backup.
    A target the user modified is left alone. True when removed."""
    if not target.exists():
        return False
    if not filecmp.cmp(str(src), str(target), shallow=False):
        skip(f"{target} differs from repo copy — leaving alone.")
        return False
    target.unlink()
    ok(f"Removed {target}")
    _restore_newest_backup(target)
    return True


# ---- Subprocess ----
def run(cmd, check: bool = True, capture: bool = False, shell: bool = False):
    """Thin subprocess.run wrapper. cmd is a list, or a string when shell=True."""
    return subprocess.run(cmd, check=check, shell=shell,
                          capture_output=capture, text=True)


def have(name: str) -> bool:
    return shutil.which(name) is not None


# ---- Homebrew (port of ensure_brew/brew_install in common.sh) ----
_BREW_PATHS = (
    "/opt/homebrew/bin/brew",
    "/usr/local/bin/brew",
    "/home/linuxbrew/.linuxbrew/bin/brew",
)
_brew_cache: Optional[str] = None


def _find_brew() -> Optional[str]:
    found = shutil.which("brew")
    if found:
        return found
    for p in _BREW_PATHS:
        if Path(p).exists():
            return p
    return None


def ensure_brew() -> str:
    """Return the brew executable, installing Homebrew when missing."""
    global _brew_cache
    if _brew_cache:
        return _brew_cache
    brew = _find_brew()
    if brew is None:
        info("Installing Homebrew...")
        run('/bin/bash -c "$(curl -fsSL '
            'https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True)
        brew = _find_brew()
        if brew is None:
            raise DotfilesError(
                "Homebrew install failed or brew not on PATH. See https://brew.sh")
    _brew_cache = brew
    return brew


def brew_install(pkg: str, cask: bool = False) -> None:
    """Install pkg via brew only if missing (brew list check, as before)."""
    brew = ensure_brew()
    listed = run([brew, "list", pkg], check=False, capture=True)
    if listed.returncode == 0:
        ok(f"{pkg} already installed.")
        return
    info(f"Installing {pkg}...")
    cmd = [brew, "install"]
    if cask:
        cmd.append("--cask")
    cmd.append(pkg)
    run(cmd)


# ---- Tool model ----
@dataclass(frozen=True)
class Link:
    src: str      # repo-relative path (absolute allowed, used by tests)
    target: str   # target path, ~ expanded

    def src_path(self) -> Path:
        p = Path(self.src)
        return p if p.is_absolute() else REPO_ROOT / p

    def target_path(self) -> Path:
        return Path(self.target).expanduser()


@dataclass(frozen=True)
class Tool:
    name: str
    doc: str
    platforms: frozenset
    brew: tuple = ()
    casks: tuple = ()
    links: tuple = ()                       # tuple[Link, ...]
    post_install: Optional[Callable[[], None]] = None
    extra_uninstall: Optional[Callable[[], None]] = None
    status_probe: Optional[Callable[[], bool]] = None  # tools without links


INSTALLED = "installed"
PARTIAL = "partial"
NOT_INSTALLED = "not installed"


def link_ok(link: Link) -> bool:
    t = link.target_path()
    return t.is_symlink() and t.resolve() == link.src_path().resolve()


def tool_status(tool: Tool) -> str:
    if tool.links:
        done = sum(1 for l in tool.links if link_ok(l))
        if done == len(tool.links):
            return INSTALLED
        return PARTIAL if done else NOT_INSTALLED
    if tool.status_probe is not None:
        return INSTALLED if tool.status_probe() else NOT_INSTALLED
    return NOT_INSTALLED


def install_tool(tool: Tool) -> None:
    """brew packages -> links -> post_install."""
    if tool.brew or tool.casks:
        ensure_brew()
    for pkg in tool.brew:
        brew_install(pkg, cask=False)
    for pkg in tool.casks:
        brew_install(pkg, cask=True)
    for link in tool.links:
        link_file(link.src_path(), link.target_path())
    if tool.post_install is not None:
        tool.post_install()


def uninstall_tool(tool: Tool) -> None:
    """extra_uninstall -> remove links -> restore backups. Brew untouched."""
    if tool.extra_uninstall is not None:
        tool.extra_uninstall()
    for link in tool.links:
        unlink_file(link.src_path(), link.target_path())
