# starship

[Starship](https://starship.rs) cross-shell prompt.

## Run

```sh
./install.py install starship
```

## What it does

- Installs `starship` via Homebrew (macOS + WSL Ubuntu)
- Symlinks [`starship.toml`](starship.toml) to `~/.config/starship.toml`

The `eval "$(starship init zsh)"` line lives in [`zsh/.zshrc`](../zsh/.zshrc) — this script never edits `~/.zshrc`.

## Customizing

Edit `starship.toml` here, commit, and every machine picks it up on `git pull` (symlinked, no re-run needed). Reference: [starship.rs/config](https://starship.rs/config/).
