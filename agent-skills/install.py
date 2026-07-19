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
CAVEMAN_REPO_URL = "https://github.com/juliusbrussee/caveman.git"
CAVEMAN_BRANCH = "main"
ADDY_REPO_URL = "https://github.com/addyosmani/agent-skills.git"
ADDY_BRANCH = "main"

BOTH = ("copilot", "claude")

# Community sources. Per skill: targets it may install to, whether it is
# pre-selected (default) or an explicit cherry-pick, and an optional note
# shown when a target is skipped.
SOURCES = [
    {
        "label": "awesome-copilot",
        "url": AWESOME_REPO_URL,
        "branch": AWESOME_BRANCH,
        "cache": "awesome-copilot",
        "fallback": ZIP_FALLBACK_URL,
        "skills": {
            "code-tour": {"targets": BOTH, "default": True},
            "acquire-codebase-knowledge": {"targets": BOTH, "default": True},
            "context-map": {"targets": BOTH, "default": True},
            "architecture-blueprint-generator": {"targets": BOTH,
                                                 "default": True},
            "add-educational-comments": {"targets": BOTH, "default": True},
        },
    },
    {
        "label": "caveman",
        "url": CAVEMAN_REPO_URL,
        "branch": CAVEMAN_BRANCH,
        "cache": "caveman",
        "fallback": "https://github.com/juliusbrussee/caveman/tree/main/skills",
        "skills": {
            "caveman": {"targets": ("copilot",), "default": True,
                        "note": "claude uses the caveman plugin"},
        },
    },
    {
        "label": "addy-agent-skills",
        "url": ADDY_REPO_URL,
        "branch": ADDY_BRANCH,
        "cache": "addy-agent-skills",
        "fallback": "https://github.com/addyosmani/agent-skills/tree/main/skills",
        "skills": {
            # Chained by investigate-issue on Copilot; Claude uses
            # superpowers:systematic-debugging instead.
            "debugging-and-error-recovery": {
                "targets": ("copilot",), "default": True,
                "note": "claude uses superpowers:systematic-debugging"},
            "observability-and-instrumentation": {"targets": BOTH,
                                                  "default": False},
            "ci-cd-and-automation": {"targets": BOTH, "default": False},
            "security-and-hardening": {"targets": BOTH, "default": False},
            "deprecation-and-migration": {"targets": BOTH, "default": False},
        },
    },
    {
        "label": "anthropics-skills",
        "url": "https://github.com/anthropics/skills.git",
        "branch": "main",
        "cache": "anthropics-skills",
        "fallback": "https://github.com/anthropics/skills/tree/main/skills",
        "skills": {
            "pdf": {"targets": BOTH, "default": False},
            "docx": {"targets": BOTH, "default": False},
            "pptx": {"targets": BOTH, "default": False},
            "xlsx": {"targets": BOTH, "default": False},
        },
    },
]


def registry():
    """{skill_name: (source, meta)} across all sources."""
    return {name: (source, meta)
            for source in SOURCES
            for name, meta in source["skills"].items()}


def source_by_label(label):
    return next(s for s in SOURCES if s["label"] == label)


def all_community_names():
    return set(registry())


def default_community_names():
    return {n for n, (_, meta) in registry().items() if meta["default"]}


# Legacy constants, derived — external callers and tests rely on them.
COMMUNITY_SKILLS = list(source_by_label("awesome-copilot")["skills"])
CAVEMAN_SKILLS = list(source_by_label("caveman")["skills"])
ADDY_SKILLS = list(source_by_label("addy-agent-skills")["skills"])


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


def target_root(target):
    return Path.home() / (".copilot" if target == "copilot"
                          else ".claude") / "skills"


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
    items += [("community", n) for n in sorted(all_community_names())]
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


# Legacy cache dirs pre-date the registry; keep them authoritative so
# existing caches (and tests that patch them) stay valid.
_LEGACY_CACHE_FUNCS = {"awesome-copilot": "cache_dir",
                       "caveman": "caveman_cache_dir",
                       "addy-agent-skills": "addy_cache_dir"}


def source_cache_dir(source):
    fn_name = _LEGACY_CACHE_FUNCS.get(source["label"])
    if fn_name:
        return globals()[fn_name]()
    return Path.home() / ".agent-skills-cache" / source["cache"]


def update_source_cache(source, dry_run, names=None):
    names = sorted(names) if names else sorted(source["skills"])
    return update_repo_cache(
        source_cache_dir(source), source["url"], source["branch"],
        [f"skills/{n}" for n in names], dry_run, source["label"],
        source["fallback"])


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
    return update_source_cache(source_by_label("awesome-copilot"), dry_run)


def update_caveman_cache(dry_run):
    return update_source_cache(source_by_label("caveman"), dry_run)


def update_addy_cache(dry_run):
    return update_source_cache(source_by_label("addy-agent-skills"), dry_run)


def install_community_for_target(target, dest_root, sel_community, dry_run):
    """Install selected community skills for one target, honoring each
    skill's target policy. Sources carry their fetched cache under
    '_cache' (None = fetch failed or skipped)."""
    results = []
    for source in SOURCES:
        cache = source.get("_cache")
        for name, meta in source["skills"].items():
            if name not in sel_community:
                continue
            if target not in meta["targets"]:
                note = meta.get("note", "not for " + target)
                results.append((target, name, f"skipped ({note})"))
                continue
            if not cache:
                continue
            src = cache / "skills" / name
            if not src.is_dir():
                results.append((target, name, "missing in cache — skipped"))
                continue
            results.append((target, name,
                            install_copy(src, dest_root / name, dry_run)))
    return results


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
        sel_community = default_community_names()

    if args.skills_only:
        log("--skills-only: skipping community skills")
        for source in SOURCES:
            source["_cache"] = None
    else:
        for source in SOURCES:
            wanted = sel_community & set(source["skills"])
            source["_cache"] = (update_source_cache(source, args.dry_run,
                                                    names=wanted)
                                if wanted else None)

    results = []
    for target in targets:
        dest_root = target_root(target)
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
        results.extend(install_community_for_target(
            target, dest_root, sel_community, args.dry_run))
        if target == "copilot":
            results.extend(install_prompts(args.dry_run, names=sel_prompts))

    print_summary(results, targets, args.dry_run)


if __name__ == "__main__":
    main()
