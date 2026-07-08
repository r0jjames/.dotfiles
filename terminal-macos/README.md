# terminal-macos (macOS only)

Apple Terminal.app: Solarized Dark theme + MesloLGS Nerd Font.

## Run

```sh
./terminal-macos/setup.sh        # or: ./install.sh terminal-macos
```

## What it does

- Installs MesloLGS Nerd Font (Homebrew cask)
- Downloads the [macos-terminal-themes](https://github.com/lysyi3m/macos-terminal-themes) collection to `~/Downloads` and imports any themes not yet loaded
- Sets **Solarized Dark** as the default + startup window profile

Terminal.app quits/relaunches during theme import — expected. Set the font manually if needed: Terminal → Settings → Profiles → Solarized Dark → Font → MesloLGS NF. Skips itself on Linux/WSL.

Prefer [iTerm2](../iterm2/README.md) or [WezTerm](../wezterm/README.md) for daily use; this keeps the stock terminal usable.
