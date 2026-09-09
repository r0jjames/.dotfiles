# ghostty (macOS, Linux)

[Ghostty](https://ghostty.org/) with the repo's theme + font — the same look as
the [iTerm2](../iterm2/) profile. Primarily used for the Claude CLI. iTerm2 is
left installed as a fallback; the two coexist.

One [`config`](config) serves both platforms: `~/.config/ghostty/config` is
already Ghostty's path on Linux as well as macOS, and the `macos-*` keys are
defined on every platform (inert off macOS), so nothing needs branching.

## Run

```sh
./install.py install ghostty
```

## What it does

- Installs Ghostty + MesloLGS Nerd Font Mono. On macOS both are Homebrew casks
  (the font is a no-op if the iTerm2 tool already installed it). On Linux
  Ghostty comes from apt — the `ppa:mkasberg/ghostty-ubuntu` PPA before Ubuntu
  26.04, the Ubuntu archive from 26.04 on — and since Homebrew on Linux has no
  casks at all, [`lib/fonts.py`](../lib/fonts.py) unpacks the font from the
  upstream Nerd Fonts release into `~/.local/share/fonts` instead.
  That font must be the Nerd Fonts build: it is the one whose family is
  `MesloLGS Nerd Font Mono`, the name `config` asks for. The MesloLGS NF files
  mirrored in `powerlevel10k-media` (what the top-level README points Windows
  at) install under the *different* family `MesloLGS NF` and would silently
  fall back.
- Copies [`config`](config) (theme + font) to `~/.config/ghostty/config`
- Sets `macos-option-as-alt = true` so Option reaches the shell and tmux as
  Alt. This is an input setting, not a keymap: no key is bound to a Ghostty
  action, so the file stays portable across environments.

## Default terminal (Linux)

The Linux install also makes Ghostty the default terminal, so Ctrl+Alt+T and
"Open in Terminal" open it:

- `sudo update-alternatives --set x-terminal-emulator /usr/bin/ghostty` —
  Ghostty's `.deb` registers itself at priority 40, *below*
  `gnome-terminal.wrapper`, so auto mode keeps choosing GNOME's. `--set`
  pins it manually.
- `gsettings set org.gnome.desktop.default-applications.terminal exec ghostty`
  (with `exec-arg` `-e`) for GNOME apps that read that key directly.

There is no XDG lever for this: `xdg-settings` on Ubuntu 24.04 knows only
`default-web-browser` and `default-url-scheme-handler` — no
`default-terminal`. Already-open terminal windows keep their old program
until relaunched.

macOS is untouched; set the default there in Ghostty's own settings.

Ghostty injects its shell integration automatically — nothing is sourced in
[`zsh/.zshrc`](../zsh/.zshrc), unlike the iTerm2 setup.

Restart Ghostty after first run to pick up the config.

## Tweaking the theme

Edit `config`, re-run the installer (it re-copies when the file differs),
restart Ghostty.

The color values mirror [`iterm2/com.dotfiles.json`](../iterm2/com.dotfiles.json);
keep them in sync if you change one.

`selection-foreground` is the background purple, not the foreground white.
Both profiles originally paired near-white selected text with the pale blue
selection background — about 1.3:1, so selected text was effectively
invisible. Dark-on-pale-blue is roughly 11.6:1. The iTerm2 profile's
`Selected Text Color` carries the same fix; keep the two in step.

One setting has no iTerm2 equivalent: `minimum-contrast = 1.1`, which only
guards against text that is literally invisible. It is deliberately *not* set
to 3. Ghostty does not lift a low-contrast color toward the foreground — it
swaps it for pure white or pure black — so against `#300a24` a threshold of 3
flattened red, blue, magenta and both greys to plain white, destroying the
palette it was meant to protect. See the comment in [`config`](config).

## Keymaps

Deliberately not in `config`. Set keybindings per-environment (e.g. inside a
Citrix VDI) so the shared config stays portable.

## Keys

Ghostty's `⌘` bindings and tmux's prefix bindings side by side:
[docs/cheatsheet-tmux-ghostty.md](../docs/cheatsheet-tmux-ghostty.md).
