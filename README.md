# .dotfiles

One-command setup for a new machine. Primary target: **macOS**. Also supported: **Ubuntu** — either a native desktop (Ghostty, fonts and all) or **Windows via WSL** (shell/tools inside WSL, VS Code settings on the Windows side).

Everything is **idempotent** — safe to re-run any time; anything already installed or linked is skipped. Requires only the system `python3` (3.9+, stdlib only).

## Quick start — new MacBook

```sh
git clone https://github.com/<you>/.dotfiles.git ~/Dev/.dotfiles
cd ~/Dev/.dotfiles
./install.py            # interactive: pick tools, install or uninstall
```

Installs Homebrew (if missing), then sets up whatever you select. Open a new terminal when it finishes.

Non-interactive:

```sh
./install.py install            # everything applicable to this OS
./install.py install zsh nvim   # subset
./install.py uninstall vscode   # remove links/configs (brew packages stay)
./install.py status             # what's installed
```

## Quick start — Ubuntu desktop (native)

**No Homebrew here** — Ubuntu's own archive carries nearly everything, so
apt is the package source and a second package manager would be redundant.

```sh
git clone git@github.com:r0jjames/.dotfiles.git ~/Development/.dotfiles
cd ~/Development/.dotfiles
./install.py install
```

Run it from a terminal you can type a password into: apt, `chsh` and the
Ghostty PPA all call `sudo`. macOS-only tools (iTerm2, Terminal.app,
Karabiner, Rancher) skip themselves. When it finishes, **log out and back
in** — `chsh` only takes effect on a new login session, and newly installed
fonts need a fresh session.

Four things Ubuntu 24.04 cannot supply are installed under `~/.local`
instead, needing no root (see [`lib/apt.py`](lib/apt.py), and
[`lib/tools/node.py`](lib/tools/node.py) for `node`):

| Tool | Why not apt | Source |
|---|---|---|
| `starship`, `lazygit` | not packaged at all | upstream release binary |
| `neovim` | packaged, but 0.9.5 — [`nvim/config`](nvim/README.md)'s Mason, lspconfig and treesitter plugins need ≥ 0.10 | upstream tarball |
| `node` | packaged, but 18.x is EOL — and a version manager's PATH never reaches the non-interactive `/bin/sh` that Claude Code plugin hooks run in | upstream tarball |

Two apt packages install under a different command name (`bat` ships
`batcat`, `fd-find` ships `fdfind`, both to dodge Debian name collisions).
The `zsh` tool symlinks the expected names into `~/.local/bin`, because
`.zshrc` and the tmux project picker call `bat`/`fd` directly.

Unlike WSL, a native desktop draws its own glyphs, so the installer fetches
Nerd Fonts into `~/.local/share/fonts` (see [`lib/fonts.py`](lib/fonts.py))
rather than deferring to a Windows-side terminal. Ghostty comes from the
`ppa:mkasberg/ghostty-ubuntu` PPA on releases before 26.04, and from the
Ubuntu archive from 26.04 on.

The cloud CLIs the macOS build gets from brew — `kubectl`, `helm`,
`terraform`, `hadolint` — are **not** installed on Linux; each would need its
own third-party apt repo. `LINUX_EXTRA_CLIS` in
[`lib/tools/nvim.py`](lib/tools/nvim.py) records the gap, and the installer
prints which are missing.

`uv` **is** installed (a single static binary, no apt repo needed). It is not
optional on Linux: Ubuntu marks its Python `EXTERNALLY-MANAGED` (PEP 668) so
`pip install --user` is refused, and a stock desktop has neither pip nor
pipx — without `uv`, `agent-skills` cannot bootstrap external skill CLIs like
`graphify`.

## Quick start — work Windows machine (WSL Ubuntu)

1. Install WSL + Ubuntu (PowerShell as admin): `wsl --install -d Ubuntu`
2. Inside Ubuntu, install Homebrew's prerequisites:
   ```sh
   sudo apt-get update && sudo apt-get install -y build-essential curl file git zsh
   ```
3. Clone and run:
   ```sh
   git clone git@github.com:r0jjames/.dotfiles.git ~/Dev/.dotfiles
   cd ~/Dev/.dotfiles
   ./install.py install
   ```
   macOS-only tools (iTerm2, Terminal.app) skip themselves automatically.
4. On the **Windows side** (not WSL):
   - Install the Nerd Font: download **Meslo** from the [Nerd Fonts releases](https://github.com/ryanoasis/nerd-fonts/releases/latest), then right-click the `MesloLGS` `.ttf` files → *Install for all users*.
     Take it from there and **not** from `powerlevel10k-media`: that mirror's files install under the family name `MesloLGS NF`, while the Nerd Fonts release installs `MesloLGS Nerd Font Mono` — which is the name [`ghostty/config`](ghostty/config) and `terminal-windows` ask for. The wrong one falls back silently to a non-Nerd font.
   - Theme Windows Terminal: run `./install.py install terminal-windows` from **Git Bash** — same palette and font as Ghostty, merged into `settings.json` (see [terminal-windows/README.md](terminal-windows/README.md)). Doing it by hand instead: Settings → Ubuntu profile → Appearance.
   - VS Code settings: run `./install.py install vscode` from **Git Bash** (see [vscode/README.md](vscode/README.md)).
   - Claude Code + agent skills for Copilot and Claude: run `./install.py install claude agent-skills` from **Git Bash** (see [claude/README.md](claude/README.md), [agent-skills/README.md](agent-skills/README.md)). Both copy instead of symlinking there — re-run after editing a config or skill.
   - Optional: WezTerm instead of Windows Terminal (see [wezterm/README.md](wezterm/README.md)).

## Uninstall

```sh
./install.py uninstall nvim vscode
```

Removes symlinks and repo-copied configs, restores `.bak-*` backups, and runs
tool-specific cleanup (e.g. Karabiner rules for `citrix-vdi`). Brew packages
are left installed — the summary lists them for manual removal.

## What's inside

| Folder | What it sets up | Platforms |
|---|---|---|
| [`zsh/`](zsh/README.md) | zsh, CLI tools (bat, eza, fzf, zoxide, ripgrep, fd, htop), plugins, `~/.zshrc` | macOS, Linux |
| [`starship/`](starship/README.md) | Starship prompt + config | macOS, Linux |
| [`git/`](git/README.md) | Global git ignore (`.tours/`, agent leftovers) + `core.excludesFile` | macOS, Linux, Windows (Git Bash) |
| [`lazygit/`](lazygit/README.md) | lazygit terminal UI for git + config (`lg` alias) | macOS, Linux |
| [`nvim/`](nvim/README.md) | Neovim DevOps IDE (k8s, Helm, Docker, Python, Ansible, Terraform) | macOS, Linux |
| [`docs/`](docs/cheatsheet-tmux-ghostty.md) | Ghostty + tmux keyboard cheat sheet (stock keys and this repo's additions) | — |
| [`tmux/`](tmux/README.md) | tmux + Ghostty-themed status bar, additive keys only, fzf project picker | macOS, Linux |
| [`ghostty/`](ghostty/README.md) | Ghostty terminal + config (Tango palette, MesloLGS Nerd Font) | macOS, Linux |
| [`wezterm/`](wezterm/README.md) | WezTerm terminal + config | macOS (Windows: manual) |
| [`vscode/`](vscode/README.md) | VS Code settings, keybindings, extensions | macOS, Windows (Git Bash) |
| [`jetbrains/`](jetbrains/README.md) | F-free cross-OS keymap for every JetBrains IDE — IntelliJ, PyCharm, GoLand (Mac/Windows/VDI) | macOS, Windows (Git Bash) |
| [`claude/`](claude/README.md) | Claude Code CLI, settings, plugins + skills inventory, statusline | macOS, Linux, Windows (Git Bash) |
| [`agent-skills/`](agent-skills/README.md) | Custom agent skills for Claude Code and GitHub Copilot | macOS, Linux, Windows (Git Bash) |
| `maven` | Maven build tool, via SDKMAN | macOS, Linux |
| `node` | Node.js LTS from the official tarball, symlinked into `~/.local/bin` — required by Claude Code plugin hooks | macOS, Linux |
| [`terminal-macos/`](terminal-macos/README.md) | Terminal.app themes + font | macOS only |
| [`terminal-ubuntu/`](terminal-ubuntu/README.md) | GNOME Terminal themed to match Ghostty (palette read from `ghostty/config`) | Ubuntu only |
| [`terminal-windows/`](terminal-windows/README.md) | Windows Terminal themed to match Ghostty — merged into `settings.json` | Windows (Git Bash) |
| [`iterm2/`](iterm2/README.md) | iTerm2 + theme profile + shell integration | macOS only |
| [`citrix-vdi/`](citrix-vdi/README.md) | Karabiner rule so Windows IDE shortcuts (Alt+F1, …) work in Citrix VDI | macOS only |
| `rancher-desktop` | Rancher Desktop (dockerd engine, Kubernetes disabled) — replaces Docker Desktop/OrbStack | macOS only |
| `lib/` | Installer engine + per-tool specs (`lib/tools/`); [`theme.py`](lib/theme.py) parses `ghostty/config` so every terminal shares one palette | — |
| `docs/` | Design specs and plans | — |
| `archived/` | Old configs and retired scripts, kept for reference | — |

## How configs are applied

Configs are **symlinked** from this repo into `$HOME` (e.g. `~/.zshrc → ~/Dev/.dotfiles/zsh/.zshrc`). Edit here, commit, `git pull` on other machines — changes are live immediately.

The clone path itself is not fixed: everything resolves relative to `install.py`, so the repo works from wherever it is cloned (`~/Dev/.dotfiles` on the Mac, `~/Development/.dotfiles` on the Ubuntu laptop). The commands below just pick one; substitute your own. To find where a linked config actually came from, follow the link — `readlink -f ~/.zshrc`. Any pre-existing real file is backed up as `<name>.bak-YYYY-MM-DD` before linking. Exception: on Windows (Git Bash) `vscode`, `jetbrains`, `claude` and `agent-skills` copy instead of linking (symlinks there need admin rights or Developer Mode) — re-run the installer after editing to refresh the copies.

Machine-local shell tweaks that shouldn't be in git go in `~/.zshrc.local`.
