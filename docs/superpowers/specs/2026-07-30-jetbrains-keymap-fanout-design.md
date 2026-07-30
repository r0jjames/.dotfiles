# jetbrains: one keymap for every JetBrains IDE

**Date:** 2026-07-30
**Status:** approved, ready for implementation plan

## Problem

`roj-keymap` reaches IntelliJ only. `lib/tools/intellij.py` globs JetBrains
config dirs whose names start with `IdeaIC` or `IntelliJIdea`, so
`~/Library/Application Support/JetBrains/PyCharm2025.3/` — installed on the
personal Mac since April — has no `keymaps/` directory at all. PyCharm runs on
stock defaults, which means the F-row shortcuts this project exists to avoid.
GoLand will have the same gap the day it is installed.

The goal is one muscle memory across every IDE. This spec covers the JetBrains
family. VS Code parity was considered and deliberately cut — see
[Out of scope](#out-of-scope).

## Approach

Keep the single shared keymap per OS and widen distribution. The tool stops
provisioning IDEs and becomes purely "distribute `roj-keymap` to every
JetBrains IDE present on this machine".

Rejected alternatives:

- **Per-product keymap overlays** (`keymap-macos-pycharm.xml` …) rebinding
  IDEA-only actions to product equivalents. More files and more install logic
  to fix a handful of dead chords. Two shared files stay the source of truth.
- **Version-stamp glob** (`^[A-Za-z]+\d{4}\.\d+$`) covering every JetBrains
  product automatically. Rejected for an explicit allowlist: tests can assert
  an exact set, and installing a new IDE is rare enough that a one-line code
  change is acceptable.
- **Keeping app installation.** The `intellij-idea-ce` cask is deprecated
  upstream (disabled 2026-12-08), PyCharm already arrived outside dotfiles,
  and GoLand is licensed. Dropping provisioning removes the dying-cask problem
  and makes install idempotent across machines with different IDE sets.

## The tool

`lib/tools/intellij.py` → `lib/tools/jetbrains.py` (`git mv`, history
preserved).

```python
_PRODUCT_PREFIXES = ("IdeaIC", "IntelliJIdea", "PyCharm", "GoLand")
```

`"PyCharm"` as a `str.startswith` prefix already covers `PyCharmCE*` and
`PyCharmEdu*`; no extra entries needed. Non-IDE siblings in the JetBrains base
(`consentOptions`, `Toolbox`, the `bl`/`crl` files) never match.

Removed: `_CASK`, `_APP`, the `brew_install` call, the macOS
already-installed check, and the deprecated-cask NOTE comment. `_post()` keeps
exactly one job — place `roj-keymap.xml` into `<product>/keymaps/` for every
config dir found. macOS symlinks, Git Bash copies, unchanged.

`_src()` reads from `core.REPO_ROOT / "jetbrains"`.

```python
TOOL = Tool(
    name="jetbrains",
    doc="roj-keymap for every JetBrains IDE (IntelliJ, PyCharm, GoLand)",
    platforms=frozenset({"macos", "gitbash"}),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

Probe semantics unchanged: installed = keymap present and correct in **every**
config dir found; zero dirs found = not installed, with the existing warning to
launch the IDE once and re-run.

### Migration of existing installs

Installed Macs have `IdeaIC2025.2/keymaps/roj-keymap.xml` symlinked to
`…/.dotfiles/intellij/keymap-macos.xml`, which dangles once the directory is
renamed. `_post()` gets a cleanup beside the existing `Roj-Ffree.xml`
stale-file removal: if the target is a symlink resolving into the old
`intellij/` path, unlink it outright rather than letting `core.link_file`
rename it to `<target>.bak-YYYY-MM-DD`. Without this, `core.unlink_file` would
later "restore" a dangling symlink as the backup on uninstall.

No back-compat alias. `./install.py install intellij` reports an unknown tool —
explicit failure beats a silent shim. Windows machines must run
`./install.py install jetbrains` after pulling; the old copies are replaced
in place because the target filename (`roj-keymap.xml`) does not change.

## Product gaps

The two keymap files stay identical in their relocated chords (a test enforces
this). The initial worry was that IDEA-only ids — `CompileDirty` (`Alt+B`)
above all, since PyCharm does not compile — would be unknown in other products.

**Checked, and they are not.** All 65 `<action id>` values in
`keymap-macos.xml` were reverse-indexed against every `<action id="…">`
registration in PyCharm 2025.3's own jars (`Contents/lib/*.jar` plus
`Contents/plugins/*/lib/*.jar`): zero missing, `CompileDirty` included.

Two caveats this check does not settle:

- **Registered is not the same as useful.** `CompileDirty` exists in PyCharm's
  action set but has nothing to compile in a pure-Python project, so `Alt+B`
  likely fires an inert action rather than a dead chord. This follows the
  seventh-pass lesson in `jetbrains/README.md` — a name or label match is not a
  semantic match. Confirm behaviour in the running IDE, not from the jar.
- **GoLand is not installed on this Mac**, so the same sweep could not be run
  against it. Run it there before trusting the result for GoLand.

Either way, a shared file is safe: an id the IDE does not know is ignored
silently by the keymap reader — the chord is simply dead in that product,
nothing breaks and no warning appears. Documented in `jetbrains/README.md`
rather than worked around.

## Repo changes

| Path | Change |
|---|---|
| `intellij/` → `jetbrains/` | `git mv` — `keymap-macos.xml`, `keymap-windows.xml`, `plugins.txt`, `README.md`, `vdi-apply-keymap.ps1` |
| `lib/tools/intellij.py` → `lib/tools/jetbrains.py` | as above |
| `tests/test_intellij.py` → `tests/test_jetbrains.py` | `_INTELLIJ` → `_JETBRAINS`; import `jetbrains` |
| `lib/tools/__init__.py` | import + registry entry renamed, same slot after `vscode` |
| `jetbrains/README.md` | retitle for all products; install section drops the cask and states IDEs are installed by you (Toolbox/brew); add the product-gap note; cheatsheet and eight-pass history carry over unchanged |
| `jetbrains/vdi-apply-keymap.ps1` | raw-URL path `intellij/` → `jetbrains/`; config-dir glob widened to `PyCharm*` / `GoLand*` |
| `README.md` (root) | table row `intellij/` → `jetbrains/` with new description; rename in the line-79 copy-instead-of-symlink list |

Left alone: `docs/superpowers/specs/*` and `docs/superpowers/plans/*` are
historical records — renaming paths inside them would falsify what was true at
the time. `citrix-vdi/README.md` already reads "IntelliJ/PyCharm".

## Tests

Existing 13 tests in `tests/test_intellij.py` move over unchanged in substance.
One is rewritten:

`test_matches_community_and_ultimate_ignores_others` →
`test_matches_every_jetbrains_ide_ignores_non_ide_dirs`: builds a temp
JetBrains base containing `IdeaIC2026.1`, `IntelliJIdea2025.3`,
`PyCharm2025.3`, `PyCharmCE2024.1`, `GoLand2025.2`, `consentOptions`,
`Toolbox`, and a plain file; asserts `find_config_dirs` returns exactly the
five IDE dirs, sorted.

The keymap-content tests (no F-keys, mac/windows chords identical, no duplicate
chord within a file, unbound actions carry no shortcut, `KNOWN_CONFLICTS`
coverage) are unaffected by the rename and keep guarding both XML files.

## Verification

1. `python3 -m unittest discover -s tests < /dev/null` — all green.
2. `./install.py install jetbrains` on the Mac: reports two config dirs
   (`IdeaIC2025.2`, `PyCharm2025.3`), creates `PyCharm2025.3/keymaps/`, and
   replaces the dangling IntelliJ symlink without leaving a `.bak-*` file.
3. `./install.py status` shows `jetbrains` installed; no `intellij` entry.
4. In PyCharm: Settings → Keymap → `roj-keymap` appears in the dropdown, select
   it, confirm a Tier 1 chord fires (`Alt+R` rename) and check for red conflict
   markers introduced by Python-specific plugins.
5. `./install.py uninstall jetbrains` removes the keymap from both dirs and
   leaves no dangling backups.

Step 4 is the one that cannot be automated — PyCharm's own plugin set may claim
a chord IntelliJ's does not, and that only shows up in the running IDE. While
there, check whether `Alt+B` (`CompileDirty`) does anything useful in a Python
project; if it is inert, note it in the README's cheatsheet rather than
rebinding, per the shared-file decision above.

## Out of scope

**VS Code parity.** The stated goal is identical bindings across VS Code too,
and the direction was chosen: a full port of Tier 0/1/2 onto VS Code command
ids, Ctrl/Alt only, with the `Alt+-` leader expressed as VS Code two-stroke
chords (`"key": "alt+- r"`) — no third-party keymap extension, since
`k--kato.intellij-idea-keybindings` reproduces IntelliJ's F-row defaults, the
exact thing this project discarded. Roughly 50 hand-mapped commands, and
several IntelliJ actions have no VS Code equivalent (Extract Field, Change
Signature, Smart Step Into, Show Execution Point) so they need a nearest
command or an explicit "unmapped" note. It also replaces most of the current
`vscode/keybindings.json`. That is its own spec, written after this one ships
and gets used on real hardware.
