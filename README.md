# .dotfiles

One-command setup for a new machine. Primary target: **macOS**. Secondary: **Windows via WSL Ubuntu** (shell/tools inside WSL, VS Code settings on the Windows side).

Every script is **idempotent** — safe to re-run any time; anything already installed or linked is skipped.

## Quick start — new MacBook

```sh
git clone https://github.com/<you>/.dotfiles.git ~/Dev/.dotfiles
cd ~/Dev/.dotfiles
./install.sh
```

Installs Homebrew (if missing), then sets up everything below. Open a new terminal when it finishes.

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
   ./install.sh
   ```
   macOS-only tools (iTerm2, Terminal.app) skip themselves automatically.
4. On the **Windows side** (not WSL):
   - Install a Nerd Font ([MesloLGS NF](https://github.com/romkatv/powerlevel10k-media/raw/master/MesloLGS%20NF%20Regular.ttf) or any from [nerdfonts.com](https://www.nerdfonts.com/)) — download, right-click → *Install for all users* — and set it as the font in Windows Terminal (Settings → Ubuntu profile → Appearance).
   - VS Code settings: run `vscode/setup.sh` from **Git Bash** (see [vscode/README.md](vscode/README.md)).
   - Optional: WezTerm instead of Windows Terminal (see [wezterm/README.md](wezterm/README.md)).

## Install a subset

```sh
./install.sh zsh nvim        # just these two
```

## What's inside

| Folder | What it sets up | Platforms |
|---|---|---|
| [`zsh/`](zsh/README.md) | zsh, CLI tools (bat, eza, fzf, zoxide, ripgrep, fd, htop), plugins, `~/.zshrc` | macOS, WSL |
| [`starship/`](starship/README.md) | Starship prompt + config | macOS, WSL |
| [`nvim/`](nvim/README.md) | Neovim DevOps IDE (k8s, Helm, Docker, Python, Ansible, Terraform) | macOS, WSL |
| [`wezterm/`](wezterm/README.md) | WezTerm terminal + config | macOS (Windows: manual) |
| [`vscode/`](vscode/README.md) | VS Code settings, keybindings, extensions | macOS, Windows (Git Bash) |
| [`claude/`](claude/README.md) | Claude Code CLI, settings, plugins + skills inventory, statusline | macOS, WSL |
| [`terminal-macos/`](terminal-macos/README.md) | Terminal.app themes + font | macOS only |
| [`iterm2/`](iterm2/README.md) | iTerm2 + theme profile + shell integration | macOS only |
| [`citrix-vdi/`](citrix-vdi/README.md) | Karabiner rule so Windows IDE shortcuts (Alt+F1, …) work in Citrix VDI | macOS only |
| `lib/` | Shared script helpers (OS detection, brew, symlinking) | — |
| `docs/` | Design specs and plans | — |
| `archived/` | Old configs and retired scripts, kept for reference | — |

## How configs are applied

Configs are **symlinked** from this repo into `$HOME` (e.g. `~/.zshrc → ~/Dev/.dotfiles/zsh/.zshrc`). Edit here, commit, `git pull` on other machines — changes are live immediately. Any pre-existing real file is backed up as `<name>.bak-YYYY-MM-DD` before linking. Exception: VS Code on Windows copies instead of linking (symlinks there need admin rights).

Machine-local shell tweaks that shouldn't be in git go in `~/.zshrc.local`.
