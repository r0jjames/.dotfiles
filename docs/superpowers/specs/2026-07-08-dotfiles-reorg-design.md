# Dotfiles Reorganization: Cross-Platform (macOS + WSL Ubuntu) Design

**Date:** 2026-07-08
**Status:** Approved

## Goal

Make this repo the single source of truth for setting up a new machine:

- **Primary:** any new MacBook — one command, full environment.
- **Secondary:** work Windows machine — full shell environment inside WSL Ubuntu; VS Code settings applied on the Windows side via Git Bash.

Every install step is idempotent: re-running any script skips what is already installed or linked.

## Decisions

| Decision | Choice |
|---|---|
| Windows target | WSL Ubuntu only (Git Bash used solely for the VS Code settings script) |
| Package manager | Homebrew on both macOS and Linux (exception: `zsh` itself via `apt` on Ubuntu) |
| Layout | Per-tool folders, each self-contained: `setup.sh` + config + `README.md` |
| Prompt | Starship (drop Oh My Zsh and Powerlevel10k) |
| Config deployment | Symlink from repo into `$HOME`, backing up real files first (`*.bak-YYYY-MM-DD`) |
| VS Code sync | Repo-managed `vscode/` folder (no dependency on Settings Sync account sign-in) |

## Target structure

```
.dotfiles/
├── README.md            # overview + quick start (macOS, WSL Ubuntu)
├── install.sh           # orchestrator: ./install.sh [tool...] — default: all
├── lib/
│   └── common.sh        # shared helpers (sourced by every setup.sh)
├── zsh/
│   ├── setup.sh
│   ├── .zshrc           # rewritten: starship, no omz/p10k
│   └── README.md
├── starship/
│   ├── setup.sh
│   ├── starship.toml
│   └── README.md
├── nvim/
│   ├── setup.sh
│   ├── README.md
│   └── config/          # init.lua, lua/, README.md (linked as ~/.config/nvim)
├── wezterm/
│   ├── setup.sh
│   ├── wezterm.lua
│   ├── events.lua
│   └── README.md
├── vscode/
│   ├── setup.sh
│   ├── settings.json
│   ├── keybindings.json
│   ├── extensions.txt
│   └── README.md
├── terminal-macos/      # mac-only: Terminal.app themes + font
│   ├── setup.sh
│   └── README.md
├── iterm2/              # mac-only
│   ├── setup.sh
│   ├── com.dotfiles.json
│   └── README.md
├── docs/                # existing specs/plans (+ spec moved from setup-scripts/docs)
├── .claude/             # moved from setup-scripts/.claude
└── archived/            # old files, plus retired setup-scripts/*.sh
```

## lib/common.sh

- `detect_os` — sets `DOTFILES_OS` to `macos` or `linux` (via `uname -s`).
- `is_wsl` — true when `/proc/version` contains `microsoft`.
- `ensure_brew` — installs Homebrew if `brew` is missing. On Linux, evals
  `/home/linuxbrew/.linuxbrew/bin/brew shellenv` so the rest of the script can
  use `brew` immediately after install.
- `brew_install <pkg> [flags...]` — `brew list <pkg>` check first; skips when
  present (promoted from setup-nvim.sh).
- `link_file <repo-path> <target>` — no-op when target is already a symlink to
  the repo path; backs up an existing real file/dir to `<target>.bak-YYYY-MM-DD`
  before linking; creates parent dirs.
- Log helpers: `info`, `ok`, `skip`, `warn`.

## install.sh

- `./install.sh` runs all tools in order: zsh → starship → nvim → wezterm →
  vscode → terminal-macos → iterm2.
- `./install.sh nvim zsh` runs a subset.
- Sources `lib/common.sh` once; each tool's `setup.sh` also works standalone
  (sources common.sh itself, resolves paths from its own location).
- On Linux, mac-only tools (terminal-macos, iterm2) are skipped with a message;
  wezterm skips the app install but explains the Windows-side setup.

## Per-tool behavior

### zsh
- Ubuntu: `sudo apt-get install -y zsh` + `chsh -s $(which zsh)` if not the
  login shell (brew-installed zsh as login shell is fragile; this is the single
  apt exception). macOS: zsh is the default already.
- CLI tools via brew: bat, eza, fzf, zoxide, ripgrep, fd, htop.
- zsh-autosuggestions + zsh-syntax-highlighting via brew (no git clones,
  no Oh My Zsh).
- `link_file zsh/.zshrc ~/.zshrc`.
- New `.zshrc` contents, in order: brew shellenv (Linux guard), DevOps aliases
  (kept from the current template), fzf + zoxide init, fzf/fd defaults,
  plugin sourcing via `$(brew --prefix)`, `eval "$(starship init zsh)"`,
  iTerm2 shell integration (guarded, mac-only file), `~/.zshrc.local`
  sourcing for machine-local overrides.
- Fixes two existing bugs: starship/p10k prompt conflict, and
  setup-starship.sh appending init lines that setup-zsh.sh's template sync
  then clobbered. All init lines now live in the template; nothing appends
  to `~/.zshrc` anymore.

### starship
- `brew_install starship`; `link_file starship/starship.toml ~/.config/starship.toml`.
- No `~/.zshrc` modification (init line is in the zsh template).

### nvim
- Configs move to `nvim/config/`; `link_file nvim/config ~/.config/nvim`
  (directory symlink — replaces the copy/rm -rf sync, removed modules can't
  linger by construction).
- Existing brew installs kept, now via common.sh `brew_install`: neovim,
  kubectl, helm, ansible, uv, hadolint, terraform; fontconfig +
  JetBrainsMono Nerd Font on macOS. On WSL the font check is skipped with a
  note (fonts render from the Windows-side terminal).
- Headless `Lazy! sync` + `MasonToolsInstall` kept as-is.

### wezterm
- macOS: cask install (wezterm + fonts), `link_file` the config dir files into
  `~/.config/wezterm/`, restart logic kept.
- WSL: skip install; README documents installing WezTerm on Windows and
  pointing it at the repo config
  (e.g. `\\wsl$\Ubuntu\home\<user>\Dev\.dotfiles\wezterm\wezterm.lua`).

### vscode
- Baseline: current live settings (Solarized Light, vscode-icons,
  fontSize 15, git smart commit/autofetch) plus curated cross-platform
  additions: MesloLGS Nerd Font for editor + integrated terminal,
  format-on-save, cross-platform-safe values only (no absolute paths).
- `keybindings.json`: current live file, captured as-is.
- `extensions.txt`: curated keep-list (user approves during implementation;
  full 62-extension dump categorized, junk/one-offs dropped).
- `setup.sh` targets:
  - macOS: `~/Library/Application Support/Code/User` — symlink.
  - Windows Git Bash: `$APPDATA/Code/User` — **copy** with backup (symlinks
    need admin/developer mode on Windows).
  - WSL: prints a note to run from Git Bash on the Windows side instead.
- Extensions: loop `extensions.txt`; skip those already in
  `code --list-extensions`; skip cleanly with instructions if `code` CLI is
  missing.
- README notes built-in Settings Sync as an alternative when account sign-in
  is allowed.

### terminal-macos (was setup-terminal.sh)
- mac-only; exits 0 with a skip message on Linux.
- Keeps: theme download/import, font defaults. Drops: duplicate brew/CLI/zsh
  installs (zsh/setup.sh owns those; install.sh ordering guarantees they ran).

### iterm2
- mac-only; exits 0 with a skip message on Linux.
- Keeps: cask install, shell integration download, dynamic profile copy,
  default profile GUID. Drops duplicate font/CLI/zsh installs (same reason).

## Prerequisites

- **macOS:** none (scripts bootstrap Homebrew; Xcode CLT prompt may appear).
- **WSL Ubuntu:** `sudo apt-get update && sudo apt-get install -y build-essential curl file git zsh`
  before running `install.sh` (Homebrew-on-Linux requirements).
- **Windows host (manual, documented in README):** Nerd Font install +
  Windows Terminal font setting; WezTerm install (optional); VS Code +
  `code` CLI on PATH for vscode/setup.sh via Git Bash.

## Migration / cleanup

- `git mv` configs from `setup-scripts/` into per-tool folders.
- Old `setup-scripts/*.sh` move to `archived/setup-scripts/` (reference only).
- `setup-scripts/docs/superpowers/specs/2026-07-07-devops-nvim-design.md`
  moves to `docs/superpowers/specs/`.
- `setup-scripts/.claude/settings.local.json` moves to `.claude/` at repo root.
- `archived/` otherwise untouched.

## Verification

1. `bash -n` every script (syntax).
2. Run `./install.sh` on this Mac; then run it a second time — second run must
   be all skip/ok messages, no reinstalls, no re-backups.
3. Open a new shell: starship prompt renders, aliases work, fzf/zoxide work.
4. `nvim --headless +qa` exits clean with linked config.
5. VS Code: settings/keybindings symlinked, extensions loop reports skips.
6. WSL path: best-effort syntax/logic review (Ubuntu docker approximates it);
   real validation on the work machine later.
