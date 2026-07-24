# ghostty (macOS only)

[Ghostty](https://ghostty.org/) with the repo's theme + font — the same look as
the [iTerm2](../iterm2/) profile. Primarily used for the Claude CLI. iTerm2 is
left installed as a fallback; the two coexist.

## Run

```sh
./install.py install ghostty
```

## What it does

- Installs Ghostty + MesloLGS Nerd Font (Homebrew casks; the font is a no-op if
  the iTerm2 tool already installed it)
- Copies [`config`](config) (theme + font) to `~/.config/ghostty/config`

Ghostty injects its shell integration automatically — nothing is sourced in
[`zsh/.zshrc`](../zsh/.zshrc), unlike the iTerm2 setup.

Restart Ghostty after first run to pick up the config.

## Tweaking the theme

Edit `config`, re-run the installer (it re-copies when the file differs),
restart Ghostty.

The color values mirror [`iterm2/com.dotfiles.json`](../iterm2/com.dotfiles.json);
keep them in sync if you change one.

## Keymaps

Deliberately not in `config`. Set keybindings per-environment (e.g. inside a
Citrix VDI) so the shared config stays portable.
