#!/usr/bin/env python3
"""Dotfiles installer. Interactive:
    ./install.py
Non-interactive:
    ./install.py install [tool...]     # no tools = all applicable
    ./install.py uninstall <tool...>   # explicit tools required
    ./install.py status | list
    ./install.py --yes ...             # skip confirmation prompts
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import core, ui                     # noqa: E402
from lib.tools import REGISTRY               # noqa: E402


def current_os() -> str:
    return core.detect_os()


def applicable(tool: core.Tool, os_name: str) -> bool:
    return os_name in tool.platforms


def resolve_tools(names: List[str], os_name: str) -> List[core.Tool]:
    """Map CLI names to Tools; raise DotfilesError on unknown names."""
    unknown = [n for n in names if n not in REGISTRY]
    if unknown:
        raise core.DotfilesError(
            f"Unknown tool(s): {', '.join(unknown)}. "
            f"Available: {' '.join(REGISTRY)}")
    return [REGISTRY[n] for n in names]


def run_batch(action: str, batch: List[core.Tool], os_name: str) -> int:
    failures = []
    for tool in batch:
        if not applicable(tool, os_name):
            core.skip(f"{tool.name} is not applicable on {os_name}, skipping.")
            continue
        print(f"\n===== {tool.name} =====")
        try:
            if action == "install":
                core.install_tool(tool)
            else:
                core.uninstall_tool(tool)
        except (core.DotfilesError, subprocess.CalledProcessError,
                OSError) as exc:
            core.warn(f"{tool.name} failed: {exc}")
            failures.append(tool.name)
    print()
    if failures:
        core.warn(f"Failed: {', '.join(failures)}")
        return 1
    if action == "install":
        core.ok("All done. Open a new terminal for shell changes to take effect.")
    else:
        core.ok("Uninstall done. Brew packages were left installed — "
                "remove manually if unwanted.")
    return 0


def cmd_status(os_name: str) -> int:
    for tool in REGISTRY.values():
        if applicable(tool, os_name):
            status = core.tool_status(tool)
        else:
            status = f"{'/'.join(sorted(tool.platforms))} only"
        print(f"  {tool.name:<15} {status:<15} {tool.doc}")
    return 0


def interactive(os_name: str, assume_yes: bool) -> int:
    print(f"Dotfiles installer — {os_name}")
    items = []
    for tool in REGISTRY.values():
        if applicable(tool, os_name):
            items.append(ui.MenuItem(tool.name, core.tool_status(tool), True))
        else:
            items.append(ui.MenuItem(
                tool.name, f"{'/'.join(sorted(tool.platforms))} only", False))
    selected = ui.interactive_select(items)
    if not selected:
        print("Nothing selected.")
        return 0
    batch = [list(REGISTRY.values())[i] for i in selected]
    action = ui.choose_action()
    if action == "quit":
        return 0
    names = ", ".join(t.name for t in batch)
    if action == "uninstall" and not assume_yes:
        if not ui.confirm(f"Remove links/configs for: {names}?"):
            print("Aborted.")
            return 0
    return run_batch(action, batch, os_name)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Dotfiles installer")
    parser.add_argument("--yes", action="store_true",
                        help="skip confirmation prompts")
    sub = parser.add_subparsers(dest="command")
    p_install = sub.add_parser("install", help="install tools (default: all)")
    p_install.add_argument("tools", nargs="*")
    p_uninstall = sub.add_parser("uninstall", help="uninstall tools")
    p_uninstall.add_argument("tools", nargs="+")
    sub.add_parser("status", help="show per-tool status")
    sub.add_parser("list", help="list tool names")

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:  # argparse errors (e.g. uninstall w/o tools)
        return 1 if exc.code else 0

    try:
        os_name = current_os()
    except core.DotfilesError as exc:
        core.warn(str(exc))
        return 1

    try:
        if args.command is None:
            return interactive(os_name, args.yes)
        if args.command == "list":
            for name in REGISTRY:
                print(name)
            return 0
        if args.command == "status":
            return cmd_status(os_name)
        if args.command == "install":
            batch = (resolve_tools(args.tools, os_name) if args.tools
                     else list(REGISTRY.values()))
            return run_batch("install", batch, os_name)
        # uninstall
        batch = resolve_tools(args.tools, os_name)
        names = ", ".join(t.name for t in batch)
        if not args.yes and sys.stdin.isatty():
            if not ui.confirm(f"Remove links/configs for: {names}?"):
                print("Aborted.")
                return 0
        return run_batch("uninstall", batch, os_name)
    except core.DotfilesError as exc:
        core.warn(str(exc))
        return 1


if __name__ == "__main__":
    sys.exit(main())
