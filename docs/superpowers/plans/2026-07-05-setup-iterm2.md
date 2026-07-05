# setup-iterm2.sh Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a standalone `setup-scripts/setup-iterm2.sh` that installs iTerm2, the same shell stack as `setup-terminal.sh` (Homebrew tools, oh-my-zsh, powerlevel10k, plugins, aliases), iTerm2 Shell Integration, and a dynamic-profile color theme matching the user's current Ubuntu-purple Terminal.app theme.

**Architecture:** Single bash script following the exact idempotent-check-then-install pattern already used by every script in `setup-scripts/`, plus one static JSON asset (`setup-scripts/iterm2/com.dotfiles.json`) that iTerm2 auto-loads as a Dynamic Profile. No runtime color conversion — the JSON is generated once now, from colors already extracted out of `~/Documents/macos-terminal-themes-master/themes/Ubuntu.terminal`.

**Tech Stack:** bash, Homebrew, oh-my-zsh, iTerm2 Dynamic Profiles (JSON), `defaults write`.

## Global Constraints

- Font: MesloLGS Nerd Font Mono, PostScript name `MesloLGSNFM-Regular`, size 13 (verified via `system_profiler SPFontsDataType` against the installed `font-meslo-lg-nerd-font` cask — do not use the plain "MesloLGS NF" name, it does not match this cask's actual PostScript name).
- Fixed dynamic-profile GUID: `557036D3-EF41-4D30-A395-3F301A17D49B` (used both inside the JSON and in the `defaults write "Default Bookmark Guid"` call — must match exactly in both places).
- Script must be idempotent: every install/append step guarded by an existence/grep check, matching the style already used in `setup-scripts/setup-terminal.sh` and `setup-scripts/setup-starship.sh`.
- Do not modify `setup-scripts/setup-terminal.sh` or any other existing script.
- Script must not actually be executed against the live system as part of this plan — only syntax/lint-checked. Running it (installing casks, editing the real `~/.zshrc`, changing iTerm2 defaults) is a separate, explicitly-confirmed step after the plan is done.

---

### Task 1: iTerm2 dynamic profile JSON

**Files:**
- Create: `setup-scripts/iterm2/com.dotfiles.json`

**Interfaces:**
- Produces: a file with top-level shape `{"Profiles": [ {...} ]}`, where the single profile object has `"Guid": "557036D3-EF41-4D30-A395-3F301A17D49B"` — Task 5 (`defaults write`) depends on this exact string matching.

- [ ] **Step 1: Write the JSON file**

```json
{
  "Profiles": [
    {
      "Guid": "557036D3-EF41-4D30-A395-3F301A17D49B",
      "Name": "dotfiles-ubuntu",
      "Dynamic Profile Parent Name": "Default",
      "Normal Font": "MesloLGSNFM-Regular 13",
      "Non Ascii Font": "MesloLGSNFM-Regular 13",
      "Use Non-ASCII Font": false,
      "Use Bold Font": true,
      "Use Bright Bold": true,
      "Use Italic Font": true,
      "Background Color": { "Red Component": 0.1882352978, "Green Component": 0.03921568766, "Blue Component": 0.1411764771, "Alpha Component": 1 },
      "Foreground Color": { "Red Component": 0.9333333373, "Green Component": 0.9333333373, "Blue Component": 0.9254902005, "Alpha Component": 1 },
      "Bold Color": { "Red Component": 0.9333333373, "Green Component": 0.9333333373, "Blue Component": 0.9254902005, "Alpha Component": 1 },
      "Cursor Color": { "Red Component": 0.7333333492, "Green Component": 0.7333333492, "Blue Component": 0.7333333492, "Alpha Component": 1 },
      "Cursor Text Color": { "Red Component": 0.1882352978, "Green Component": 0.03921568766, "Blue Component": 0.1411764771, "Alpha Component": 1 },
      "Selection Color": { "Red Component": 0.709800005, "Green Component": 0.8353000283, "Blue Component": 1, "Alpha Component": 1 },
      "Selected Text Color": { "Red Component": 0.9333333373, "Green Component": 0.9333333373, "Blue Component": 0.9254902005, "Alpha Component": 1 },
      "Ansi 0 Color": { "Red Component": 0.180392161, "Green Component": 0.2039215714, "Blue Component": 0.2117647082, "Alpha Component": 1 },
      "Ansi 1 Color": { "Red Component": 0.8000000119, "Green Component": 0, "Blue Component": 0, "Alpha Component": 1 },
      "Ansi 2 Color": { "Red Component": 0.3058823645, "Green Component": 0.6039215922, "Blue Component": 0.02352941222, "Alpha Component": 1 },
      "Ansi 3 Color": { "Red Component": 0.7686274648, "Green Component": 0.6274510026, "Blue Component": 0, "Alpha Component": 1 },
      "Ansi 4 Color": { "Red Component": 0.2039215714, "Green Component": 0.3960784376, "Blue Component": 0.6431372762, "Alpha Component": 1 },
      "Ansi 5 Color": { "Red Component": 0.4588235319, "Green Component": 0.3137255013, "Blue Component": 0.4823529422, "Alpha Component": 1 },
      "Ansi 6 Color": { "Red Component": 0.02352941222, "Green Component": 0.5960784554, "Blue Component": 0.6039215922, "Alpha Component": 1 },
      "Ansi 7 Color": { "Red Component": 0.8274509907, "Green Component": 0.8431372643, "Blue Component": 0.8117647171, "Alpha Component": 1 },
      "Ansi 8 Color": { "Red Component": 0.3333333433, "Green Component": 0.3411764801, "Blue Component": 0.3254902065, "Alpha Component": 1 },
      "Ansi 9 Color": { "Red Component": 0.9372549057, "Green Component": 0.160784319, "Blue Component": 0.160784319, "Alpha Component": 1 },
      "Ansi 10 Color": { "Red Component": 0.5411764979, "Green Component": 0.8862745166, "Blue Component": 0.2039215714, "Alpha Component": 1 },
      "Ansi 11 Color": { "Red Component": 0.9882352948, "Green Component": 0.9137254953, "Blue Component": 0.3098039329, "Alpha Component": 1 },
      "Ansi 12 Color": { "Red Component": 0.4470588267, "Green Component": 0.6235294342, "Blue Component": 0.8117647171, "Alpha Component": 1 },
      "Ansi 13 Color": { "Red Component": 0.6784313917, "Green Component": 0.4980392158, "Blue Component": 0.6588235497, "Alpha Component": 1 },
      "Ansi 14 Color": { "Red Component": 0.2039215714, "Green Component": 0.8862745166, "Blue Component": 0.8862745166, "Alpha Component": 1 },
      "Ansi 15 Color": { "Red Component": 0.9333333373, "Green Component": 0.9333333373, "Blue Component": 0.9254902005, "Alpha Component": 1 }
    }
  ]
}
```

- [ ] **Step 2: Validate JSON syntax**

Run: `python3 -m json.tool setup-scripts/iterm2/com.dotfiles.json > /dev/null && echo VALID`
Expected: `VALID`

- [ ] **Step 3: Validate required keys present**

Run:
```bash
python3 -c "
import json
p = json.load(open('setup-scripts/iterm2/com.dotfiles.json'))
prof = p['Profiles'][0]
assert prof['Guid'] == '557036D3-EF41-4D30-A395-3F301A17D49B'
assert prof['Normal Font'] == 'MesloLGSNFM-Regular 13'
for i in range(16):
    assert f'Ansi {i} Color' in prof
print('OK')
"
```
Expected: `OK`

- [ ] **Step 4: Commit**

```bash
git add setup-scripts/iterm2/com.dotfiles.json
git commit -m "Add iTerm2 dynamic profile matching Ubuntu terminal theme"
```

---

### Task 2: setup-iterm2.sh — Homebrew, iTerm2, font, CLI tools

**Files:**
- Create: `setup-scripts/setup-iterm2.sh`

**Interfaces:**
- Produces: executable script file, extended by Tasks 3–5. Uses `#!/bin/bash` + `set -e` at top like other scripts in this repo do NOT use `set -e` (check: `setup-terminal.sh` has no `set -e`, but `setup-wezterm.sh`/`setup-nvim.sh` do). Match `setup-terminal.sh` style since this script is its direct sibling — no `set -e`, plain `#!/bin/bash`.

- [ ] **Step 1: Create the file with shebang and Homebrew/font/tools sections**

```bash
#!/bin/bash

# Install Homebrew if not already installed
if ! command -v brew &> /dev/null; then
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install iTerm2 if not already installed
if ! brew list --cask iterm2 &> /dev/null; then
  brew install --cask iterm2
fi

# Install font and CLI tools if not already installed
if ! brew list --cask | grep -q "font-meslo-lg-nerd-font"; then
  brew install --cask font-meslo-lg-nerd-font
fi
for tool in bat eza fzf zoxide ripgrep fd htop; do
  if ! command -v $tool &> /dev/null; then
    brew install $tool
  fi
done
```

- [ ] **Step 2: Make executable and syntax-check**

Run: `chmod +x setup-scripts/setup-iterm2.sh && bash -n setup-scripts/setup-iterm2.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`

- [ ] **Step 3: Commit**

```bash
git add setup-scripts/setup-iterm2.sh
git commit -m "Add setup-iterm2.sh: Homebrew, iTerm2 cask, font, CLI tools"
```

---

### Task 3: oh-my-zsh, powerlevel10k, zsh plugins

**Files:**
- Modify: `setup-scripts/setup-iterm2.sh` (append after Task 2's content)

**Interfaces:**
- Consumes: nothing new from Task 2 besides file continuation.
- Produces: script now installs oh-my-zsh + p10k + 2 plugins, for Task 4 to build on.

- [ ] **Step 1: Append oh-my-zsh / p10k / plugins sections**

```bash

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
```

- [ ] **Step 2: Syntax-check**

Run: `bash -n setup-scripts/setup-iterm2.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`

- [ ] **Step 3: Commit**

```bash
git add setup-scripts/setup-iterm2.sh
git commit -m "Add oh-my-zsh, powerlevel10k, plugin installs to setup-iterm2.sh"
```

---

### Task 4: .zshrc backup, theme, plugins list, aliases

**Files:**
- Modify: `setup-scripts/setup-iterm2.sh` (append after Task 3's content)

**Interfaces:**
- Consumes: nothing new.
- Produces: script now fully replicates `setup-terminal.sh`'s `.zshrc` mutation block, for Task 5 to add iTerm2-specific pieces after.

- [ ] **Step 1: Append .zshrc backup + theme + plugins + aliases sections**

```bash

# Backup existing .zshrc if it exists and hasn't been backed up today
if [ -f ~/.zshrc ] && [ ! -f ~/.zshrc.bak-$(date +%Y-%m-%d) ]; then
  cp ~/.zshrc ~/.zshrc.bak-$(date +%Y-%m-%d)
fi

# Update .zshrc theme if not already set
if ! grep -q "ZSH_THEME=\"powerlevel10k/powerlevel10k\"" ~/.zshrc; then
  sed -i '' 's/^ZSH_THEME=.*/ZSH_THEME="powerlevel10k\/powerlevel10k"/' ~/.zshrc
fi

# Update .zshrc plugins if not already set
if ! grep -q "plugins=(\n  git\n  docker" ~/.zshrc; then
  sed -i '' 's/^plugins=.*/plugins=(\n  git\n  docker\n  docker-compose\n  kubectl\n  helm\n  terraform\n  ansible\n  aws\n  ssh-agent\n  zsh-autosuggestions\n  zsh-syntax-highlighting\n)/' ~/.zshrc
fi

# Append aliases and tool integrations to .zshrc if not already present
if ! grep -q "# ---- DevOps aliases ----" ~/.zshrc; then
  cat >> ~/.zshrc << 'EOF'

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
EOF
fi
```

- [ ] **Step 2: Syntax-check**

Run: `bash -n setup-scripts/setup-iterm2.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`

- [ ] **Step 3: Commit**

```bash
git add setup-scripts/setup-iterm2.sh
git commit -m "Add .zshrc theme/plugins/aliases block to setup-iterm2.sh"
```

---

### Task 5: iTerm2 Shell Integration, dynamic profile install, default profile, completion message

**Files:**
- Modify: `setup-scripts/setup-iterm2.sh` (append after Task 4's content)

**Interfaces:**
- Consumes: `setup-scripts/iterm2/com.dotfiles.json` from Task 1 (copied by path relative to script's working directory, same convention `setup-wezterm.sh` uses for `./wezterm/wezterm.lua`).
- Produces: complete, runnable script.

- [ ] **Step 1: Append Shell Integration install**

```bash

# Install iTerm2 Shell Integration if not already installed
if [ ! -f ~/.iterm2_shell_integration.zsh ]; then
  curl -fsSL https://iterm2.com/shell_integration/zsh -o ~/.iterm2_shell_integration.zsh
fi
if ! grep -q "iterm2_shell_integration.zsh" ~/.zshrc; then
  cat >> ~/.zshrc << 'EOF'

# ---- iTerm2 Shell Integration ----
test -e "${HOME}/.iterm2_shell_integration.zsh" && source "${HOME}/.iterm2_shell_integration.zsh"
EOF
fi
```

- [ ] **Step 2: Append dynamic profile install + default profile + completion message**

```bash

# Install iTerm2 dynamic profile (color theme + font) if not already installed
mkdir -p ~/Library/Application\ Support/iTerm2/DynamicProfiles
cp ./iterm2/com.dotfiles.json ~/Library/Application\ Support/iTerm2/DynamicProfiles/com.dotfiles.json

# Set the dotfiles profile as the default for new windows/tabs
defaults write com.googlecode.iterm2 "Default Bookmark Guid" -string "557036D3-EF41-4D30-A395-3F301A17D49B"

echo "Setup complete. Restart iTerm2 (Cmd+Q then relaunch) for the theme and default profile to take effect."
```

- [ ] **Step 3: Full syntax-check**

Run: `bash -n setup-scripts/setup-iterm2.sh && echo SYNTAX_OK`
Expected: `SYNTAX_OK`

- [ ] **Step 4: Shellcheck (if available)**

Run: `command -v shellcheck &> /dev/null && shellcheck setup-scripts/setup-iterm2.sh || echo "shellcheck not installed, skipping"`
Expected: no errors (warnings about unquoted `$tool`/globbing are pre-existing style in `setup-terminal.sh` — acceptable, don't fix beyond what this task touches).

- [ ] **Step 5: Confirm script references Task 1's file correctly**

Run: `grep -n "com.dotfiles.json" setup-scripts/setup-iterm2.sh`
Expected: two lines — the `cp ./iterm2/com.dotfiles.json ...` line and nothing else stale.

- [ ] **Step 6: Commit**

```bash
git add setup-scripts/setup-iterm2.sh
git commit -m "Add iTerm2 shell integration and dynamic profile install to setup-iterm2.sh"
```

---

## Post-Plan: Running the script

This plan only builds and statically verifies the script — it does not execute it, since running it installs real software, edits the real `~/.zshrc`, and writes a real macOS default. After all 5 tasks are committed, run it yourself from the repo root:

```bash
cd setup-scripts && ./setup-iterm2.sh
```
