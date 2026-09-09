# lib/tools/node.py
"""Node.js from the official tarball, unpacked under ~/.local.

Not apt and not a version manager, both for the same reason: Claude Code
plugin hooks run as `/bin/sh -c`, which never sources a shell rc. A manager
that exports PATH from .zshrc leaves `node` unresolvable there (the caveman
plugin's SessionStart hook fails with "node: not found"), while apt's Ubuntu
24.04 candidate is an EOL 18.x. A fixed path under ~/.local/bin — already on
PATH via .profile, so it survives into non-interactive shells — resolves for
both. Bump _NODE_VERSION to upgrade, as with _JAVA_VERSION in maven.py."""
from __future__ import annotations

import hashlib
import platform
import shutil
import tempfile
import urllib.request
from pathlib import Path

from lib import core
from lib.core import Tool

_NODE_VERSION = "24.21.0"          # LTS "Krypton"
_BASE_URL = "https://nodejs.org/dist"
_LOCAL = Path.home() / ".local"
_BIN = _LOCAL / "bin"
_BINARIES = ("node", "npm", "npx")


def _dist_name() -> str:
    """e.g. node-v24.21.0-linux-x64 — the directory the tarball unpacks to."""
    os_name = core.detect_os()
    plat = {"macos": "darwin", "linux": "linux"}[os_name]
    machine = platform.machine().lower()
    arch = {"x86_64": "x64", "amd64": "x64",
            "aarch64": "arm64", "arm64": "arm64"}.get(machine)
    if arch is None:
        raise core.DotfilesError(
            f"No Node.js build for architecture {machine}. "
            f"See {_BASE_URL}/v{_NODE_VERSION}/")
    return f"node-v{_NODE_VERSION}-{plat}-{arch}"


def _install_dir() -> Path:
    return _LOCAL / _dist_name()


def _fetch(url: str, dest: Path) -> None:
    with urllib.request.urlopen(url, timeout=60) as resp, \
            dest.open("wb") as out:
        shutil.copyfileobj(resp, out)


def _verify(tarball: Path, sums: Path) -> None:
    """Check the tarball against the release's own SHASUMS256.txt."""
    digest = hashlib.sha256(tarball.read_bytes()).hexdigest()
    for line in sums.read_text().splitlines():
        expected, _, name = line.partition("  ")
        if name.strip() == tarball.name:
            if expected != digest:
                raise core.DotfilesError(
                    f"Checksum mismatch for {tarball.name}: "
                    f"expected {expected}, got {digest}")
            return
    raise core.DotfilesError(f"{tarball.name} absent from SHASUMS256.txt")


def _download_and_extract() -> None:
    dist = _dist_name()
    release = f"{_BASE_URL}/v{_NODE_VERSION}"
    with tempfile.TemporaryDirectory() as tmp:
        tarball = Path(tmp) / f"{dist}.tar.gz"
        sums = Path(tmp) / "SHASUMS256.txt"
        core.info(f"Downloading {dist}...")
        _fetch(f"{release}/{tarball.name}", tarball)
        _fetch(f"{release}/SHASUMS256.txt", sums)
        _verify(tarball, sums)
        _LOCAL.mkdir(parents=True, exist_ok=True)
        core.run(["tar", "-xzf", str(tarball), "-C", str(_LOCAL)])


def _link_binaries() -> None:
    _BIN.mkdir(parents=True, exist_ok=True)
    src_dir = _install_dir() / "bin"
    for name in _BINARIES:
        src, target = src_dir / name, _BIN / name
        if target.is_symlink() or target.exists():
            target.unlink()
        target.symlink_to(src)
    core.ok(f"Linked {', '.join(_BINARIES)} into {_BIN}")


def _post() -> None:
    if _probe():
        core.ok(f"Node.js {_NODE_VERSION} already installed.")
        return
    if not _install_dir().exists():
        _download_and_extract()
    _link_binaries()
    if not core.have("node"):
        core.warn(f"{_BIN} is not on PATH — add it in your shell config, "
                  "otherwise plugin hooks still will not find node.")


def _uninstall() -> None:
    for name in _BINARIES:
        target = _BIN / name
        if target.is_symlink() and _install_dir() in target.resolve().parents:
            target.unlink()
    shutil.rmtree(_install_dir(), ignore_errors=True)
    core.ok(f"Removed Node.js {_NODE_VERSION}.")


def _probe() -> bool:
    node = _BIN / "node"
    return node.is_symlink() and node.resolve() == _install_dir() / "bin" / "node"


TOOL = Tool(
    name="node",
    doc="Node.js LTS (official tarball under ~/.local)",
    platforms=frozenset({"macos", "linux"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
