# lib/tools/rancher_desktop.py
"""Rancher Desktop: container engine (dockerd/moby), Kubernetes disabled.
Replaces Docker Desktop and OrbStack as the local Docker-compatible engine
on this machine; neither was ever a dotfiles-managed tool."""
from __future__ import annotations

from pathlib import Path

from lib import core
from lib.core import Tool

_APP_PATH = Path("/Applications/Rancher Desktop.app")
_DOCKER_APP_PATH = Path("/Applications/Docker.app")

_RDCTL_SET_CMD = (
    "rdctl set --container-engine.name moby --kubernetes.enabled=false")


def _post() -> None:
    if _DOCKER_APP_PATH.is_dir():
        core.skip(
            f"{_DOCKER_APP_PATH} is not brew-managed — quit Docker "
            "Desktop and remove it manually (drag to Trash) when ready.")

    brew = core.ensure_brew()
    orbstack_listed = core.run([brew, "list", "--cask", "orbstack"],
                               check=False, capture=True)
    if orbstack_listed.returncode == 0:
        core.skip("orbstack cask still installed — remove it yourself "
                  "with: brew uninstall --cask orbstack")

    pgrep = core.run(["pgrep", "-x", "Docker"], check=False, capture=True)
    if pgrep.returncode == 0:
        core.warn("Docker Desktop is running — quit it before starting "
                  "Rancher Desktop (both bind the same docker socket path).")

    core.info(
        "Launch Rancher Desktop, complete the first-run setup, then run:\n"
        f"    {_RDCTL_SET_CMD}\n"
        "to set the container engine to moby and disable Kubernetes "
        "(rdctl's backend API isn't reachable until after first launch, "
        "so this can't be scripted here).")


def _uninstall() -> None:
    core.skip("Rancher Desktop app left installed — remove the "
              "rancher-desktop cask yourself if desired.")


def _probe() -> bool:
    return _APP_PATH.is_dir()


TOOL = Tool(
    name="rancher-desktop",
    doc="Rancher Desktop (dockerd/moby engine, Kubernetes disabled)",
    platforms=frozenset({"macos"}),
    casks=("rancher-desktop",),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
