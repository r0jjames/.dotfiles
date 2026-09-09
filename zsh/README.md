# zsh

Shell stack: zsh + modern CLI tools + plugins + managed `~/.zshrc`.

## Run

```sh
./install.py install zsh
```

## What it installs

- **zsh** — preinstalled on macOS; on Linux installed via `apt` and made the
  shell interactive terminals land in (see [Login shell](#login-shell))
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

## Login shell

On Linux the installer takes whichever of two routes actually works:

- **`chsh -s /usr/bin/zsh`** for a normal local account. It prompts for your
  password once and takes effect on the next login.
- **A hand-off block appended to `~/.bashrc`** when the account is
  directory-managed — served by Active Directory (centrifydc), sssd, LDAP or
  winbind rather than by `/etc/passwd`. `chsh` writes `/etc/passwd`, so it
  cannot move such an account at all; the installer detects this (no
  `/etc/passwd` line for the user) and skips straight to the hand-off instead
  of prompting for a password that would fail anyway. A failed `chsh` on a
  local account falls back to the same block.

The block is marked with `# >>> dotfiles: zsh hand-off >>>` and execs zsh for
interactive bash shells only, so `scp`, `rsync` and `bash -c` stay on bash:

```sh
case $- in
  *i*)
    if [ -z "$ZSH_VERSION" ] && [ -x /usr/bin/zsh ]; then
      exec /usr/bin/zsh -l
    fi
    ;;
esac
```

Because it sits in `~/.bashrc` rather than in the passwd record, it covers
every entry point a login-shell change would have: Ghostty, tmux, SSH, the
VS Code terminal and Claude Code. Re-running the installer rewrites a stale
block rather than stacking a second one, and `./install.py uninstall zsh`
removes it. If `chsh` later succeeds, or the login shell becomes zsh by any
other means, the next install run deletes the block as redundant.

To confirm which route applied:

```sh
getent passwd "$USER" | cut -d: -f7   # the real login shell
grep -c 'dotfiles: zsh hand-off' ~/.bashrc
```

## Platform notes

- **WSL:** `chsh` may prompt for your password once. Homebrew-on-Linux is added to PATH by the `.zshrc` automatically.
