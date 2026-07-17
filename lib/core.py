# lib/core.py
"""Engine for the dotfiles installer: logging, OS detection, link/copy ops.

Ported 1:1 from lib/common.sh. Stdlib only, Python 3.9+.
"""
from __future__ import annotations

import filecmp
import platform as _platform
import shutil
import sys
from datetime import date
from pathlib import Path

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
