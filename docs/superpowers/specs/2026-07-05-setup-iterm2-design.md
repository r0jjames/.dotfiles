# setup-iterm2.sh design

## Purpose
Migrate terminal setup from macOS Terminal.app to iTerm2, replicating current stack (font, oh-my-zsh, p10k, plugins, aliases) plus Ubuntu-purple color theme, as one runnable script. Mirrors `setup-scripts/setup-terminal.sh` pattern.

## Location
```
setup-scripts/
  setup-iterm2.sh
  iterm2/
    com.dotfiles.json   # iTerm2 dynamic profile
```

## Script steps (idempotent, emoji-status echo pattern matching existing scripts)

1. Install Homebrew if missing.
2. `brew install --cask iterm2` if not installed.
3. `brew install --cask font-meslo-lg-nerd-font` if not installed.
4. Install CLI tools if missing: bat, eza, fzf, zoxide, ripgrep, fd, htop.
5. Install oh-my-zsh if missing (unattended).
6. Clone powerlevel10k theme if missing.
7. Clone zsh-autosuggestions and zsh-syntax-highlighting plugins if missing.
8. Backup `~/.zshrc` to `~/.zshrc.bak-$(date +%Y-%m-%d)` if not already backed up today.
9. Update `~/.zshrc`: set `ZSH_THEME="powerlevel10k/powerlevel10k"`, set `plugins=(...)` block, append DevOps aliases + fzf/zoxide tool-integration heredoc — same content as `setup-terminal.sh` (guarded by grep check, only appended once).
10. Install iTerm2 Shell Integration: download `https://iterm2.com/shell_integration/zsh` to `~/.iterm2_shell_integration.zsh`, append `source` line to `.zshrc` guarded by grep check.
11. Copy `iterm2/com.dotfiles.json` into `~/Library/Application Support/iTerm2/DynamicProfiles/` (mkdir -p first).
12. `defaults write com.googlecode.iterm2 "Default Bookmark Guid" -string "557036D3-EF41-4D30-A395-3F301A17D49B"` to make the profile default for new windows/tabs. Same GUID is the `Guid` field inside `com.dotfiles.json`.
13. Echo completion message: restart iTerm2 to pick up dynamic profile.

## Theme data

Colors extracted directly from user's existing `~/Documents/macos-terminal-themes-master/themes/Ubuntu.terminal` (Apple Terminal plist, NSKeyedArchiver-encoded NSColor values decoded via regex on embedded RGB float strings):

| Key | Hex |
|---|---|
| Background | #300A24 |
| Foreground/Bold/Text | #EEEEEC |
| Cursor | #BBBBBB |
| Selection | #B5D5FF |
| ANSI Black | #2E3436 |
| ANSI Red | #CC0000 |
| ANSI Green | #4E9A06 |
| ANSI Yellow | #C4A000 |
| ANSI Blue | #3465A4 |
| ANSI Magenta | #75507B |
| ANSI Cyan | #06989A |
| ANSI White | #D3D7CF |
| Bright Black | #555753 |
| Bright Red | #EF2929 |
| Bright Green | #8AE234 |
| Bright Yellow | #FCE94F |
| Bright Blue | #729FCF |
| Bright Magenta | #AD7FA8 |
| Bright Cyan | #34E2E2 |
| Bright White | #EEEEEC |

Baked directly into `com.dotfiles.json` as a static dynamic-profile file (no runtime conversion step in the script — conversion happened once during design).

Font: MesloLGS NF, size 13 (matches `setup-terminal.sh`'s Terminal.app font size).

## Out of scope
- No transparency/blur (screenshot shows opaque background).
- No migration of existing iTerm2 preferences (assumes fresh iTerm2 install).
- No changes to setup-terminal.sh itself (Terminal.app path stays as-is, untouched).
