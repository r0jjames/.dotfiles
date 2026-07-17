# wezterm

[WezTerm](https://wezterm.org) terminal emulator + config.

## Run (macOS)

```sh
./install.py install wezterm
```

Installs WezTerm + fonts via Homebrew casks and symlinks [`wezterm.lua`](wezterm.lua) / [`events.lua`](events.lua) into `~/.config/wezterm/`.

## Windows (WSL setup)

The installer marks wezterm macOS-only — WezTerm must run on the Windows host:

1. Install WezTerm on Windows: `winget install wez.wezterm`
2. Point it at this repo's config. Create `%USERPROFILE%\.wezterm.lua` containing:
   ```lua
   -- Load the repo config from inside WSL
   package.path = package.path .. ";\\\\wsl$\\Ubuntu\\home\\<user>\\Dev\\.dotfiles\\wezterm\\?.lua"
   return dofile("\\\\wsl$\\Ubuntu\\home\\<user>\\Dev\\.dotfiles\\wezterm\\wezterm.lua")
   ```
   (replace `<user>`; adjust distro name if not `Ubuntu`)
3. Set WSL as the default shell in WezTerm if desired (`default_domain = "WSL:Ubuntu"` in a local override).

Alternatively just copy `wezterm.lua`/`events.lua` to `%USERPROFILE%\.config\wezterm\` and re-copy after changes.
