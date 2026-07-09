# Claude Code

Reproducible Claude Code setup: CLI, global settings, plugins, statusline,
plus an inventory of every installed plugin/skill and how to invoke it.

## What setup.sh does

```sh
./install.sh claude    # or: bash claude/setup.sh
```

1. Installs the Claude Code CLI if missing (official native installer,
   lands in `~/.local/bin/claude`).
2. Symlinks `claude/settings.json` → `~/.claude/settings.json`.
3. Symlinks `claude/statusline-command.sh` → `~/.claude/statusline-command.sh`.
4. Symlinks `claude/CLAUDE.md` → `~/.claude/CLAUDE.md` (global memory, loaded
   into every session — keep it short).

Plugins are **not** installed by the script: `settings.json` carries
`enabledPlugins` and `extraKnownMarketplaces`, so Claude Code fetches the
marketplaces and installs every enabled plugin on its next start.

The VS Code extension (`anthropic.claude-code`) is installed by the `vscode`
tool — it is listed in `vscode/extensions.txt` along with
`yahyashareef.claude-code-usage-tracker`.

Because `~/.claude/settings.json` is a symlink into this repo, runtime
changes (theme toggle, enabling a plugin) show up as a git diff here.
Review them: commit to keep, checkout to revert.

## Not managed by this repo

- `~/.claude.json` — machine state. Holds the global MCP servers; currently
  `MCP_DOCKER` (Docker MCP gateway: `docker mcp gateway run`). Re-add on a
  new machine with: `claude mcp add MCP_DOCKER -s user -- docker mcp gateway run`.
  It only connects while Docker Desktop is running — a "Failed to connect"
  in `claude mcp list` with Docker stopped is expected, not a config bug.
- `~/.claude/projects/` (per-project memory), sessions, history, plugin cache.
- claude.ai connectors (Gmail, Calendar, Spotify, …) — configured in the
  claude.ai account, not on this machine.

## Marketplaces

| Marketplace | Source |
|---|---|
| claude-plugins-official | github.com/anthropics/claude-plugins-official |
| caveman | github.com/JuliusBrussee/caveman |
| superpowers-marketplace | github.com/obra/superpowers-marketplace (known, no plugins enabled from it) |

## Installed plugins and their skills

Skills are invoked as slash commands (`/plugin:skill`) or picked up
automatically by Claude when the task matches the skill description.

**Global vs per-project:** heavy stack plugins — `vercel`, `supabase`,
`frontend-design` — are installed but **disabled globally**
(`"…": false` in `enabledPlugins`) so their ~45 skill descriptions don't
load into every session. Projects that need them re-enable per repo in
`.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "vercel@claude-plugins-official": true,
    "supabase@claude-plugins-official": true,
    "frontend-design@claude-plugins-official": true
  }
}
```

Currently enabled this way in `~/Dev/worship-lineup`.

### superpowers — disciplined dev workflow (obra)

The core process plugin. Workflow: brainstorm → spec → plan → implement.
Specs and plans land in `docs/superpowers/specs/` and `docs/superpowers/plans/`.

| Skill | Use |
|---|---|
| `/superpowers:brainstorming` | Before any creative/feature work; turns an idea into an approved design spec |
| `/superpowers:writing-plans` | Turn a spec into a step-by-step implementation plan |
| `/superpowers:executing-plans` | Execute a written plan with review checkpoints |
| `/superpowers:subagent-driven-development` | Execute plan tasks via subagents in-session |
| `/superpowers:dispatching-parallel-agents` | 2+ independent tasks in parallel |
| `/superpowers:test-driven-development` | TDD for any feature/bugfix |
| `/superpowers:systematic-debugging` | Any bug or unexpected behavior, before proposing fixes |
| `/superpowers:verification-before-completion` | Verify with evidence before claiming done |
| `/superpowers:requesting-code-review` | After completing major work |
| `/superpowers:receiving-code-review` | Before implementing review feedback |
| `/superpowers:finishing-a-development-branch` | Merge/PR/cleanup decision when work is done |
| `/superpowers:using-git-worktrees` | Isolated workspace for feature work |
| `/superpowers:writing-skills` | Create or edit skills |

### caveman — token-efficient output (JuliusBrussee)

Session hook activates caveman mode automatically (terse replies, full
technical substance). Level persists per session.

| Skill | Use |
|---|---|
| `/caveman lite\|full\|ultra` | Switch intensity; "stop caveman" reverts |
| `/caveman-commit` | Terse Conventional Commits message |
| `/caveman-review` | One-line-per-finding code review |
| `/caveman-stats` | Real session token usage + savings |
| `/caveman-compress FILE` | Compress memory files (CLAUDE.md etc.) |
| `/caveman-init` | Drop caveman rule into current repo |
| `/caveman-help` | Quick reference card |

Also ships subagents: `cavecrew-investigator` (locate code),
`cavecrew-builder` (1–2 file edits), `cavecrew-reviewer` (diff review) —
compressed output saves main-thread context.

### skill-creator

| Skill | Use |
|---|---|
| `/skill-creator:skill-creator` | Create, improve, or benchmark skills |

### vercel (per-project only)

Slash commands: `/vercel:deploy` (add `prod` for production), `/vercel:env`,
`/vercel:status`, `/vercel:bootstrap`, `/vercel:marketplace`.
Plus ~30 auto-triggering knowledge skills (nextjs, ai-sdk, shadcn,
vercel-functions, storage, firewall, …) and agents (`vercel:ai-architect`,
`vercel:deployment-expert`, `vercel:performance-optimizer`).
Includes the Vercel MCP server (deployments, logs, projects).

### supabase (per-project only)

Auto-triggering skills: `supabase:supabase` (any Supabase task),
`supabase:supabase-postgres-best-practices` (Postgres query/schema work).
Includes the Supabase MCP server (migrations, SQL, logs, advisors).

### code-simplifier

Agent `code-simplifier:code-simplifier` — simplify recently modified code
while preserving behavior.

### claude-md-management

| Skill | Use |
|---|---|
| `/claude-md-management:revise-claude-md` | Update CLAUDE.md with session learnings |
| `claude-md-improver` | Audit/improve CLAUDE.md files (auto-triggers) |

### claude-code-setup

`claude-automation-recommender` — analyze a codebase, recommend hooks,
subagents, skills, MCP servers.

### frontend-design (per-project only)

`frontend-design:frontend-design` — intentional visual design guidance for
new or reworked UI (auto-triggers on UI work).

## Project-level conventions

- `.claude/settings.json` in a repo holds shareable project config — e.g.
  per-project `enabledPlugins` (see worship-lineup above).
- `.claude/settings.local.json` in a repo holds per-project permission
  grants (committed here for this repo). Prune stale one-off entries
  occasionally; `/fewer-permission-prompts` builds a sane allowlist.
- `docs/superpowers/specs/YYYY-MM-DD-<topic>-design.md` and
  `docs/superpowers/plans/` — superpowers workflow artifacts.
- No custom user-level skills yet (`~/.claude/skills/` unused); add one
  with `/skill-creator:skill-creator` and track it here if it should be
  reproducible.

## Useful commands

```sh
claude --version          # CLI version
claude doctor             # health check
claude plugin list        # installed plugins
claude mcp list           # MCP servers
/plugin                   # in-session plugin manager
/skills                   # in-session skill browser
/statusline               # statusline config helper
```
