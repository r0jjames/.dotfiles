# terminal-windows (Windows / Git Bash only)

**Windows Terminal**, themed to match [Ghostty](../ghostty/README.md) — the
Windows member of the set alongside
[`terminal-macos/`](../terminal-macos/README.md) and
[`terminal-ubuntu/`](../terminal-ubuntu/README.md).

This is the terminal WSL Ubuntu runs inside on the work machine, so it is
worth having the same palette there as everywhere else.

## Run

From **Git Bash** (not WSL — the settings file lives on the Windows side):

```sh
./install.py install terminal-windows
```

Launch Windows Terminal at least once first, or there is no `settings.json`
to merge into and the tool skips with a note.

## What it does

- Adds a color scheme named **`Dotfiles Tango`** to `schemes` — the same 16
  Tango slots, background, cursor and selection colors as Ghostty.
- Points `profiles.defaults.colorScheme` at it, so every profile inherits it.
- Sets `profiles.defaults.font` to `MesloLGS Nerd Font Mono`, size 13.

## It merges — it does not overwrite

`settings.json` is a file you also edit by hand, so the tool reads it, changes
only the keys above, and writes it back. Everything else — your profiles,
keybindings, `copyOnSelect`, opacity — is preserved, and a re-run that would
change nothing does not rewrite the file at all.

Two caveats, both deliberate:

- **Comments are lost on a write.** Windows Terminal ships `settings.json`
  as JSONC, with `//` comments. They are stripped to parse it and cannot be
  put back. The file is backed up to `settings.json.bak-YYYY-MM-DD` before
  the first write, and the installer says so.
- The comment stripper matches string literals in the same pass, so a value
  containing `//` — a URL, a `C:\` path — survives intact. That is the bug
  a naive strip would introduce.

`./install.py uninstall terminal-windows` removes the scheme and clears the
two `defaults` keys, leaving the rest of the file alone.

## The font is not installed for you

Unlike the macOS and Ubuntu tools, this one does **not** install the Nerd
Font — on Windows that has to happen system-side. Download
[MesloLGS Nerd Font Mono](https://github.com/ryanoasis/nerd-fonts/releases/latest),
right-click the `.ttf` → *Install for all users*, then re-run. Naming a font
Windows does not have makes it fall back silently, so the installer prints a
reminder rather than assuming.

## Where settings.json lives

Checked in this order, first match wins:

| Install | Path under `%LOCALAPPDATA%` |
|---|---|
| Store | `Packages/Microsoft.WindowsTerminal_8wekyb3d8bbwe/LocalState/settings.json` |
| Preview | `Packages/Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe/LocalState/settings.json` |
| Unpackaged / scoop | `Microsoft/Windows Terminal/settings.json` |

## Status

`./install.py status` compares the stored scheme and the two `defaults` keys
against what the theme wants, so editing the scheme in Windows Terminal's UI
shows up as `not installed`.

> **Not yet run on real hardware.** This module was written and unit-tested
> on Linux (`tests/test_terminal_windows.py` covers the JSONC handling and
> the merge, which is where the risk is). The first run on the Windows box
> is still the real test — the backup is there for that reason.
