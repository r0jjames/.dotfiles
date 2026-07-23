# Rancher Desktop: replace Docker Desktop + OrbStack

## Context

Docker Desktop (`/Applications/Docker.app`) is installed manually on this
machine — not brew-managed, not tracked by dotfiles. `orbstack` is installed
via brew cask but also untracked by dotfiles (no `lib/tools/orbstack.py`
ever existed). Neither is a dotfiles-managed tool today. This adds Rancher
Desktop as a new managed tool and retires both alternatives on this machine.

`claude/CLAUDE.md` (symlinked into `~/.claude/CLAUDE.md`) currently says:

> The `MCP_DOCKER` MCP server only connects when Docker Desktop is running;
> a failed connection there is expected, not a config bug.

This needs to reference Rancher Desktop instead, since that becomes the
active Docker-socket provider.

## Decisions

- Container engine mode: **dockerd (moby)** — full `docker` CLI/socket
  compatibility, required for MCP_DOCKER and any existing docker-based
  workflows.
- Kubernetes (bundled k3s): **disabled** by default — lighter weight, not
  needed day-to-day; can be turned on later in-app if a use case appears.
- Docker Desktop and OrbStack: **not** auto-removed by the installer. Both
  are flagged with instructions during Rancher Desktop's install so the
  user removes them deliberately (matches this repo's existing convention
  of never silently touching software outside a tool's own scope — see
  `maven.py`'s uninstall, which leaves SDKMAN candidates in place with a
  printed manual command).

## Component: `lib/tools/rancher_desktop.py`

Follows the `maven.py` / `iterm2.py` shape — no dedicated subfolder, no
config files to symlink, registered directly in `lib/tools/__init__.py`.

```python
TOOL = Tool(
    name="rancher-desktop",
    doc="Rancher Desktop (dockerd/moby engine, k3s disabled)",
    platforms=frozenset({"macos"}),
    casks=("rancher-desktop",),
    post_install=_post,
    extra_uninstall=_uninstall,
    status_probe=_probe,
)
```

- `_post()`:
  1. Print a one-time reminder with the exact command to run after first
     launch (Rancher Desktop's first run needs the GUI wizard completed
     before its backend/`rdctl` API is available, so this can't be
     automated blindly at install time):
     `rdctl set --container-engine.name moby --kubernetes.enabled=false`
     (flags confirmed against Rancher Desktop's official `rdctl` command
     reference: `--container-engine.name` accepts `docker`/`containerd`/
     `moby`, `--kubernetes.enabled` is a bool).
  2. Warn (print only, no action) when conflicting software is present:
     - `pgrep -x Docker` succeeds → tell user to quit Docker Desktop
     - `brew list --cask orbstack` succeeds → print
       `brew uninstall --cask orbstack` for the user to run themselves
     - `/Applications/Docker.app` exists → note it isn't brew-managed,
       print reminder to remove it manually (drag to Trash)
  3. Print a reminder to launch Rancher Desktop once to complete first-run
     setup, then run the `rdctl set` command from step 1 (matches
     `iterm2.py`'s "Restart iTerm2" reminder).
- `_uninstall()`: skip/warn only — app left in place, no settings to undo
  since nothing was written to disk by this tool (matches `maven.py` /
  `iterm2.py` convention: uninstall never removes brew packages or apps).
- `_probe()`: `Path("/Applications/Rancher Desktop.app").is_dir()`

## Docs

- `README.md`: add a row to the tool table, styled like the `maven` row
  (no folder link, since there's no dedicated subfolder):
  `| rancher-desktop | Rancher Desktop (dockerd engine, k3s disabled) | macOS only |`
- `claude/CLAUDE.md`: reword the MCP_DOCKER line to say Rancher Desktop
  instead of Docker Desktop.

## Testing

No dedicated test file (matches `maven`/`iterm2` — neither has one).
Generic `test_registry.py` checks cover the new entry automatically.
Manual verification after implementation:

1. `./install.py install rancher-desktop` — cask installs, reminder text
   and warnings print correctly for the existing Docker.app/orbstack
   state on this machine.
2. Launch Rancher Desktop, complete the first-run wizard, run
   `rdctl set --container-engine.name moby --kubernetes.enabled=false`,
   confirm engine mode is moby and Kubernetes is off in its own UI.
3. `docker context ls` shows a `rancher-desktop` context after first
   launch.
4. `./install.py status` shows `rancher-desktop` as installed.
