# lib/ui.py
"""Interactive checkbox menu and prompts. Stdlib only; I/O injectable for tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional, Set

MARK_ON = "[x]"
MARK_OFF = "[ ]"


@dataclass(frozen=True)
class MenuItem:
    label: str
    status: str
    enabled: bool


def parse_numbers(raw: str, count: int) -> Optional[Set[int]]:
    """Parse 1-based indices from '3 7' or '3,7'. None on any invalid token."""
    tokens = [t for t in raw.replace(",", " ").split() if t]
    if not tokens:
        return None
    out = set()
    for t in tokens:
        if not t.isdigit():
            return None
        n = int(t)
        if not 1 <= n <= count:
            return None
        out.add(n)
    return out


def _draw(items: List[MenuItem], selected: Set[int], print_fn) -> None:
    print_fn("")
    for i, item in enumerate(items):
        if not item.enabled:
            print_fn(f"   –  [{i + 1}] {item.label:<15} {item.status}")
        else:
            mark = MARK_ON if i in selected else MARK_OFF
            print_fn(f"  {mark} [{i + 1}] {item.label:<15} {item.status}")
    print_fn("")
    print_fn("Toggle: numbers (space/comma separated), a=all, n=none, "
             "enter=confirm, q=quit")


def interactive_select(items: List[MenuItem],
                       input_fn: Callable = input,
                       print_fn: Callable = print) -> List[int]:
    """Checkbox selection loop. Returns selected 0-based indices ([] = quit)."""
    selected: Set[int] = set()
    while True:
        _draw(items, selected, print_fn)
        raw = input_fn("> ").strip().lower()
        if raw == "":
            return sorted(selected)
        if raw == "q":
            return []
        if raw == "a":
            selected = {i for i, item in enumerate(items) if item.enabled}
            continue
        if raw == "n":
            selected = set()
            continue
        nums = parse_numbers(raw, len(items))
        if nums is None:
            print_fn("Invalid selection.")
            continue
        for n in nums:
            i = n - 1
            if not items[i].enabled:
                print_fn(f"{items[i].label}: {items[i].status} — not selectable.")
                continue
            selected.symmetric_difference_update({i})


def choose_action(input_fn: Callable = input,
                  print_fn: Callable = print) -> str:
    while True:
        raw = input_fn("[i]nstall / [u]ninstall / [q]uit > ").strip().lower()
        if raw in ("i", "install"):
            return "install"
        if raw in ("u", "uninstall"):
            return "uninstall"
        if raw in ("q", "quit", ""):
            return "quit"
        print_fn("Please answer i, u or q.")


def confirm(prompt: str, input_fn: Callable = input) -> bool:
    return input_fn(f"{prompt} [y/N] ").strip().lower() in ("y", "yes")
