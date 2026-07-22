# .dotfiles

One-command setup for a new machine. Primary target: **macOS**. Secondary: **Windows via WSL Ubuntu** (shell/tools inside WSL, VS Code settings on the Windows side).

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
   - Install a Nerd Font ([MesloLGS NF](https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf) or any from [nerdfonts.com](https://www.nerdfonts.com/)) — download, right-click → *Install for all users* — and set it as the font in Windows Terminal (Settings → Ubuntu profile → Appearance).
   - VS Code settings: run `./install.py install vscode` from **Git Bash** (see [vscode/README.md](vscode/README.md)).
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
| [`zsh/`](zsh/README.md) | zsh, CLI tools (bat, eza, fzf, zoxide, ripgrep, fd, htop), plugins, `~/.zshrc` | macOS, WSL |
| [`starship/`](starship/README.md) | Starship prompt + config | macOS, WSL |
| [`nvim/`](nvim/README.md) | Neovim DevOps IDE (k8s, Helm, Docker, Python, Ansible, Terraform) | macOS, WSL |
| [`wezterm/`](wezterm/README.md) | WezTerm terminal + config | macOS (Windows: manual) |
| [`vscode/`](vscode/README.md) | VS Code settings, keybindings, extensions | macOS, Windows (Git Bash) |
| [`claude/`](claude/README.md) | Claude Code CLI, settings, plugins + skills inventory, statusline | macOS, WSL |
| `maven` | Maven build tool, via SDKMAN | macOS, WSL |
| [`terminal-macos/`](terminal-macos/README.md) | Terminal.app themes + font | macOS only |
| [`iterm2/`](iterm2/README.md) | iTerm2 + theme profile + shell integration | macOS only |
| [`citrix-vdi/`](citrix-vdi/README.md) | Karabiner rule so Windows IDE shortcuts (Alt+F1, …) work in Citrix VDI | macOS only |
| `lib/` | Installer engine + per-tool specs (`lib/tools/`) | — |
| `docs/` | Design specs and plans | — |
| `archived/` | Old configs and retired scripts, kept for reference | — |

## How configs are applied

Configs are **symlinked** from this repo into `$HOME` (e.g. `~/.zshrc → ~/Dev/.dotfiles/zsh/.zshrc`). Edit here, commit, `git pull` on other machines — changes are live immediately. Any pre-existing real file is backed up as `<name>.bak-YYYY-MM-DD` before linking. Exception: VS Code on Windows copies instead of linking (symlinks there need admin rights).

Machine-local shell tweaks that shouldn't be in git go in `~/.zshrc.local`.
