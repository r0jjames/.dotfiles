# lazygit

[lazygit](https://github.com/jesseduffield/lazygit) — a terminal UI for git:
stage hunks, commit, rebase interactively, browse branches and reflog, resolve
conflicts, all without leaving the shell.

## Run

```sh
./install.py install lazygit
```

## What it does

- Installs `lazygit` via Homebrew (macOS + WSL Ubuntu)
- Symlinks [`config.yml`](config.yml) into lazygit's config directory
- The `lg` alias lives in [`zsh/.zshrc`](../zsh/.zshrc)

## Platforms

lazygit is **not macOS-only**. Homebrew covers macOS and Linux/WSL, which is
what this repo installs. On Windows outside WSL it ships via
`winget install JesseDuffield.lazygit` (also scoop, choco) — not managed here,
same as the rest of the shell stack.

## Config location

lazygit does not use one path everywhere. The installer resolves it the same
way lazygit does:

| Condition | Config file |
|---|---|
| `XDG_CONFIG_HOME` set | `$XDG_CONFIG_HOME/lazygit/config.yml` |
| macOS | `~/Library/Application Support/lazygit/config.yml` |
| Linux / WSL | `~/.config/lazygit/config.yml` |

Check what lazygit itself thinks with `lazygit --print-config-dir`.

## What's configured

- Nerd Font icons (v3) — the MesloLGS font the terminal tools already install
- Colors matching the Tango-on-purple theme in
  [`ghostty/config`](../ghostty/config) and [`iterm2/`](../iterm2/README.md)
- File tree view, full commit graph, no startup popups
- `nvim` as the editor, matching the `vim`/`vi`/`v` aliases

Everything else is left at lazygit's defaults on purpose: lazygit **rewrites
this file in place** when a config key is renamed between versions (it prints
what it migrated on startup), so a short file means fewer surprise diffs in
this repo. Commit them when they show up.

## Keys worth knowing

| Key | Does |
|---|---|
| `?` | Keybinding help for the focused panel |
| `space` | Stage / unstage the selected file or hunk |
| `c` | Commit |
| `p` / `P` | Pull / push |
| `enter` on a file | Line-by-line staging |
| `i` on a commit | Interactive rebase from here |
| `z` / `ctrl+z` | Undo / redo (via reflog) |
| `q` | Quit |

## Uninstall

```sh
./install.py uninstall lazygit
```

Removes the link and restores any `.bak-*` backup. The brew package stays —
`brew uninstall lazygit` if you want it gone.
