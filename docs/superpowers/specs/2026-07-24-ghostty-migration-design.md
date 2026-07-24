# Ghostty migration (iTerm2 retained as fallback)

**Date:** 2026-07-24
**Status:** Approved

## Goal

Add a `ghostty` terminal to the dotfiles that reproduces iTerm2's exact color
theme and font, primarily for running the Claude CLI. iTerm2 stays fully
installed and configured so the user can switch back at any time.

## Constraints

- Do **not** modify, uninstall, or degrade the existing iTerm2 setup
  (`iterm2/`, `lib/tools/iterm2.py`, its dynamic profile, or `zsh/.zshrc`
  shell-integration sourcing).
- Reuse what iTerm2 already provides: the color palette, and the MesloLGS Nerd
  Font cask (`font-meslo-lg-nerd-font`).
- Follow the existing dotfiles tool pattern (config dir + `lib/tools/<name>.py`
  + registry entry, run via `./install.py install <name>`).
- Config is **keymap-free**. The user checks out `.dotfiles` inside a
  Citrix VDI and sets keybindings there directly, so no `keybind =` lines
  belong in the shared config.

## Non-goals (YAGNI)

- No symlinking (the repo copies config files; match that).
- No iTerm2 shell-integration reuse — Ghostty injects shell integration
  automatically, so nothing is curled and nothing is sourced in `.zshrc`.
- No changes to `zsh/.zshrc` or any iTerm2 file.
- No keybindings in the shared config (handled per-environment by the user).

## Architecture

Three pieces, mirroring `iterm2/` + `lib/tools/iterm2.py` + registry:

### 1. `ghostty/` config directory

- **`ghostty/config`** — plain-text Ghostty config. Sections:

  Colors (translated 1:1 from `iterm2/com.dotfiles.json`, a Tango palette on a
  custom purple background):

  ```
  background = 300a24
  foreground = eeeeec
  cursor-color = bbbbbb
  cursor-text = 300a24
  selection-background = b5d5ff
  selection-foreground = eeeeec

  palette = 0=#2e3436
  palette = 1=#cc0000
  palette = 2=#4e9a06
  palette = 3=#c4a000
  palette = 4=#3465a4
  palette = 5=#75507b
  palette = 6=#06989a
  palette = 7=#d3d7cf
  palette = 8=#555753
  palette = 9=#ef2929
  palette = 10=#8ae234
  palette = 11=#fce94f
  palette = 12=#729fcf
  palette = 13=#ad7fa8
  palette = 14=#34e2e2
  palette = 15=#eeeeec
  ```

  Font (same cask as iTerm2):

  ```
  font-family = MesloLGS Nerd Font
  font-size = 13
  ```

  Sane defaults (low-risk, easy to trim):

  ```
  window-padding-x = 8
  window-padding-y = 8
  cursor-style = block
  copy-on-select = false
  macos-titlebar-style = tabs
  ```

- **`ghostty/README.md`** — mirrors `iterm2/README.md`: how to run, what it
  does, how to tweak the theme.

### 2. `lib/tools/ghostty.py`

Clone of `lib/tools/iterm2.py`'s structure using `lib.core`:

- `_config_src()` → `REPO_ROOT / "ghostty" / "config"`
- `_config_target()` → `~/.config/ghostty/config`
- `_post()`:
  - If `/Applications/Ghostty.app` is a dir → `core.ok` (already installed),
    else `core.brew_install("ghostty", cask=True)`.
  - `core.brew_install("font-meslo-lg-nerd-font", cask=True)` (no-op if the
    iTerm2 tool already installed it).
  - `core.copy_file(_config_src(), _config_target())`.
  - `core.ok("Ghostty setup complete. ...")`. No shell-integration step —
    Ghostty auto-injects it.
- `_uninstall()`: `core.uncopy_file(...)`; leave app, font, and any user
  keymap alone.
- `_probe()`: target exists and `filecmp.cmp(src, target, shallow=False)`.
- `TOOL = Tool(name="ghostty", doc=..., platforms=frozenset({"macos"}),
  post_install=_post, extra_uninstall=_uninstall, status_probe=_probe)`.

### 3. Registry

`lib/tools/__init__.py`: add `ghostty` to the import group and insert
`ghostty.TOOL` into the `_ALL` tuple (placed next to `iterm2.TOOL`).

## Run

```sh
./install.py install ghostty
```

iTerm2 and Ghostty coexist. Nothing about iTerm2 changes.

## Testing / verification

- `python -c "from lib.tools import REGISTRY; print(REGISTRY['ghostty'])"`
  succeeds (module imports, registry wiring correct).
- `./install.py status` (or equivalent) lists `ghostty`.
- Every color/font value in `ghostty/config` matches `com.dotfiles.json`.
- After `./install.py install ghostty`: `~/.config/ghostty/config` exists and
  Ghostty launches with the purple theme + MesloLGS font.
