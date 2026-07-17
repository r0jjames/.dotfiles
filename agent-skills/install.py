#!/usr/bin/env python3
"""Install agent skills globally for GitHub Copilot and/or Claude Code.

Usage:
  python3 install.py --target claude
  python3 install.py --target copilot
  python3 install.py --target both --dry-run
  python3 install.py                # interactive target menu
  python3 install.py --target claude --skills-only   # skip community fetch

Python >= 3.8, standard library only.
Copilot gets copies; Claude gets per-skill symlinks (edit the repo, changes
are live). On filesystems without symlink support the installer falls back
to copying.
"""
import argparse
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent
SKILLS_SRC = REPO_ROOT / "skills"
PROMPTS_SRC = REPO_ROOT / "prompts"

AWESOME_REPO_URL = "https://github.com/github/awesome-copilot.git"
AWESOME_BRANCH = "main"
ZIP_FALLBACK_URL = "https://github.com/github/awesome-copilot/tree/main/skills"

COMMUNITY_SKILLS = [
    "code-tour",
    "acquire-codebase-knowledge",
    "context-map",
    "architecture-blueprint-generator",
    "add-educational-comments",
]


def log(msg):
    print(f"[skills] {msg}")


def ok(msg):
    print(f"[  ok  ] {msg}")


def warn(msg):
    print(f"[ warn ] {msg}", file=sys.stderr)


def dirs_equal(a, b):
    """Recursive content comparison of two directories (like diff -rq)."""
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.funny_files:
        return False
    _, mismatch, errors = filecmp.cmpfiles(a, b, cmp.common_files, shallow=False)
    if mismatch or errors:
        return False
    return all(dirs_equal(Path(a) / d, Path(b) / d) for d in cmp.common_dirs)


def install_copy(src, dest, dry_run):
    """Copy skill dir src -> dest. Returns 'installed'|'updated'|'up to date'."""
    src, dest = Path(src), Path(dest)
    if dest.is_symlink() or dest.is_file():
        if not dry_run:
            dest.unlink()
            shutil.copytree(src, dest)
        return "updated"
    if not dest.exists():
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(src, dest)
        return "installed"
    if dirs_equal(src, dest):
        return "up to date"
    if not dry_run:
        shutil.rmtree(dest)
        shutil.copytree(src, dest)
    return "updated"


def install_symlink(src, dest, dry_run):
    """Symlink dest -> src. Returns 'linked'|'already linked' or a copy
    status suffixed with ' (copy fallback)' when symlinks are unsupported."""
    src, dest = Path(src), Path(dest)
    if dest.is_symlink():
        if dest.resolve() == src.resolve():
            return "already linked"
        if not dry_run:
            dest.unlink()  # wrong or broken link: replace
    elif dest.exists():
        backup = dest.parent / (dest.name + ".bak")
        if not dry_run:
            if backup.is_symlink() or backup.is_file():
                backup.unlink()
            elif backup.is_dir():
                shutil.rmtree(backup)
            dest.rename(backup)
            log(f"backed up existing {dest.name} to {backup.name}")
    if dry_run:
        return "linked"
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        dest.symlink_to(src, target_is_directory=True)
        return "linked"
    except OSError:
        warn(f"symlink unsupported for {dest} — copying instead "
             "(re-run install.py after edits to refresh)")
        return install_copy(src, dest, dry_run=False) + " (copy fallback)"


def pick_targets(arg_target):
    """Resolve --target value (or interactive menu) to a list of targets."""
    if arg_target:
        return ["copilot", "claude"] if arg_target == "both" else [arg_target]
    print("Install skills for:")
    print("  1) GitHub Copilot   (~/.copilot/skills + VS Code prompts)")
    print("  2) Claude Code      (~/.claude/skills, symlinked)")
    print("  3) Both")
    choice = input("Choice [1-3]: ").strip()
    targets = {"1": ["copilot"], "2": ["claude"],
               "3": ["copilot", "claude"]}.get(choice)
    if not targets:
        sys.exit("Invalid choice — run again or pass --target.")
    return targets


def vscode_prompts_dir():
    """Locate the VS Code user prompts dir, or None if VS Code is absent."""
    candidates = []
    appdata = os.environ.get("APPDATA")
    if appdata:
        candidates.append(Path(appdata) / "Code" / "User")          # Windows
    candidates.append(Path.home() / "Library" / "Application Support"
                      / "Code" / "User")                            # macOS
    candidates.append(Path.home() / ".config" / "Code" / "User")    # Linux
    for c in candidates:
        if c.is_dir():
            return c / "prompts"
    return None


def install_prompts(dry_run):
    """Copy prompts/*.prompt.md into the VS Code user prompts dir."""
    results = []
    user_dir = vscode_prompts_dir()
    if user_dir is None:
        warn("VS Code user dir not found — prompt files not installed.")
        warn("Per-repo alternative: copy prompts/*.prompt.md into .github/prompts/")
        return results
    if not dry_run:
        user_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(PROMPTS_SRC.glob("*.prompt.md")):
        dest = user_dir / p.name
        if dest.exists() and filecmp.cmp(p, dest, shallow=False):
            status = "up to date"
        else:
            status = "updated" if dest.exists() else "installed"
            if not dry_run:
                shutil.copy2(p, dest)
        results.append(("copilot", f"prompt:{p.stem}", status))
    return results
