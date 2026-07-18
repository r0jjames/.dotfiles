#!/usr/bin/env python3
"""Install agent skills globally for GitHub Copilot and/or Claude Code.

Usage:
  python3 install.py --target claude
  python3 install.py --target copilot
  python3 install.py --target both --dry-run
  python3 install.py                # interactive: pick target + items
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

CAVEMAN_REPO_URL = "https://github.com/juliusbrussee/caveman.git"
CAVEMAN_BRANCH = "main"
CAVEMAN_SKILLS = ["caveman"]

# Chained by investigate-issue for root-cause discipline.
ADDY_REPO_URL = "https://github.com/addyosmani/agent-skills.git"
ADDY_BRANCH = "main"
ADDY_SKILLS = ["debugging-and-error-recovery"]


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


def build_items(custom_skills, prompt_files):
    """Ordered installable items as (kind, name): custom skills, prompt
    files, then community skills."""
    items = [("skill", n) for n in custom_skills]
    items += [("prompt", n) for n in prompt_files]
    items += [("community", n)
              for n in COMMUNITY_SKILLS + CAVEMAN_SKILLS + ADDY_SKILLS]
    return items


def pick_items(items):
    """Interactive toggle menu over (kind, name) items. All pre-selected.
    Number toggles one, 'a' toggles all, empty input confirms. Exits when
    nothing is selected."""
    selected = [True] * len(items)
    while True:
        print("\nSelect items to install:")
        for i, ((kind, name), on) in enumerate(zip(items, selected), 1):
            print(f"  [{'x' if on else ' '}] {i:2}) {kind:9} {name}")
        raw = input("Toggle number, 'a' = all, enter = confirm: ").strip().lower()
        if raw == "":
            chosen = [item for item, on in zip(items, selected) if on]
            if not chosen:
                sys.exit("Nothing selected — exiting without changes.")
            return chosen
        if raw == "a":
            value = not all(selected)
            selected = [value] * len(items)
        elif raw.isdigit() and 1 <= int(raw) <= len(items):
            idx = int(raw) - 1
            selected[idx] = not selected[idx]
        else:
            print("Invalid input.")


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


def install_prompts(dry_run, names=None):
    """Copy prompts/*.prompt.md into the VS Code user prompts dir.
    names: optional set of file names to install; None = all."""
    results = []
    user_dir = vscode_prompts_dir()
    if user_dir is None:
        warn("VS Code user dir not found — prompt files not installed.")
        warn("Per-repo alternative: copy prompts/*.prompt.md into .github/prompts/")
        return results
    if not dry_run:
        user_dir.mkdir(parents=True, exist_ok=True)
    for p in sorted(PROMPTS_SRC.glob("*.prompt.md")):
        if names is not None and p.name not in names:
            continue
        dest = user_dir / p.name
        if dest.exists() and filecmp.cmp(p, dest, shallow=False):
            status = "up to date"
        else:
            status = "updated" if dest.exists() else "installed"
            if not dry_run:
                shutil.copy2(p, dest)
        results.append(("copilot", f"prompt:{p.stem}", status))
    return results


def cache_dir():
    return Path.home() / ".agent-skills-cache" / "awesome-copilot"


def caveman_cache_dir():
    return Path.home() / ".agent-skills-cache" / "caveman"


def addy_cache_dir():
    return Path.home() / ".agent-skills-cache" / "addy-agent-skills"


def run_git(args):
    subprocess.run(["git", *args], check=True)


def update_repo_cache(cache, url, branch, sparse, dry_run, label,
                      fallback_url):
    """Sparse-clone/refresh a skills repo. Returns cache path or None when
    no usable cache exists."""
    if dry_run:
        log(f"dry-run: would clone/update {url} into {cache}")
        return cache if (cache / "skills").is_dir() else None
    try:
        if (cache / ".git").is_dir():
            log(f"Updating {label} cache...")
            run_git(["-C", str(cache), "sparse-checkout", "set", *sparse])
            run_git(["-C", str(cache), "fetch", "--depth", "1",
                     "origin", branch])
            run_git(["-C", str(cache), "reset", "--hard",
                     f"origin/{branch}"])
        else:
            log(f"Cloning {label} (sparse, only needed skills)...")
            cache.parent.mkdir(parents=True, exist_ok=True)
            run_git(["clone", "--depth", "1", "--filter=blob:none", "--sparse",
                     "-b", branch, url, str(cache)])
            run_git(["-C", str(cache), "sparse-checkout", "set", *sparse])
        ok(f"{label} cache ready")
        return cache
    except (subprocess.CalledProcessError, FileNotFoundError):
        warn(f"Could not clone/update {label} (offline? proxy?).")
        if (cache / "skills").is_dir():
            warn("Using existing local cache instead.")
            return cache
        warn(f"Fallback: download the skill folders as ZIP from {fallback_url}")
        warn(f"and unzip into {cache / 'skills'}, then re-run this script.")
        return None


def update_community_cache(dry_run):
    return update_repo_cache(
        cache_dir(), AWESOME_REPO_URL, AWESOME_BRANCH,
        [f"skills/{s}" for s in COMMUNITY_SKILLS], dry_run,
        "awesome-copilot", ZIP_FALLBACK_URL)


def update_caveman_cache(dry_run):
    return update_repo_cache(
        caveman_cache_dir(), CAVEMAN_REPO_URL, CAVEMAN_BRANCH,
        [f"skills/{s}" for s in CAVEMAN_SKILLS], dry_run,
        "caveman", "https://github.com/juliusbrussee/caveman/tree/main/skills")


def update_addy_cache(dry_run):
    return update_repo_cache(
        addy_cache_dir(), ADDY_REPO_URL, ADDY_BRANCH,
        [f"skills/{s}" for s in ADDY_SKILLS], dry_run,
        "addyosmani/agent-skills",
        "https://github.com/addyosmani/agent-skills/tree/main/skills")


def print_summary(results, targets, dry_run):
    print()
    title = "Planned actions (dry run)" if dry_run else "Install summary"
    log(title + ":")
    for target, name, status in results:
        print(f"  {target:8} {name:35} {status}")
    print()
    if "copilot" in targets:
        log("Verify Copilot:  /skills list  in Copilot CLI, or ask VS Code "
            "agent mode 'What skills do you have available?'")
    if "claude" in targets:
        log("Verify Claude:   ask 'what skills are available?' in a new "
            "claude session")


def main():
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--target", choices=["copilot", "claude", "both"],
                    help="where to install (omit for interactive menu)")
    ap.add_argument("--skills-only", action="store_true",
                    help="skip fetching community skills (offline/proxy)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print planned actions without writing anything")
    args = ap.parse_args()

    interactive = args.target is None
    targets = pick_targets(args.target)
    custom = sorted(p for p in SKILLS_SRC.iterdir() if p.is_dir())
    if not custom:
        sys.exit(f"No skills found in {SKILLS_SRC}")
    prompt_files = sorted(p.name for p in PROMPTS_SRC.glob("*.prompt.md"))

    if interactive:
        chosen = pick_items(build_items([p.name for p in custom],
                                        prompt_files))
        sel_skills = {n for k, n in chosen if k == "skill"}
        sel_prompts = {n for k, n in chosen if k == "prompt"}
        sel_community = {n for k, n in chosen if k == "community"}
        custom = [p for p in custom if p.name in sel_skills]
    else:
        sel_prompts = None
        sel_community = set(COMMUNITY_SKILLS + CAVEMAN_SKILLS + ADDY_SKILLS)

    community_src = None
    caveman_src = None
    addy_src = None
    if args.skills_only:
        log("--skills-only: skipping community and caveman skills")
    elif not sel_community:
        log("no community skills selected — skipping fetch")
    else:
        if sel_community & set(COMMUNITY_SKILLS):
            cache = update_community_cache(args.dry_run)
            if cache:
                community_src = cache / "skills"
        if sel_community & set(CAVEMAN_SKILLS):
            cave = update_caveman_cache(args.dry_run)
            if cave:
                caveman_src = cave / "skills"
        if sel_community & set(ADDY_SKILLS):
            addy = update_addy_cache(args.dry_run)
            if addy:
                addy_src = addy / "skills"

    results = []
    for target in targets:
        dest_root = Path.home() / (".copilot" if target == "copilot"
                                   else ".claude") / "skills"
        log(f"Target {target}: {dest_root}")
        if not args.dry_run:
            dest_root.mkdir(parents=True, exist_ok=True)
        for skill in custom:
            if target == "claude":
                status = install_symlink(skill, dest_root / skill.name,
                                         args.dry_run)
            else:
                status = install_copy(skill, dest_root / skill.name,
                                      args.dry_run)
            results.append((target, skill.name, status))
        for src_root, names in ((community_src, COMMUNITY_SKILLS),
                                (caveman_src, CAVEMAN_SKILLS),
                                (addy_src, ADDY_SKILLS)):
            if not src_root:
                continue
            for name in names:
                if name not in sel_community:
                    continue
                src = src_root / name
                if not src.is_dir():
                    results.append((target, name, "missing in cache — skipped"))
                    continue
                results.append((target, name,
                                install_copy(src, dest_root / name,
                                             args.dry_run)))
        if target == "copilot":
            results.extend(install_prompts(args.dry_run, names=sel_prompts))

    print_summary(results, targets, args.dry_run)


if __name__ == "__main__":
    main()
