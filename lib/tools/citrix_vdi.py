# lib/tools/citrix_vdi.py
"""Citrix VDI (macOS only): Karabiner-Elements + a Citrix-scoped rule so
Windows IDE shortcuts (Alt+F1, Alt+F7, Shift+F6, ...) reach the VDI intact.
Runs on the Mac — nothing is installed inside the VDI."""
from __future__ import annotations

import filecmp
import json
import shutil
from datetime import date
from pathlib import Path

from lib import core
from lib.core import Tool


def _rules_srcs() -> list[Path]:
    return [
        core.REPO_ROOT / "citrix-vdi" / "karabiner-citrix.json",
        core.REPO_ROOT / "citrix-vdi" / "karabiner-nuphy-windows-mode.json",
    ]


def _assets_file() -> Path:
    return (Path.home() / ".config/karabiner/assets/complex_modifications"
            / "karabiner-citrix.json")


def _karabiner_config() -> Path:
    return Path.home() / ".config/karabiner/karabiner.json"


def remove_enabled_rules(rules_file: Path, config_file: Path) -> int:
    """Remove our rules (matched by description) from every profile in the
    live karabiner.json. Returns the number of rules removed; the file is
    rewritten only when something was removed."""
    ours = {r["description"] for r in
            json.loads(rules_file.read_text())["rules"]}
    config = json.loads(config_file.read_text())
    removed = 0
    for profile in config.get("profiles", []):
        rules = profile.get("complex_modifications", {}).get("rules", [])
        kept = [r for r in rules if r.get("description") not in ours]
        removed += len(rules) - len(kept)
        if len(kept) != len(rules):
            profile["complex_modifications"]["rules"] = kept
    if removed:
        config_file.write_text(json.dumps(config, indent=4) + "\n")
    return removed


def _post() -> None:
    if Path("/Applications/Karabiner-Elements.app").is_dir():
        core.ok("Karabiner-Elements already installed.")
    else:
        core.brew_install("karabiner-elements", cask=True)
    core.copy_file(_rules_src(), _assets_file())
    core.ok("citrix-vdi setup complete. One-time manual steps remain "
            "(Karabiner rule enable + Citrix keyboard preferences) — "
            "see citrix-vdi/README.md.")


def _uninstall() -> None:
    config = _karabiner_config()
    # ---- 1. Remove enabled rules from the live Karabiner config ----
    if not config.is_file():
        core.skip(f"No {config} — no enabled rules to remove.")
    else:
        backup = config.with_name(
            config.name + ".bak-" + date.today().isoformat())
        if not backup.exists():
            core.info(f"Backing up {config} -> {backup}")
            shutil.copy2(config, backup)
        removed = remove_enabled_rules(_rules_src(), config)
        if removed:
            core.ok(f"Removed {removed} enabled rule(s) from karabiner.json "
                    "(Karabiner reloads automatically).")
        else:
            core.ok("No Citrix/NuPhy rules enabled in karabiner.json.")
    # ---- 2. Remove the rule file from the assets folder ----
    if _assets_file().exists():
        _assets_file().unlink()
        core.ok(f"Removed {_assets_file()}")
    else:
        core.ok("Rule file already absent from assets folder.")
    # ---- 3. Manual follow-ups ----
    core.ok("citrix-vdi uninstall complete. Remaining manual steps:")
    print("  1. Citrix Workspace -> Preferences -> Keyboard -> Keyboard input"
          " mode -> Automatic (then reconnect the VDI session).")
    print("  2. NuPhy: free to use any mode and connection again.")
    print("  3. Optional, if Karabiner-Elements is otherwise unused: "
          "Karabiner-Elements -> Settings -> uninstall section, or "
          "brew uninstall --cask karabiner-elements")


def _probe() -> bool:
    t = _assets_file()
    return t.exists() and filecmp.cmp(str(_rules_src()), str(t), shallow=False)


TOOL = Tool(
    name="citrix-vdi",
    doc="Karabiner Citrix/NuPhy keyboard rules",
    platforms=frozenset({"macos"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
