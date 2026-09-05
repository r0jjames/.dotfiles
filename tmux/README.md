# tmux

Terminal multiplexer with a status bar themed to match Ghostty, plus a
handful of keys that tmux leaves unbound. No plugin manager, no `tpm`, no
bootstrap step — one symlink and the config is live.

## Run

```sh
./install.py install tmux
```

Installs `tmux` via Homebrew and symlinks this whole directory to
`~/.config/tmux`, so `tmux.conf` and `scripts/` stay together.

## Defaults are not touched

Every key below fills a slot that stock tmux leaves empty. Nothing is
rebound, nothing is unbound, and the `root`, `copy-mode` and `copy-mode-vi`
tables are byte-identical to a `tmux -f /dev/null` server. What you read in
`man tmux` or see in `prefix ?` is what this config does.

Two knobs are deliberately left alone for the same reason:

- windows stay **0-indexed** (`prefix 0` is the first window, as documented)
- copy mode keeps its **emacs keys** — `mode-keys vi` rewrites that whole table

To check after editing `tmux.conf`:

```sh
tmux -L default-probe -f /dev/null new-session -d
diff <(tmux -L default-probe list-keys -T prefix | sort) \
     <(tmux list-keys -T prefix | sort)          # only additions expected
tmux -L default-probe kill-server
```

## Added keys

Full key reference for both layers, stock keys included:
**[docs/cheatsheet-tmux-ghostty.md](../docs/cheatsheet-tmux-ghostty.md)**.

Prefix is `C-b`, unchanged.

| Key | Does | Stock key it avoids |
|---|---|---|
| `prefix C-h/C-j/C-k/C-l` | focus pane left/down/up/right | `l` is `last-window` |
| `prefix M-h/M-j/M-k/M-l` | resize pane (repeatable) | `L` is `switch-client -l` |
| `prefix g` | fzf project picker in a popup | `f` is `find-window`, `s` the session tree |
| `prefix R` | reload `tmux.conf` | `r` is `refresh-client` |

The stock equivalents still work: `prefix` + arrows to move, `C-`/`M-` arrows
to resize, `prefix %` and `prefix "` to split.

## Status bar

Top bar, refreshed every 5s, colored from Ghostty's own palette
(`ghostty/config`) so the two read as one surface.

- **Left** — session name. Turns **amber the moment the prefix is live**, so
  you can always see whether tmux or the shell will take the next key.
- **Middle** — windows; the current one is raised and green, `` marks zoom.
- **Right** — kube context/namespace, git branch of the focused pane (`*`
  when dirty), host, clock.

Both right-hand segments come from `scripts/status.sh`, which prints nothing
when the tool is missing — no `kubectl`, no kube segment, no error text.

Pane borders carry the running command, so a wall of panes is readable at a
glance.

## Project picker

`prefix g` opens `scripts/sessionizer.sh` in a popup: fzf over every git repo
up to three levels under `~/Dev/projects` and `~/Dev`, then attaches a
session named after the repo (creating it the first time). Needs `fzf`, which
the [zsh module](../zsh/README.md) installs; `fd` is used when present and
`find` otherwise.

## Starting tmux

There is no auto-attach: a new Ghostty tab or split is a plain shell.

```sh
tmux                 # attach to the last session, or create one
tmux new -s main     # named session
tmux attach -t main
```

This is deliberate. `tmux new-session -A -s main` in `.zshrc` looks tidy but
attaches every new terminal surface to the *same* session, so `⌘T` and `⌘D`
produce mirrored views of the same panes, both clamped to the smaller
client's size. Ghostty tabs/splits and tmux windows/panes are two solutions
to one problem — pick tmux's (`prefix c`, `prefix %`, `prefix "`) and leave
Ghostty at one window.

## Requirements

A Nerd Font for the powerline separators and icons — Ghostty and iTerm2 are
already set to `MesloLGS Nerd Font Mono` by this repo. In a terminal without
one, the separators show as boxes; everything still works.

## Why `~/.config/tmux` and not `$XDG_CONFIG_HOME`

`tmux.conf` calls its scripts by absolute path, and tmux's config expansion
has no default-value form — a line containing `${XDG_CONFIG_HOME:-...}` fails
to parse (3.7c). So `~/.config/tmux` is always linked and always the path the
config names. If `XDG_CONFIG_HOME` is set elsewhere, the installer adds a
second link there too, because tmux searches that location first.

## Uninstall

```sh
./install.py uninstall tmux
```

Removes the symlink(s) and restores any config that was backed up. Homebrew
packages are left installed.
