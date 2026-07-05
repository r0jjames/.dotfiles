# Shared .zshrc prereq design

## Purpose
Replace the fragile per-script sed-patching of `~/.zshrc` (root cause of the plugins-array corruption bug fixed in `setup-terminal.sh`/`setup-iterm2.sh`) with one repo-owned `.zshrc` template and one prereq script that `setup-terminal.sh`, `setup-iterm2.sh`, and `setup-wezterm.sh` all call automatically. Single source of truth, no sed, no per-script drift.

## Files
```
setup-scripts/
  setup-zsh.sh          # new prereq script
  zsh/
    .zshrc              # repo-owned template, copied wholesale (no sed)
  setup-terminal.sh     # slimmed: calls setup-zsh.sh first, keeps only Terminal.app-specific steps
  setup-iterm2.sh       # slimmed: calls setup-zsh.sh first, keeps only iTerm2-specific steps
  setup-wezterm.sh      # gains a call to setup-zsh.sh first (new capability)
```

`setup-scripts/setup-starship.sh` is untouched — it manages a separate, non-oh-my-zsh prompt stack (raw `starship` binary + manually-sourced zsh plugins) that isn't currently active in `~/.zshrc` and isn't one of the three consumers named for this prereq.

## setup-zsh.sh behavior

1. Install Homebrew if missing (same guard as existing scripts).
2. Install CLI tools if missing: bat, eza, fzf, zoxide, ripgrep, fd, htop.
3. Install oh-my-zsh if missing (unattended installer).
4. Clone powerlevel10k theme if missing.
5. Clone zsh-autosuggestions and zsh-syntax-highlighting if missing.
6. One-time migration: if `~/.zshrc` contains the line `export PATH="$HOME/.local/bin:$PATH"` and `~/.zshrc.local` does not exist yet, create `~/.zshrc.local` containing that line.
7. Diff the repo template (`setup-scripts/zsh/.zshrc`) against the live `~/.zshrc`. If they differ (or live file doesn't exist): back up the live file to `~/.zshrc.bak-$(date +%Y-%m-%d)` (only if not already backed up today, same guard as current scripts), then `cp` the template over `~/.zshrc`. If identical: skip silently — no backup noise on repeat runs.
8. No `sed` anywhere in this script.

## Template: setup-scripts/zsh/.zshrc

Based on the current live (already-repaired) `~/.zshrc`, with:
- Alias block reconciled to the fuller set already intended by the scripts' old heredocs: `k`, `kctx`, `kns`, `d`, `dc`, `tf`, `ll`, `ls`, `cat`, `..`, `...` (current live file was missing several of these due to drift from an old script version).
- The stray `export PATH="$HOME/.local/bin:$PATH"` line removed (migrated to `.zshrc.local` by setup-zsh.sh step 6, not present in the repo template).
- A trailing guarded local-override line:
  ```bash
  [[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
  ```
- All existing content preserved as-is: p10k instant-prompt block, oh-my-zsh path/theme/plugins, `source $ZSH/oh-my-zsh.sh`, DevOps aliases, fzf/zoxide tool integration, FZF_DEFAULT_COMMAND exports, p10k config source, iTerm2 Shell Integration guard.

## Caller script changes

Each of `setup-terminal.sh`, `setup-iterm2.sh`, `setup-wezterm.sh` gets one new line near the top, before any other logic:
```bash
"$(dirname "$0")/setup-zsh.sh"
```
(Uses `dirname "$0"` so it works regardless of the caller's current working directory.)

`setup-terminal.sh` and `setup-iterm2.sh` then have their oh-my-zsh install, powerlevel10k clone, zsh-plugin clones, `.zshrc` backup, and `.zshrc` theme/plugins/alias sed/heredoc sections deleted — that's now setup-zsh.sh's job. They keep: Homebrew check, their own cask/font installs, and (for `setup-iterm2.sh`) the iTerm2 Shell Integration curl install + dynamic profile copy + default-bookmark-guid `defaults write`.

`setup-wezterm.sh` keeps its existing cask/font install and wezterm.lua/events.lua copy, and gains a working oh-my-zsh/p10k/plugins/aliases shell for free via the new prereq call — this is new behavior for that script (previously it did nothing shell-related).

## Idempotency / testing
- `bash -n` on all four modified/created scripts.
- `zsh -n` on `setup-scripts/zsh/.zshrc` to confirm it parses.
- Run `setup-zsh.sh` twice in a row against a copy of the live `.zshrc`: second run must not create a new backup file and must leave the file unchanged (diff-based skip works).

## Out of scope
- `setup-starship.sh` — untouched, separate prompt stack, not a consumer of this prereq.
- No changes to the Ubuntu iTerm2 color theme, font, or dynamic profile work already done.
