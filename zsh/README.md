# zsh

Shell stack: zsh + modern CLI tools + plugins + managed `~/.zshrc`.

## Run

```sh
./install.py install zsh
```

## What it installs

- **zsh** — preinstalled on macOS; on WSL Ubuntu installed via `apt` and set as login shell (`chsh`)
- **CLI tools** (Homebrew): `bat`, `eza`, `fzf`, `zoxide`, `ripgrep`, `fd`, `htop`
- **Plugins** (Homebrew): `zsh-autosuggestions`, `zsh-syntax-highlighting`
- **`~/.zshrc`** — symlinked to [`./.zshrc`](.zshrc)

## The .zshrc

- Prompt: [Starship](../starship/README.md) (init line lives here; no Oh My Zsh, no Powerlevel10k)
- DevOps aliases: `k`, `kctx`, `kns`, `d`, `dc`, `tf`, plus `ll`/`ls` (eza) and `cat` (bat)
- `fzf` keybindings (Ctrl+R history, Ctrl+T files, backed by `fd`) and `zoxide` (`z <dir>`)
- Everything is guarded with `command -v`, so the file is safe even before tools are installed

## Machine-local overrides

Put anything machine-specific (work proxies, secrets, extra PATH entries) in `~/.zshrc.local` — it is sourced last and never touched by this repo.

## Platform notes

- **WSL:** `chsh` may prompt for your password once. Homebrew-on-Linux is added to PATH by the `.zshrc` automatically.
