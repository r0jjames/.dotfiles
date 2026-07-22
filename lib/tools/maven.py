# lib/tools/maven.py
"""Maven build tool, via SDKMAN (avoids brew's openjdk X11/cairo dep chain).
SDKMAN's own installer appends its init block to zsh/.zshrc on first run."""
from __future__ import annotations

from pathlib import Path

from lib import core
from lib.core import Tool

_SDKMAN_DIR = Path.home() / ".sdkman"
_SDKMAN_INIT = _SDKMAN_DIR / "bin" / "sdkman-init.sh"
_JAVA_VERSION = "21.0.5-tem"


def _sdk(cmd: str) -> None:
    core.run(["bash", "-c", f'source "{_SDKMAN_INIT}" && {cmd}'])


def _ensure_sdkman() -> None:
    if _SDKMAN_INIT.exists():
        core.ok("SDKMAN already installed.")
        return
    # SDKMAN's installer requires Bash 4+; macOS ships 3.2.
    core.brew_install("bash")
    core.info("Installing SDKMAN...")
    core.run('curl -s "https://get.sdkman.io" | bash', shell=True)


def _post() -> None:
    _ensure_sdkman()

    if (_SDKMAN_DIR / "candidates" / "java" / "current").exists():
        core.ok("Java already installed via SDKMAN.")
    else:
        core.info(f"Installing Temurin {_JAVA_VERSION} via SDKMAN...")
        _sdk(f"sdk install java {_JAVA_VERSION}")

    if (_SDKMAN_DIR / "candidates" / "maven" / "current").exists():
        core.ok("Maven already installed via SDKMAN.")
    else:
        core.info("Installing Maven via SDKMAN...")
        _sdk("sdk install maven")


def _uninstall() -> None:
    core.skip("SDKMAN candidates (java, maven) left installed — "
              "run `sdk uninstall maven <version>` manually if desired.")


def _probe() -> bool:
    return (_SDKMAN_DIR / "candidates" / "maven" / "current").exists()


TOOL = Tool(
    name="maven",
    doc="Maven build tool (via SDKMAN)",
    platforms=frozenset({"macos", "linux"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
