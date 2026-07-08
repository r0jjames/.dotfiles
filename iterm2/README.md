# iterm2 (macOS only)

iTerm2 with the repo's theme/font profile and shell integration.

## Run

```sh
./iterm2/setup.sh        # or: ./install.sh iterm2
```

## What it does

- Installs iTerm2 + MesloLGS Nerd Font (Homebrew casks)
- Downloads iTerm2 shell integration to `~/.iterm2_shell_integration.zsh` (sourced by [`zsh/.zshrc`](../zsh/.zshrc) when present)
- Installs the dynamic profile [`com.dotfiles.json`](com.dotfiles.json) (theme + font) and sets it as the default profile

Restart iTerm2 (Cmd+Q, relaunch) after first run. Skips itself on Linux/WSL.

## Tweaking the theme

Edit `com.dotfiles.json`, re-run the script (it re-copies when the file differs), restart iTerm2.
