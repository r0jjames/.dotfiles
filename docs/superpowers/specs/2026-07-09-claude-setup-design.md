# Claude Code Setup — Design

**Date:** 2026-07-09
**Status:** Approved

## Goal

Make the Claude Code setup reproducible from the dotfiles repo: CLI install,
global settings, plugins, statusline, and VS Code extension — plus a curated
document of every installed plugin/skill and how to invoke it.

## Current state (captured 2026-07-09)

- Claude Code CLI 2.1.205, native install at `~/.local/bin/claude`
- `~/.claude/settings.json`: model, statusline command, 9 enabled plugins,
  2 extra marketplaces (`claude-plugins-official`, `caveman`)
- Plugins: superpowers, skill-creator, vercel, supabase, code-simplifier,
  claude-md-management, claude-code-setup, frontend-design (official) +
  caveman (JuliusBrussee/caveman)
- MCP: `MCP_DOCKER` gateway configured in `~/.claude.json` (machine state)
- VS Code: `anthropic.claude-code` + `yahyashareef.claude-code-usage-tracker`,
  already tracked in `vscode/extensions.txt`
- No user-level (`~/.claude/skills`) or project-level custom skills

## Design

New `claude/` tool directory following the existing dotfiles pattern
(`<tool>/setup.sh` + config files + README):

```
claude/
  setup.sh               # installer
  settings.json          # tracked ~/.claude/settings.json
  statusline-command.sh  # tracked statusline script (referenced by settings)
  README.md              # setup steps + plugin/skill inventory
```

### setup.sh

1. Install Claude Code CLI if missing via the official native installer
   (`curl -fsSL https://claude.ai/install.sh | bash`); otherwise report the
   installed version.
2. Symlink `claude/settings.json` → `~/.claude/settings.json` using
   `link_file` (dated backup of any existing real file).
3. Symlink `claude/statusline-command.sh` → `~/.claude/statusline-command.sh`.
4. No plugin install step: `enabledPlugins` + `extraKnownMarketplaces` in
   settings.json make Claude Code fetch marketplaces and install plugins on
   next start.
5. Remind that the VS Code extension is handled by the `vscode` tool.

### install.sh

Add `claude` to `ALL_TOOLS`. Cross-platform (macOS + Linux/WSL), not in
`MAC_ONLY`.

### README.md

- Install steps: CLI, settings symlink, first-run plugin sync, VS Code
  extension.
- Plugin inventory: each plugin, its skills, invocation (`/skill-name`),
  one-line when-to-use.
- MCP servers documented as a manual step (`~/.claude.json` is per-machine
  state, not managed by the repo).
- Project-level conventions: `.claude/settings.local.json` permissions,
  `docs/superpowers/` specs + plans.

## Decisions

- **Symlink over seed-copy** for settings.json: repo file is the live file,
  same discipline as zsh/nvim. Runtime changes (theme toggles, new plugins)
  show up as git diff to review and commit or revert.
- **Static curated README** over generated inventory: plugins change rarely;
  hand-written doc stays readable. Update it when adding/removing plugins.
- **Excluded from management:** `~/.claude.json`, memory dir, sessions,
  history, plugin cache — machine state, not configuration.

## Risks

- Claude Code rewrites settings.json at runtime; with a symlink this dirties
  the dotfiles working tree. Intentional — review the diff, commit or revert.
- Official installer URL may change; setup.sh warns and points to
  https://claude.com/claude-code docs on failure.
