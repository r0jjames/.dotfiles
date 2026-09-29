# vscode

VS Code settings, keybindings, and a curated extension list — same editor on the personal Mac, the Ubuntu laptop and the work Windows machine.

## Files

- [`settings.json`](settings.json) — Solarized Light / Monokai Dimmed following the OS appearance, vscode-icons, MesloLGS Nerd Font (editor + terminal), autosave, git smart-commit/autofetch, Go via gopls, per-language format-on-save
- [`keybindings.json`](keybindings.json) — custom terminal/file-tree/navigation keybindings. Every binding ships a `cmd+` and a `ctrl+` variant, so one file covers all three platforms; the unused half is inert.
- [`extensions.txt`](extensions.txt) — curated extension ids, grouped by purpose (DevOps, Remote/WSL, Python, Java, Go, Markdown, AI, docs/walkthroughs, utilities)
- [`copilot-instructions.template.md`](copilot-instructions.template.md) — template to copy into a project's `.github/`. Not installed by `install.py`; copied per project by hand.

### Platform tags in extensions.txt

Lines may end with `@macos`, `@linux` or `@windows`; untagged lines install on all three machines.
Used for the AI split — Claude Code only on the personal Mac and the Ubuntu laptop — and for
Windows-only extensions like Remote-WSL:

```
anthropic.claude-code @macos @linux
ms-vscode-remote.remote-wsl @windows
```

Copilot is **not** listed: from VS Code 1.139 it ships built in
(`GitHub.copilot-chat` 0.67.0 under `Contents/Resources/app/extensions/copilot`),
and listing either `github.copilot` or `github.copilot-chat` makes every install
run fail — the built-in cannot be downgraded to the marketplace version, and
`github.copilot` depends on that older build. It runs on both accounts anyway:
Business on the work Windows machine, Pro personally.

After installing, the installer reports extensions that are installed but not in
the list (with ready-to-paste `code --uninstall-extension` commands). It never
uninstalls anything itself — extras on the work machine may be IT-mandated.

## Run

```sh
./install.py install vscode
```

The installer **copies** `settings.json` and `keybindings.json` into the platform's VS Code User directory (with a dated backup of whatever was there) and installs missing extensions:

| Platform | User directory |
|---|---|
| macOS | `~/Library/Application Support/Code/User` |
| Ubuntu | `~/.config/Code/User` |
| Windows (Git Bash) | `$APPDATA/Code/User` |

**Copies, not symlinks, on every platform** — see [Settings Sync](#settings-sync) below. Edits made in the VS Code settings UI therefore do **not** flow back here: change the file in this repo, commit, then re-run the installer.

A machine set up before the copy-mode change still holds symlinks from the old link mode. The installer removes them on the next run (backing up any that point somewhere other than this repo) and copies in their place.

### Work Windows machine

VS Code runs on the Windows host (WSL connects via the Remote-WSL extension), so apply settings from **Git Bash**, not WSL:

1. Install [VS Code](https://code.visualstudio.com/) and [Git for Windows](https://gitforwindows.org/) (includes Git Bash).
2. Make sure `code` works in Git Bash (installed by default; otherwise Cmd Palette → *Shell Command: Install 'code' command in PATH*).
3. In Git Bash:
   ```sh
   git clone https://github.com/<you>/.dotfiles.git ~/dotfiles
   cd ~/dotfiles && ./install.py install vscode
   ```

## Copilot token routing

Copilot bills **one premium request per prompt you send**, times the model
multiplier — not per token, and not per autonomous step the agent takes inside
one prompt. So the expensive event is the **retry** after a wrong answer, and
the goal is to make each prompt land, not to make it small.

That is the opposite of Claude Code, which bills tokens of context per turn.
Don't carry habits across — see `claude/README.md` for that half.

| Task | Mode | Model |
| --- | --- | --- |
| Single well-scoped edit | Edit | Included model |
| Multi-file or open-ended change | Agent | Included model; premium if it stalls |
| Design a change before making it | Plan (read-only) | Premium model |
| Completions while typing | Inline / NES | n/a — not premium-billed |

**Rules that outweigh every setting:**

- **Do not run Copilot code review casually — 13 premium requests per review.**
  Largest single line item available.
- **Default to an included model**; reach for a premium one only for
  architecture and debugging.
- **Write `.github/copilot-instructions.md`** from
  [`copilot-instructions.template.md`](copilot-instructions.template.md). One
  prevented misunderstanding per session pays for the file.
- **Start a new chat for unrelated work** rather than letting one thread carry
  irrelevant history.

The settings in `settings.json` deliberately *widen* context per prompt
(`codesearch`, `temporalContext`, instruction-file pinning): under per-prompt
billing that context is free, and it is what removes retries.

`chat.agent.maxRequests` is deliberately left at its default of 25 — it caps
iterations inside a single billed prompt, so lowering it truncates work and
forces a second prompt. `github.copilot.chat.virtualTools.threshold` is not set
either; set it only if the 128-tools-per-request error appears, since VS Code
documents no default value for it.

Billing note: GitHub moved from request-based to usage-based billing on
2026-06-01, and model multipliers are now legacy (Pro/Pro+ annual only). The
direction above holds under both. Check the live allowance in GitHub billing
settings rather than trusting a number written here.

## Settings Sync

VS Code's built-in Settings Sync is on and carries these settings to the account, which distributes them across machines. That makes the loop:

```
edit this repo  ->  ./install.py install vscode  ->  VS Code  ->  Settings Sync  ->  account  ->  other machines
```

Sync rewrites `settings.json` in the User directory on every sync-down. A symlink would send that write straight into this repo — hence copy mode everywhere. The repo stays the versioned source of truth; the account handles distribution.

`./install.py status` reports `vscode` as `not installed` when the installed copy has drifted from the repo (a UI edit, or a sync-down carrying someone else's change). Diff the two, fold anything worth keeping back into this repo, then re-run the installer.

## Go

`golang.go` plus the `go.*` / `gopls` block in `settings.json` cover it: gopls formatting and import organisation on save, staticcheck diagnostics, `golangci-lint` on save per package, verbose tests with coverage on a single test. `alt+t` runs the test under the cursor and `alt+y` toggles coverage (see `keybindings.json`).

Tooling (`gopls`, `dlv`, `golangci-lint`) is **not** installed by this repo — `golang.go` prompts to install anything missing the first time a Go file opens, and `go.toolsManagement.autoUpdate` keeps it current.

## Requirements / notes

- `code` CLI on PATH (installer skips extensions with instructions if missing).
- The editor font falls back Menlo/Consolas/`monospace` until a MesloLGS Nerd Font is installed ([`iterm2/`](../iterm2/README.md) or [`terminal-macos/`](../terminal-macos/README.md) install it on macOS; on Ubuntu and Windows install manually — see root README).
