# Python Interactive Installer Design

**Date:** 2026-07-17
**Status:** Approved

## Goal

Replace the bash install layer (`install.sh`, `lib/common.sh`, all per-tool
`setup.sh`, `citrix-vdi/uninstall.sh`) with a single Python 3 installer that:

- installs and **uninstalls** every tool symmetrically,
- offers an interactive checkbox menu with live install status,
- keeps working non-interactively for scripting,
- runs on a fresh macOS or WSL Ubuntu machine with **stdlib only** (no pip).

Behavior ports 1:1 from the existing shell scripts — no feature changes
smuggled into the migration.

## Decisions

| Decision | Choice |
|---|---|
| Migration depth | Full Python rewrite; shell layer deleted after port |
| Dependencies | Python stdlib only (fresh-machine bootstrap, no pip/uv) |
| Uninstall scope | Links/configs + tool-specific cleanup only; brew packages left installed, listed for manual removal |
| State | None — install status derived by checking whether a tool's links point into the repo |
| agent-skills | Stays a separate standalone `agent-skills/install.py`; new installer shells out to it |
| Architecture | Declarative `Tool` specs + optional hook functions (approach A) |

## Repo structure

```
install.py              # entry point: CLI + interactive menu (replaces install.sh)
lib/
  core.py               # engine: Tool/Link dataclasses, brew, backup/restore, OS detect, logging
  ui.py                 # stdlib checkbox menu, prompts, colored output
  tools/
    __init__.py         # registry: imports all specs, stable order, unique names
    zsh.py  starship.py  nvim.py  wezterm.py  vscode.py  claude.py
    agent_skills.py  terminal_macos.py  iterm2.py  citrix_vdi.py
tests/                  # unittest suite
```

Deleted after migration: `install.sh`, `lib/common.sh`, all ten `*/setup.sh`,
`citrix-vdi/uninstall.sh`. Config payloads (`.zshrc`, `settings.json`,
karabiner JSON, READMEs) stay in their per-tool folders — only the script
layer moves.

## Tool spec

```python
Tool(
    name="zsh",
    platforms={"macos", "linux"},
    brew=["bat", "eza", "fzf", "zoxide", "ripgrep", "fd", "htop",
          "zsh-autosuggestions", "zsh-syntax-highlighting"],
    links=[Link("zsh/.zshrc", "~/.zshrc")],
    post_install=...,      # optional callable(ctx) for OS quirks
    extra_uninstall=...,   # optional callable(ctx) for tool-specific cleanup
)
```

Engine order — install: brew packages → links → `post_install`.
Uninstall: `extra_uninstall` → remove links → restore newest `.bak-*` backup.
Both directions read the same spec, so symmetry is structural, not
disciplined.

`Link` semantics match today's `link_file`: skip when already linked
correctly, back up a real file/dir to `<target>.bak-YYYY-MM-DD` (one backup
per day; stale same-day target is dropped), then symlink.

Uninstall removes a link **only when it points into the repo** — a foreign
file at the target is left alone and reported.

## Per-tool mapping

| Tool | platforms | Beyond brew+links |
|---|---|---|
| starship | macos, linux | pure data |
| wezterm | macos | pure data (casks: wezterm, font-go-mono-nerd-font) |
| claude | macos, linux | `post_install`: curl-based CLI installer when `claude` missing |
| zsh | macos, linux | `post_install` on linux: apt install zsh, `chsh` |
| nvim | macos, linux | `post_install`: macOS Nerd Font cask; headless `Lazy! sync` + Mason install |
| vscode | macos, gitbash | own platform logic: macOS symlink, Git Bash copy-mode, WSL skip message; extensions from `extensions.txt`; `extra_uninstall` removes copied files and restores backups |
| agent-skills | macos, linux | `post_install`: `python3 agent-skills/install.py --target claude --skills-only`; `extra_uninstall`: remove `~/.claude/skills` symlinks pointing into repo |
| terminal-macos | macos | `post_install`: existing `defaults`/plist logic; `defaults` left alone on uninstall (noted in summary) |
| iterm2 | macos | same pattern as terminal-macos |
| citrix-vdi | macos | `post_install`: Karabiner rule merge (port of embedded python, now native); `extra_uninstall`: port of `uninstall.sh` rule removal |

## CLI

```
./install.py                      # interactive menu
./install.py install [tool...]    # no tools = all applicable to this OS
./install.py uninstall <tool...>  # explicit tools required, never implicit all
./install.py status               # table: tool, platform, installed/partial/not
./install.py list                 # names only
./install.py --yes ...            # skip confirmation prompts
```

## Interactive flow

```
Dotfiles installer — macOS

  [1] ✓ zsh            installed
  [2] ✓ starship       installed
  [3] ✗ nvim           not installed
  [10] – citrix-vdi    macOS only    (disabled when not applicable)

Toggle: numbers (space/comma separated), a=all, n=none, enter=confirm
Empty selection quits. Then: [i]nstall / [u]ninstall / [q]uit.
```

Status per tool: all links resolve into repo → `installed`; some →
`partial`; none → `not installed`. Tools with no links (agent-skills) define
a status probe in their spec.

Uninstall confirms once with the tool list (`Remove links for: nvim,
vscode? [y/N]`); install needs no confirmation (backups preserve existing
files). `--yes` skips prompts.

## Error handling

- Missing Homebrew → bootstrap install (port of `ensure_brew`, macOS +
  linuxbrew paths).
- A failing tool does not abort the batch: engine records the failure,
  continues, prints a red failure summary, exits 1. (Improves on today's
  `set -e` mid-run abort.)
- Unknown tool name on CLI → error listing available names, exit 1.
- Unsupported OS → error, exit 1 (as today).

## Testing

`unittest` in `tests/`, runnable via `python3 -m unittest discover tests`:

- Engine: link/backup/restore/status on a tmpdir; uninstall symmetry
  (install then uninstall restores prior state); foreign-file safety.
- Registry sanity: every spec imports, names unique, every `Link` source
  exists in the repo, platform sets valid.
- No mocked-brew integration theater; manual smoke = `status` plus
  install/uninstall of one tool.

## Out of scope

- Changing what any tool installs or configures.
- Removing brew packages on uninstall.
- State/manifest files.
- Touching `agent-skills/install.py` internals.
