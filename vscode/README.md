# vscode

VS Code settings, keybindings, and a curated extension list — same editor on personal Mac and work Windows machine.

## Files

- [`settings.json`](settings.json) — Solarized Light, vscode-icons, MesloLGS Nerd Font (editor + terminal), autosave, git smart-commit/autofetch, per-language format-on-save
- [`keybindings.json`](keybindings.json) — custom terminal/file-tree/navigation keybindings
- [`extensions.txt`](extensions.txt) — curated extension ids, grouped by purpose (DevOps, Remote/WSL, Python, Java, Go, Markdown, AI, utilities)

## Run — macOS

```sh
./install.py install vscode
```

Symlinks settings + keybindings into `~/Library/Application Support/Code/User` and installs missing extensions.

## Run — work Windows machine

VS Code runs on the Windows host (WSL connects via the Remote-WSL extension), so apply settings from **Git Bash**, not WSL:

1. Install [VS Code](https://code.visualstudio.com/) and [Git for Windows](https://gitforwindows.org/) (includes Git Bash).
2. Make sure `code` works in Git Bash (installed by default; otherwise Cmd Palette → *Shell Command: Install 'code' command in PATH*).
3. In Git Bash:
   ```sh
   git clone https://github.com/<you>/.dotfiles.git ~/dotfiles
   cd ~/dotfiles && ./install.py install vscode
   ```

On Windows the installer **copies** (with dated backup) instead of symlinking — symlinks there need admin rights. Re-run after pulling changes.

## Requirements / notes

- `code` CLI on PATH (installer skips extensions with instructions if missing).
- The editor font falls back Menlo/Consolas until a MesloLGS Nerd Font is installed ([`iterm2/`](../iterm2/README.md) or [`terminal-macos/`](../terminal-macos/README.md) install it on macOS; on Windows install manually — see root README).
- Alternative: VS Code's built-in **Settings Sync** (sign in with GitHub) syncs the same things automatically — use it if your work machine allows account sign-in; this folder remains the versioned source of truth.
