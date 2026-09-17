# lib/tools/vscode.py
"""VS Code: settings, keybindings, extensions.
  macOS              — copies into ~/Library/Application Support/Code/User
  Linux (Ubuntu)     — copies into ~/.config/Code/User
  Windows (Git Bash) — copies into $APPDATA/Code/User
  WSL                — VS Code lives on the Windows host; run from Git Bash

Copies, never symlinks: VS Code's Settings Sync owns the installed file and
rewrites it on every sync-down. A symlink would send that write straight into
the repo. Re-run the installer after editing a config file here.
"""
from __future__ import annotations

import filecmp
import os
import shutil
from pathlib import Path

from lib import core
from lib.core import Tool

_FILES = ("settings.json", "keybindings.json")

# extensions.txt platform tags -> detect_os() names ("gitbash" is the
# work Windows machine; VS Code runs on the Windows host there).
_TAG_TO_OS = {"@macos": "macos", "@linux": "linux", "@windows": "gitbash"}


def parse_extensions(text: str, os_name: str) -> list[str]:
    """Extension ids from extensions.txt that apply to os_name.

    Line format: `<ext-id> [@macos|@linux|@windows ...]  # comment`.
    Untagged lines apply to every platform; unknown tags never match.
    """
    exts = []
    for line in text.splitlines():
        tokens = line.split("#", 1)[0].split()
        if not tokens:
            continue
        ext, tags = tokens[0], tokens[1:]
        if tags and os_name not in {_TAG_TO_OS.get(t) for t in tags}:
            continue
        exts.append(ext)
    return exts


def _target() -> Path:
    """Return the VS Code User directory for this platform."""
    os_name = core.detect_os()
    if os_name == "macos":
        return Path.home() / "Library/Application Support/Code/User"
    if os_name == "linux":
        return Path.home() / ".config/Code/User"
    if os_name == "gitbash":
        appdata = os.environ.get("APPDATA")
        if not appdata:
            raise core.DotfilesError("APPDATA not set; cannot locate VS Code user dir.")
        return Path(appdata) / "Code/User"
    raise core.DotfilesError(f"vscode: unsupported platform ({os_name}).")


def _unlink_legacy(src: Path, target: Path) -> None:
    """Drop a symlink left by the old link mode, so the copy that follows
    lands on a real file instead of writing through the link.

    Ours (resolves to src) is removed outright — the repo holds the content.
    Any other symlink has its content backed up first. Real files are left
    for copy_file, which backs them up itself."""
    if not target.is_symlink():
        return
    if target.exists() and target.resolve() != src.resolve():
        backup = core._backup_path(target)
        if not backup.exists():
            core.info(f"Backing up {target} -> {backup}")
            shutil.copy2(target, backup)
    target.unlink()
    core.info(f"Removed legacy symlink {target} (copy mode now).")


def _install_extensions() -> None:
    # Full path from which(): on Windows the CLI is code.cmd, which
    # subprocess can't resolve from the bare name (no PATHEXT lookup).
    code = shutil.which("code")
    if not code:
        core.warn("'code' CLI not found — skipping extension install.")
        core.warn("In VS Code: Cmd/Ctrl+Shift+P -> 'Shell Command: Install "
                  "code command in PATH', then re-run.")
        return
    core.info("Installing extensions (skipping already installed)...")
    installed = {line.strip().lower() for line in
                 core.run([code, "--list-extensions"],
                          capture=True).stdout.splitlines()}
    ext_file = core.REPO_ROOT / "vscode" / "extensions.txt"
    expected = parse_extensions(ext_file.read_text(), core.detect_os())
    for ext in expected:
        if ext.lower() in installed:
            core.ok(f"{ext} already installed.")
            continue
        core.info(f"Installing {ext}...")
        result = core.run([code, "--install-extension", ext], check=False)
        if result.returncode != 0:
            core.warn(f"Failed to install {ext} (continuing).")
    _report_extras(installed, expected)


def _report_extras(installed: set[str], expected: list[str]) -> None:
    """List installed extensions missing from extensions.txt (report only)."""
    extras = sorted(installed - {ext.lower() for ext in expected})
    if not extras:
        return
    core.warn(f"{len(extras)} installed extension(s) not in extensions.txt "
              "— add them there or uninstall:")
    for ext in extras:
        print(f"    code --uninstall-extension {ext}")


def _post() -> None:
    target_dir = _target()
    core.info("Applying VS Code settings + keybindings (copy)...")
    for name in _FILES:
        src = core.REPO_ROOT / "vscode" / name
        target = target_dir / name
        _unlink_legacy(src, target)
        core.copy_file(src, target)
    _install_extensions()


def _uninstall() -> None:
    target_dir = _target()
    for name in _FILES:
        src = core.REPO_ROOT / "vscode" / name
        core.uncopy_file(src, target_dir / name)
    core.info("Extensions left installed — remove in VS Code if unwanted.")


def _probe() -> bool:
    try:
        target_dir = _target()
    except core.DotfilesError:
        return False
    for name in _FILES:
        src = core.REPO_ROOT / "vscode" / name
        t = target_dir / name
        if t.is_symlink() or not t.exists():
            return False
        if not filecmp.cmp(str(src), str(t), shallow=False):
            return False
    return True


TOOL = Tool(
    name="vscode",
    doc="VS Code settings + keybindings + extensions",
    platforms=frozenset({"macos", "linux", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
