# terminal-ubuntu (Ubuntu only)

The stock **GNOME Terminal**, themed to match [Ghostty](../ghostty/README.md) —
the Ubuntu counterpart to [`terminal-macos/`](../terminal-macos/README.md),
which does the same job for Terminal.app.

Ghostty is the daily driver. This exists because the stock terminal is still
what opens from the Files context menu, from an IDE's "open in terminal", or
when Ghostty is mid-upgrade — and a jarring default profile in those moments
is exactly the thing this repo is meant to prevent.

## Run

```sh
./install.py install terminal-ubuntu
```

Open a new terminal window to see it.

## What it does

Applies to the **default profile** (the one `gsettings get
org.gnome.Terminal.ProfilesList default` reports):

| Setting | Value |
|---|---|
| `background-color` / `foreground-color` | `#300A24` / `#EEEEEC` |
| `palette` | the 16 Tango slots |
| `cursor-background-color` / `-foreground-color` | `#BBBBBB` / `#300A24` |
| `font` | `MesloLGS Nerd Font Mono 13` |
| `use-theme-colors`, `use-system-font` | `false` — required, or GNOME ignores the above |
| `bold-is-bright` | `true`, matching Ghostty and iTerm2 |
| `cursor-shape` | `block` |
| `audible-bell` | `false` |
| `scrollback-unlimited` | `true` |

The Nerd Font is installed first if missing (see [`lib/fonts.py`](../lib/fonts.py)) —
naming a font the system does not have would silently fall back.

## Where the colors come from

**`ghostty/config` is the source of truth.** This tool parses the palette,
background, foreground, cursor and font straight out of it at install time.

That is deliberate. The palette already lives in two places —
[`ghostty/config`](../ghostty/config) and
[`iterm2/com.dotfiles.json`](../iterm2/com.dotfiles.json) — each carrying a
README note reminding you to keep them in sync. A third hand-maintained copy
would be a third thing to drift. Change `ghostty/config`, re-run this tool,
and GNOME Terminal follows.

## Why there is no config file to symlink

GNOME Terminal has no config file. Profiles live in dconf, so the only
interface is `gsettings`, and settings are *copied in* rather than linked.
That means:

- Re-run the installer after changing `ghostty/config` — nothing is live.
- `./install.py uninstall terminal-ubuntu` runs `gsettings reset` on exactly
  the keys above, returning the profile to GNOME's defaults.
- `./install.py status` compares every key against what the theme wants, so a
  profile edited by hand in Preferences shows as `not installed`.

The profile schema (`org.gnome.Terminal.Legacy.Profile`) is *relocatable* —
one instance per profile UUID — so it appears in `gsettings
list-relocatable-schemas`, never in `list-schemas`. Worth knowing if you
extend this.

## Skips

- **WSL** — no GNOME Terminal; the Windows-side terminal owns the theme.
- **A machine without GNOME Terminal** — skipped with a note, not an error.
  Ghostty carries the same theme, so nothing is lost.
