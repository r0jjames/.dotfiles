# Claude Code

Reproducible Claude Code setup: CLI, global settings, plugins, statusline,
plus an inventory of every installed plugin/skill and how to invoke it.

## What the installer does

```sh
./install.py install claude
```

1. Links `claude/settings.json` → `~/.claude/settings.json`.
2. Links `claude/statusline-command.sh` → `~/.claude/statusline-command.sh`.
3. Links `claude/CLAUDE.md` → `~/.claude/CLAUDE.md` (global memory, loaded
   into every session — keep it short).
4. Installs the Claude Code CLI if missing (official native installer,
   lands in `~/.local/bin/claude`).

Plugins are **not** installed by the installer: `settings.json` carries
`enabledPlugins` and `extraKnownMarketplaces`, so Claude Code fetches the
marketplaces and installs every enabled plugin on its next start.

The VS Code extension (`anthropic.claude-code`) is installed by the `vscode`
tool — it is listed in `vscode/extensions.txt` along with
`yahyashareef.claude-code-usage-tracker`.

Because `~/.claude/settings.json` is a symlink into this repo, runtime
changes (theme toggle, enabling a plugin) show up as a git diff here.
Review them: commit to keep, checkout to revert.

## Windows (Git Bash)

Same command, two differences:

- Symlinks need admin rights, so the three config files are **copied** into
  `~/.claude` (i.e. `%USERPROFILE%\.claude`). Copies are snapshots — re-run
  `./install.py install claude` after editing one, and runtime changes made
  inside Claude Code will **not** show up as a git diff here.
- The CLI comes from the PowerShell installer
  (`irm https://claude.ai/install.ps1 | iex`), driven via `powershell` from
  Git Bash. On a locked-down VDI (execution policy, proxy) that can fail —
  the installer warns and prints the manual command plus the
  `npm install -g @anthropic-ai/claude-code` alternative instead of aborting
  the run.

`statusLine.command` uses `$HOME` rather than an absolute path so the same
`settings.json` works on macOS, WSL and Windows.

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

### skill-creator (per-project only)

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

### code-simplifier (disabled — use the built-in `/simplify`)

Agent `code-simplifier:code-simplifier` — simplify recently modified code
while preserving behavior. Off globally: the built-in `/simplify` skill
covers the same ground without a plugin's description weight.

### claude-md-management (per-project only)

| Skill | Use |
|---|---|
| `/claude-md-management:revise-claude-md` | Update CLAUDE.md with session learnings |
| `claude-md-improver` | Audit/improve CLAUDE.md files (auto-triggers) |

### claude-code-setup (per-project only)

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
- `~/.claude/skills/` holds the repo's own skills (symlinked from
  `agent-skills/skills/`) plus installer-managed community skills. Add new
  ones through `agent-skills/install.py`, not by hand, so they stay
  reproducible.

## Token routing

Claude bills **tokens of context per turn**; Copilot bills **one premium
request per prompt**. The two need opposite handling, so don't carry habits
across — see `vscode/README.md` for the Copilot half.

Defaults set in `settings.json`: `model: sonnet`, `effortLevel: high`.

| Task | Model | Notes |
| --- | --- | --- |
| Routine edits, tests, refactors, reviews | `sonnet` (default) | Handles most coding work |
| Architecture, multi-step debugging, tricky design | `/model opus` | Switch for the task, then switch back |
| Verbose subagent work (log parsing, doc fetching) | `haiku` via subagent config | Output stays in the subagent's context |

Habits that matter more than any setting here:

- **`/clear` between unrelated tasks.** Claude re-sends the whole
  conversation every turn, so stale context is charged on every later
  message. `/rename` first if you want to `/resume` it later.
- **Plan mode (Shift+Tab) before large changes.** A wrong direction costs
  far more than the planning turn.
- **Delegate verbose output to subagents** so it never enters the main
  context.
- **Prefer CLI tools (`gh`, `kubectl`) over MCP servers** where both exist —
  no per-tool listing in context.
- **Watch `/context` and `/usage`.** `/usage` attributes recent spend to
  skills, subagents, plugins and individual MCP servers, and flags
  behaviours (long context, cache misses) above 10%.

### Skills that reduce tokens

Skills are not only weight to prune — several installed ones exist to cut
context. Reach for these instead of the default path:

| Instead of | Use | Why |
| --- | --- | --- |
| `Explore` agent, or grepping yourself | `caveman:cavecrew-investigator` | Returns a `file:line` table; the reads stay in the subagent |
| Opening files to orient in a new repo | `caveman:caveman-explore` | Read-only exploration, citations only, reads stay out of main context |
| A full review pass | `caveman:cavecrew-reviewer` | One line per finding, no prose |
| Guessing what a session cost | `/caveman-stats`, `/usage` | Actual token accounting |
| A heavy CLAUDE.md or memory file | `/caveman-compress` | Compresses the always-loaded text, keeps a backup |
| Re-reading the same files each session | `/graphify .` | Query a persistent graph instead |
| Re-exploring a repo you already mapped | `acquire-codebase-knowledge` | One discovery pass, written to `docs/codebase/` |

`skillOverrides` in `settings.json` turns off individual skills — but **only
user skills**. The docs are explicit: "Plugin skills are not affected by
`skillOverrides`. Manage those through `/plugin` instead." So a plugin is
all-or-nothing: caveman's 3,591 B of descriptions is the price of its mode and
`cavecrew` agents, and 2,180 B of that is skills with no use here (the Caveman
Cloud operations set, and a workflow set that overlaps superpowers'
`systematic-debugging`, `test-driven-development` and `executing-plans`).

Run `/skill-doctor` for per-skill context cost and invocation counts — it
names the skills that have never run and says where to turn each one off.
`claude -p "/skill-doctor"` prints the same report from a fresh session,
which is the only way to see the effect of a settings change.

`skillOverrides` carries 29 entries, nearly all `user-invocable-only`:
hidden from the listing Claude reads every turn, still typeable as a slash
command. Two groups, both measured at 0 invocations by `/skill-doctor`:

- **This repo's own skills** (~1,680 tokens/turn) — they are installed to
  both targets, and they get used on the Copilot side, where skill context
  is free under per-prompt billing. Nothing about Copilot changes.
- **claude.ai sync skills** (~3,010 tokens/turn) — `anthropic-skills:pdf` is
  kept; it has actually run. A deleted synced copy is re-downloaded on the
  next sync, so the override is the durable fix, not deletion.

Both formats work for a synced skill's key, `anthropic-skills:docx` or bare
`docx`; the prefixed form is used here because it matches what
`/skill-doctor` prints. Verify a change by re-running the report, not by
assuming — plugin skills silently ignore these entries.

Per-project `enabledPlugins` exists precisely so global context stays small:
`supabase`, `vercel`, `frontend-design`, `skill-creator`,
`claude-md-management` and `claude-code-setup` are off globally and enabled
in the repos that need them.

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
