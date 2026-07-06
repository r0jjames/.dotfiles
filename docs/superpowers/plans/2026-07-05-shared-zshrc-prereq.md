# Shared .zshrc Prereq Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Extract shell setup (oh-my-zsh, p10k, plugins, CLI tools, `.zshrc` content) out of `setup-terminal.sh`/`setup-iterm2.sh` and into one new `setup-zsh.sh` prereq script, called automatically by `setup-terminal.sh`, `setup-iterm2.sh`, and `setup-wezterm.sh`, replacing the fragile sed-based `.zshrc` patching with a repo-owned template that's copied in wholesale.

**Architecture:** One new script (`setup-scripts/setup-zsh.sh`) owns all shell-stack installs and a diff-then-copy of a repo-owned template (`setup-scripts/zsh/.zshrc`) over the live `~/.zshrc`. The three terminal-emulator scripts each gain a one-line call to this prereq at the top and lose their now-redundant oh-my-zsh/p10k/plugin/zshrc-mutation sections.

**Tech Stack:** bash, Homebrew, oh-my-zsh, diff/cp (no sed).

## Global Constraints

- No `sed` anywhere in `setup-zsh.sh` — diff-then-`cp` only.
- Idempotent: identical template vs. live file must skip (no backup, no copy) on repeat runs.
- Template alias block uses the fuller set: `k`, `kctx`, `kns`, `d`, `dc`, `tf`, `ll`, `ls`, `cat`, `..`, `...`.
- `setup-scripts/setup-starship.sh` is not modified.
- `setup-zsh.sh` must be callable via `"$(dirname "$0")/setup-zsh.sh"` regardless of caller's cwd.
- Testing in this plan must not mutate the real `~/.zshrc` — use a scratch `HOME` for prereq-script tests.

---

### Task 1: Repo-owned `.zshrc` template

**Files:**
- Create: `setup-scripts/zsh/.zshrc`

**Interfaces:**
- Produces: a complete, valid zsh config file. Task 2's `setup-zsh.sh` copies this file verbatim to `~/.zshrc`. Must end with the exact line `[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local` — Task 2's migration step depends on `~/.zshrc.local` being the filename referenced here.

- [ ] **Step 1: Write the template file**

```bash
# Enable Powerlevel10k instant prompt. Should stay close to the top of ~/.zshrc.
# Initialization code that may require console input (password prompts, [y/n]
# confirmations, etc.) must go above this block; everything else may go below.
if [[ -r "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh" ]]; then
  source "${XDG_CACHE_HOME:-$HOME/.cache}/p10k-instant-prompt-${(%):-%n}.zsh"
fi

# Path to your Oh My Zsh installation.
export ZSH="$HOME/.oh-my-zsh"

# See https://github.com/ohmyzsh/ohmyzsh/wiki/Themes
ZSH_THEME="powerlevel10k/powerlevel10k"

# Which plugins would you like to load?
# Standard plugins can be found in $ZSH/plugins/
# Custom plugins may be added to $ZSH_CUSTOM/plugins/
plugins=(
  git
  docker
  docker-compose
  kubectl
  helm
  terraform
  ansible
  aws
  ssh-agent
  zsh-autosuggestions
  zsh-syntax-highlighting
)
source $ZSH/oh-my-zsh.sh

# User configuration

# ---- DevOps aliases ----
alias k='kubectl'
alias kctx='kubectl config use-context'
alias kns='kubectl config set-context --current --namespace'
alias d='docker'
alias dc='docker compose'
alias tf='terraform'
alias ll='eza -lah --icons --git'
alias ls='eza --icons'
alias cat='bat --paging=never'
alias ..='cd ..'
alias ...='cd ../..'

# ---- Tool integrations ----
eval "$(fzf --zsh)"
eval "$(zoxide init zsh)"

# ---- fzf better defaults (use fd instead of find) ----
export FZF_DEFAULT_COMMAND='fd --type f --hidden --follow --exclude .git'
export FZF_CTRL_T_COMMAND="$FZF_DEFAULT_COMMAND"

# To customize prompt, run `p10k configure` or edit ~/.p10k.zsh.
[[ ! -f ~/.p10k.zsh ]] || source ~/.p10k.zsh

# ---- iTerm2 Shell Integration ----
test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"

# ---- Machine-local overrides (not managed by this repo) ----
[[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
```

- [ ] **Step 2: Verify it parses as valid zsh**

Run: `zsh -n setup-scripts/zsh/.zshrc && echo PARSE_OK`
Expected: `PARSE_OK`

- [ ] **Step 3: Commit**

```bash
git add setup-scripts/zsh/.zshrc
git commit -m "Add repo-owned .zshrc template"
```

---

### Task 2: `setup-zsh.sh` prereq script

**Files:**
- Create: `setup-scripts/setup-zsh.sh`

**Interfaces:**
- Consumes: `setup-scripts/zsh/.zshrc` from Task 1 (referenced via `"$(dirname "$0")/zsh/.zshrc"` so it works regardless of caller's cwd).
- Produces: an executable script other scripts call as `"$(dirname "$0")/setup-zsh.sh"`. Idempotent — safe to call from Task 3/4/5's scripts every run.

- [ ] **Step 1: Write the script**

```bash
#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install CLI tools if not already installed
for tool in bat eza fzf zoxide ripgrep fd htop; do
  if ! command -v $tool &> /dev/null; then
    brew install $tool
  fi
done

# Install Oh My Zsh if not already installed
if [ ! -d ~/.oh-my-zsh ]; then
  sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
fi

# Install Powerlevel10k theme if not already installed
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k ]; then
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k
fi

# Install zsh plugins if not already installed
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions ]; then
  git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
fi
if [ ! -d ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting ]; then
  git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting
fi

# One-time migration: pull the stray .local/bin PATH export out of ~/.zshrc
# into ~/.zshrc.local, if present and not already migrated.
if [ -f ~/.zshrc ] && [ ! -f ~/.zshrc.local ] && grep -qF 'export PATH="$HOME/.local/bin:$PATH"' ~/.zshrc; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' > ~/.zshrc.local
fi

# Sync ~/.zshrc with the repo template if it differs
if [ ! -f ~/.zshrc ] || ! diff -q "$SCRIPT_DIR/zsh/.zshrc" ~/.zshrc &> /dev/null; then
  if [ -f ~/.zshrc ] && [ ! -f ~/.zshrc.bak-$(date +%Y-%m-%d) ]; then
    cp ~/.zshrc ~/.zshrc.bak-$(date +%Y-%m-%d)
  fi
  cp "$SCRIPT_DIR/zsh/.zshrc" ~/.zshrc
fi
```

- [ ] **Step 2: Make executable and syntax-check**

Run: `chmod +x setup-scripts/setup-zsh.sh && bash -n setup-scripts/setup-zsh.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`

- [ ] **Step 3: Test idempotency against a scratch HOME (does not touch real ~/.zshrc)**

```bash
SCRATCH=$(mktemp -d)
cp setup-scripts/zsh/.zshrc "$SCRATCH/.zshrc"
# First run: template already identical to "live" file -> should skip, no backup created
HOME="$SCRATCH" bash -c '
  SCRIPT_DIR="'"$(pwd)"'/setup-scripts"
  if [ ! -f ~/.zshrc ] || ! diff -q "$SCRIPT_DIR/zsh/.zshrc" ~/.zshrc &> /dev/null; then
    echo WOULD_COPY
  else
    echo SKIPPED
  fi
'
ls "$SCRATCH"/.zshrc.bak-* 2>/dev/null && echo "FAIL: backup created" || echo "PASS: no backup on identical file"
rm -rf "$SCRATCH"
```
Expected: `SKIPPED` then `PASS: no backup on identical file`

- [ ] **Step 4: Test that a differing file triggers backup + copy**

```bash
SCRATCH=$(mktemp -d)
echo "# old custom zshrc" > "$SCRATCH/.zshrc"
SCRIPT_DIR="$(pwd)/setup-scripts"
HOME="$SCRATCH" bash -c '
  if [ ! -f ~/.zshrc ] || ! diff -q "'"$SCRIPT_DIR"'/zsh/.zshrc" ~/.zshrc &> /dev/null; then
    if [ -f ~/.zshrc ] && [ ! -f ~/.zshrc.bak-$(date +%Y-%m-%d) ]; then
      cp ~/.zshrc ~/.zshrc.bak-$(date +%Y-%m-%d)
    fi
    cp "'"$SCRIPT_DIR"'/zsh/.zshrc" ~/.zshrc
  fi
'
diff -q "$SCRATCH/.zshrc" setup-scripts/zsh/.zshrc && echo "PASS: template copied in"
ls "$SCRATCH"/.zshrc.bak-* &> /dev/null && echo "PASS: backup created"
rm -rf "$SCRATCH"
```
Expected: `PASS: template copied in` then `PASS: backup created`

- [ ] **Step 5: Commit**

```bash
git add setup-scripts/setup-zsh.sh
git commit -m "Add setup-zsh.sh prereq: shell stack install + template-based .zshrc sync"
```

---

### Task 3: Slim down `setup-terminal.sh`

**Files:**
- Modify: `setup-scripts/setup-terminal.sh`

**Interfaces:**
- Consumes: `setup-scripts/setup-zsh.sh` from Task 2, called as `"$(dirname "$0")/setup-zsh.sh"`.
- Produces: a script that still fully sets up Terminal.app (font cask, terminal themes, default font/theme `defaults write`), but no longer duplicates shell-stack logic.

- [ ] **Step 1: Read current file to confirm exact block boundaries**

Run: `grep -n "^#\|^if\|^for\|^fi\|^done" setup-scripts/setup-terminal.sh`
Expected: a numbered list of section boundaries — use it to find the exact lines for Step 2's removal (oh-my-zsh through the aliases/tool-integrations heredoc, i.e. everything between the CLI-tools loop and the "Download and load Terminal themes" section).

- [ ] **Step 2: Replace the whole shell-stack section with a single prereq call**

Remove everything from `# Install Oh My Zsh if not already installed` through the end of the aliases/tool-integrations heredoc block (the `EOF` line just before `# Download and load Terminal themes`), and insert this single line in its place, immediately after the CLI-tools `for tool in ...; done` loop:

```bash
# Shell stack (oh-my-zsh, p10k, plugins, .zshrc) is owned by setup-zsh.sh
"$(dirname "$0")/setup-zsh.sh"
```

The resulting file's middle section (after the CLI-tools loop) should read:

```bash
for tool in bat eza fzf zoxide ripgrep fd htop; do
  if ! command -v $tool &> /dev/null; then
    brew install $tool
  fi
done

# Shell stack (oh-my-zsh, p10k, plugins, .zshrc) is owned by setup-zsh.sh
"$(dirname "$0")/setup-zsh.sh"

# Download and load Terminal themes if not already downloaded
if [ ! -d ~/Downloads/macos-terminal-themes-master ]; then
```

- [ ] **Step 3: Syntax-check**

Run: `bash -n setup-scripts/setup-terminal.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`

- [ ] **Step 4: Confirm no leftover duplicated shell-stack logic**

Run: `grep -n "oh-my-zsh\|powerlevel10k\|ZSH_THEME\|plugins=(" setup-scripts/setup-terminal.sh`
Expected: no output (empty) — all of that now lives only in `setup-zsh.sh`/the template.

- [ ] **Step 5: Commit**

```bash
git add setup-scripts/setup-terminal.sh
git commit -m "Slim setup-terminal.sh: delegate shell stack to setup-zsh.sh"
```

---

### Task 4: Slim down `setup-iterm2.sh`

**Files:**
- Modify: `setup-scripts/setup-iterm2.sh`

**Interfaces:**
- Consumes: `setup-scripts/setup-zsh.sh` from Task 2, called as `"$(dirname "$0")/setup-zsh.sh"`.
- Produces: a script that still installs iTerm2 (app detection by path, per the earlier fix), the font cask, iTerm2 Shell Integration, and the dynamic color profile — but no longer duplicates shell-stack logic.

- [ ] **Step 1: Read current file to confirm exact block boundaries**

Run: `grep -n "^#\|^if\|^for\|^fi\|^done" setup-scripts/setup-iterm2.sh`
Expected: numbered section boundaries — find the span from `# Install Oh My Zsh if not already installed` through the end of the aliases/tool-integrations heredoc (the `EOF` just before `# Install iTerm2 Shell Integration`).

- [ ] **Step 2: Replace the whole shell-stack section with a single prereq call**

Remove everything from `# Install Oh My Zsh if not already installed` through that `EOF` line, and insert this single line in its place, immediately after the CLI-tools `for tool in ...; done` loop:

```bash
# Shell stack (oh-my-zsh, p10k, plugins, .zshrc) is owned by setup-zsh.sh
"$(dirname "$0")/setup-zsh.sh"
```

The resulting file's middle section should read:

```bash
for tool in bat eza fzf zoxide ripgrep fd htop; do
  if ! command -v $tool &> /dev/null; then
    brew install $tool
  fi
done

# Shell stack (oh-my-zsh, p10k, plugins, .zshrc) is owned by setup-zsh.sh
"$(dirname "$0")/setup-zsh.sh"

# Install iTerm2 Shell Integration if not already installed
if [ ! -f ~/.iterm2_shell_integration.zsh ]; then
```

- [ ] **Step 3: Syntax-check**

Run: `bash -n setup-scripts/setup-iterm2.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`

- [ ] **Step 4: Confirm no leftover duplicated shell-stack logic**

Run: `grep -n "oh-my-zsh\|powerlevel10k\|ZSH_THEME\|plugins=(" setup-scripts/setup-iterm2.sh`
Expected: no output (empty).

- [ ] **Step 5: Confirm iTerm2-specific pieces still intact**

Run: `grep -n "iTerm.app\|com.dotfiles.json\|Default Bookmark Guid\|iterm2_shell_integration" setup-scripts/setup-iterm2.sh`
Expected: 4 matching lines (app-path detection, dynamic profile copy, default-guid write, shell-integration install/source-append).

- [ ] **Step 6: Commit**

```bash
git add setup-scripts/setup-iterm2.sh
git commit -m "Slim setup-iterm2.sh: delegate shell stack to setup-zsh.sh"
```

---

### Task 5: Wire prereq into `setup-wezterm.sh`

**Files:**
- Modify: `setup-scripts/setup-wezterm.sh`

**Interfaces:**
- Consumes: `setup-scripts/setup-zsh.sh` from Task 2, called as `"$(dirname "$0")/setup-zsh.sh"`.
- Produces: `setup-wezterm.sh` now provisions a full shell stack in addition to its existing wezterm-specific work (this is new behavior for this script — previously it did no shell setup at all).

- [ ] **Step 1: Read current file to find insertion point**

Run: `grep -n "^#\|^if\|^fi" setup-scripts/setup-wezterm.sh`
Expected: section list — find the line number of `# Create wezterm config directory` (the first non-install step) to insert before it.

- [ ] **Step 2: Insert the prereq call**

Insert immediately before the `# Create wezterm config directory` comment line:

```bash
# Shell stack (oh-my-zsh, p10k, plugins, .zshrc) is owned by setup-zsh.sh
"$(dirname "$0")/setup-zsh.sh"

```

- [ ] **Step 3: Syntax-check**

Run: `bash -n setup-scripts/setup-wezterm.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`

- [ ] **Step 4: Confirm the call was inserted in the right place**

Run: `grep -n "setup-zsh.sh\|Create wezterm config directory" setup-scripts/setup-wezterm.sh`
Expected: two lines, `setup-zsh.sh` line number lower than `Create wezterm config directory` line number.

- [ ] **Step 5: Commit**

```bash
git add setup-scripts/setup-wezterm.sh
git commit -m "Wire setup-zsh.sh prereq into setup-wezterm.sh"
```

---

## Post-Plan: Applying to your real machine

This plan builds and statically/scratch-tests the scripts — it does not run `setup-zsh.sh` against your real `~/.zshrc`. After all 5 tasks are committed, running any of the three scripts (`setup-terminal.sh`, `setup-iterm2.sh`, or `setup-wezterm.sh`) will call `setup-zsh.sh`, which will diff the new template against your current live `~/.zshrc`. Since the template now has the fuller alias set (`k`/`kctx`/`kns`/`d`/`dc`/`tf`/`..`/`...`) that your live file is missing, they will differ — expect one backup (`~/.zshrc.bak-<today>`) and one template copy-in on first run. Restart your shell afterward.
