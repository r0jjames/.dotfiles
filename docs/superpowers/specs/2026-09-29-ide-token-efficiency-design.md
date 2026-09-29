# IDE token efficiency for Claude Code and GitHub Copilot

Date: 2026-09-29

## Intent

Reduce what Claude Code and GitHub Copilot cost per unit of work across both
IDEs, without degrading output quality.

Two distinct pains, on two distinct accounts:

- **Copilot Business (work, Windows)** and **Copilot Pro (personal)** — the
  premium request allowance runs out before the month does.
- **Claude Code (personal, macOS and Ubuntu)** — the rolling 5-hour and weekly
  usage windows are hit during normal work.

Success criteria:

1. A measured drop in Claude Code's always-loaded context, taken as a `/context`
   delta between two fresh sessions in this repo.
2. Fewer Copilot premium requests consumed per week of comparable work.
3. No increase in re-prompting or re-work. If item 5 of the Claude section
   (the model default) produces more re-prompting, it reverts.

## The constraint that shapes everything

The two tools bill on opposite axes:

| | Billing unit | Consequence |
| --- | --- | --- |
| Claude Code | tokens of context per turn | shrink what loads per turn |
| Copilot | one premium request per prompt you send, times the model multiplier | grow the context per prompt, so the first answer is right |

Copilot does not bill each autonomous agent iteration inside a single prompt —
only the prompts a human sends. The expensive event is therefore the *retry*
after a wrong answer, not a large context. Copilot configuration in this spec
deliberately adds context in order to remove retries. Claude configuration does
the opposite. Applying one tool's instincts to the other makes both worse.

## Measured baseline

Always-loaded Claude Code surface, measured 2026-09-29 on the macOS machine by
summing `description:` lines in every `SKILL.md` that an enabled plugin or
`~/.claude/skills` contributes, plus the session-start injections:

| Source | Bytes | Loaded |
| --- | --- | --- |
| Plugin skill descriptions (caveman 24, superpowers 15, supabase 2, plus three single-skill plugins) | 7,969 | every session |
| `~/.claude/skills` descriptions (13 skills with a `SKILL.md`) | 5,009 | every session |
| superpowers SessionStart injection (full `using-superpowers` body) | ~3,500 | every session |
| caveman SessionStart block | ~4,000 | every session |
| `autoMode.environment` array in `claude/settings.json` | ~1,900 | every session |
| caveman UserPromptSubmit block | ~250 | every turn |

Roughly 5.5k–6k tokens before Claude reads a single file.

These byte counts are a proxy. The authoritative before/after numbers come from
`/context` and `/usage`, which are interactive commands the user runs; they are
recorded in the results section below.

## Section 1 — Claude Code always-loaded budget

### 1.1 Split `autoMode.environment`

`claude/settings.json` is the user-level settings file, so its
`autoMode.environment` array loads in every repository. Its current content
describes `/Users/roj/Dev/second-brain` specifically: `6-Work/`,
`github.com/r0jjames/ai-context`, and that repo's confidentiality policy. In any
other repository those lines are roughly 480 tokens of inapplicable context.

Keep the org-wide and security-posture lines in `claude/settings.json`. Move the
second-brain-specific lines to `/Users/roj/Dev/second-brain/.claude/settings.json`,
where they apply.

### 1.2 Trim external skills — narrower than first proposed

Initial investigation classified seven entries in `~/.claude/skills` as
unmanaged local additions. That was wrong, and the correction narrows this item
considerably:

- `code-tour`, `acquire-codebase-knowledge` — named in `~/.claude/CLAUDE.md` as
  deliberate. Keep.
- `context-map` — a declared requirement of the repo's own
  `explain-feature-changes` skill (`agent-skills/install.py`, `_REQUIRES`).
  Removing it breaks that chain. Keep.
- `graphify` — named in `~/.claude/CLAUDE.md`, and that mention is load-bearing:
  it is the guard preventing `graphify install` from appending an always-on
  block to the file. Keep.
- `synced` — not a skill. It holds bucket UUID directories and no `SKILL.md`, so
  it contributes nothing to the description budget. Leave untouched.
- `architecture-blueprint-generator` (401-byte description) and
  `add-educational-comments` — genuinely unused, no dependents. Remove.

All of these are installer-managed externals declared in
`agent-skills/install.py` under the `awesome-copilot` source, not stray files.
The removal is therefore a `default: False` flip plus the installer's own
uninstall path, not a manual delete.

Realistic saving: roughly 600 bytes of description, and two fewer near-miss
skill descriptions competing during skill selection. Small. Recorded honestly
rather than dropped, because the selection-noise benefit is real even where the
byte count is not.

### 1.3 Demote occasional plugins to per-project

`~/.claude/CLAUDE.md` already establishes this pattern for heavy plugins
(`vercel`, `supabase`, `frontend-design` disabled globally, enabled per project
through that repo's `.claude/settings.json`). `supabase` is nonetheless still
enabled globally, at 1,654 bytes for two unusually long descriptions.

Set to `false` in `claude/settings.json`, to be enabled per project:
`supabase`, `skill-creator`, `claude-md-management`, `claude-code-setup`.

### 1.4 Keep caveman and superpowers

caveman provides 24 skills for 1,866 bytes of descriptions — the best
weight-to-value ratio in the set, and its output compression offsets its own
input cost. superpowers is heavier (3,372 bytes plus a ~3,500-byte SessionStart
injection) but it is the workflow actually in use. No change to either; the cost
is now documented.

### 1.5 Model default: Opus to Sonnet

`claude/settings.json` currently sets `model: opus` with `effortLevel: high`.
Thinking tokens bill as output tokens, so this is the top of both scales.

Change `model` to `sonnet`. Keep `effortLevel: high`. Escalate to Opus with
`/model` for architectural and multi-step debugging work, per Anthropic's own
guidance that Sonnet handles most coding tasks and Opus should be reserved for
complex architectural decisions.

This is the only change in this spec that trades quality for cost. It is
deliberately the most reversible one: `/model` is a single command, and the
setting is one line.

## Section 2 — VS Code and Copilot

`lib/tools/vscode.py` copies a single `settings.json` to every platform; only
`extensions.txt` supports `@macos`/`@linux`/`@windows` tags. Copilot and Claude
keys therefore share one file. This is fine: each tool's keys are inert without
its extension installed, and a per-platform overlay would mean new merge logic
in `vscode.py` plus tests for no runtime benefit.

### 2.1 Settings added to `vscode/settings.json`

| Key | Value | Rationale |
| --- | --- | --- |
| `github.copilot.chat.codesearch.enabled` | `true` | Default `false`. Lets `#codebase` discover relevant files automatically. Better first answer; free under per-prompt billing. |
| `github.copilot.chat.editor.temporalContext.enabled` | `true` | Default `false`, experimental. Attaches recently viewed and edited files to inline chat. |
| `github.copilot.chat.codeGeneration.useInstructionFiles` | `true` | Already the default; pinned so `.github/copilot-instructions.md` is reliably picked up. |
| `chat.includeApplyingInstructions` | `true` | Already the default; pinned so `applyTo`-matched `.instructions.md` files attach automatically. |
| `github.copilot.chat.summarizeAgentConversationHistory.enabled` | `true` | Already the default; pinned. Summarizes rather than dropping context when the window fills. |

### 2.2 Deliberately unchanged

- `chat.agent.maxRequests` stays at its default of 25. It caps iterations
  *inside* one billed prompt, so lowering it truncates work and forces a second
  prompt — the opposite of the goal.
- `github.copilot.nextEditSuggestions.enabled` stays `true`. Completions and
  next edit suggestions are not premium-request features; they are free, and
  they displace chat prompts that would not be.
- `chat.tools.terminal.autoApprove` and `chat.tools.edits.autoApprove` are not
  set. They would reduce interruptions, but auto-approving terminal commands on
  a work machine is a security trade that a dotfiles default should not make.
- `github.copilot.chat.virtualTools.threshold` is documented in
  `vscode/README.md` as an on-demand remedy rather than shipped as a default.
  It auto-groups tools to stay under the hard limit of 128 tools per request,
  but VS Code's documentation does not state its default value, and picking a
  number blind risks grouping tools that did not need grouping. Set it if and
  when the 128-tool error appears.

### 2.3 Behavioural rules that outweigh the settings

1. Do not run Copilot code review casually. It costs 13 premium requests per
   review — the single largest line item available.
2. Default to an included model for routine work and switch to a premium model
   only for architecture and debugging.

Note on billing: GitHub moved from request-based to usage-based billing on
2026-06-01, and model multipliers are now legacy (Pro and Pro+ annual plans
only). The direction of rule 2 holds under both regimes. Plan allowances are not
quoted here because GitHub's current documentation does not state them cleanly
post-migration; check the live figure in GitHub billing settings.

### 2.4 Instruction file template

Add `vscode/copilot-instructions.template.md`, a deliberately short template to
copy into a project's `.github/`. GitHub's guidance is to keep instruction files
concise and focused on what cannot be inferred from the code, with `applyTo`
scoping for language-specific rules. This is the primary retry-killer, and
retries are what the premium allowance actually pays for.

The template is not installed by `install.py`; it is copied per project by hand.

### 2.5 Extension tag correction

`vscode/extensions.txt` currently tags `github.copilot` and
`github.copilot-chat` as `@windows`. With Copilot Pro on the personal machines
and the IntelliJ Copilot plugin already installed on macOS, that is wrong.
Both become untagged, so they install on every platform.

## Section 3 — JetBrains

Investigation removed this section's main proposed artifact.
`~/Library/Application Support/JetBrains/<IDE>/options/github-copilot.xml` is
plugin-owned state, not a settings surface: it holds `signinNotificationShown`,
`nesDefaultAppliedForFreePlan`, `legacyXdgConfigMigrated`, `terminalRulesVersion`
and similar flags. The only genuine setting is `enableNextEditSuggestions`.
Shipping this file from dotfiles would overwrite authentication and migration
state that the plugin maintains. It is therefore not managed here.

What JetBrains gets instead:

- `jetbrains/plugins.txt` gains `github-copilot-intellij` (already installed on
  IdeaIC2025.2 and IntelliJIdea2026.2, previously unrecorded) and the Claude Code
  plugin id (not currently installed anywhere).
- `jetbrains/README.md` gains a checklist of the settings that exist only in the
  UI: Tools → GitHub Copilot → Completions for per-language toggles, and the chat
  model picker.
- A note that the installed `fullLine` plugin (JetBrains Full Line Code
  Completion) is **not** a token lever. It runs locally, and Copilot completions
  are not premium-billed either. It is documented only because it conflicts with
  Copilot completions, which is a quality and latency choice.
- Claude Code in JetBrains needs no new configuration. The plugin reads the same
  `~/.claude/settings.json` that Section 1 covers.

Separately, the installed `mcpserver` plugin and the configured `MCP_DOCKER`
server warrant a `/mcp` audit. Claude Code defers MCP tool definitions by
default, so only names and server instructions enter context — low cost, but
nonzero per configured server.

## Files touched

| File | Change |
| --- | --- |
| `claude/settings.json` | `model` → `sonnet`; `supabase`, `skill-creator`, `claude-md-management`, `claude-code-setup` → `false`; `autoMode.environment` split |
| `~/Dev/second-brain/.claude/settings.json` | receives the second-brain-specific `autoMode.environment` lines |
| `agent-skills/install.py` | `architecture-blueprint-generator` and `add-educational-comments` → `default: False` |
| `vscode/settings.json` | five Copilot keys added |
| `vscode/extensions.txt` | Copilot entries untagged |
| `vscode/copilot-instructions.template.md` | new template |
| `jetbrains/plugins.txt` | Copilot and Claude Code plugin ids |
| `jetbrains/README.md` | UI settings checklist, fullLine note |
| `claude/README.md`, `vscode/README.md` | one routing table each |

## Install mechanics

Two different mechanisms, worth stating because they behave differently:

- `claude/` **symlinks** into `~/.claude` on macOS and Linux, so repository edits
  take effect immediately. On Windows and Git Bash they are copies, so
  `./install.py install claude` must be re-run.
- `vscode/` **copies** always, on every platform, because VS Code Settings Sync
  owns the installed file and would otherwise write back into the repository.
  Every settings change needs `./install.py install vscode`.

## Testing

Extend the existing suites, following their established patterns:

- `tests/test_vscode.py` — `settings.json` parses as JSON; the Copilot keys are
  present with the expected values; `parse_extensions` returns `github.copilot`
  on all three platforms, where it previously returned it only for `gitbash`.
- `tests/test_jetbrains.py` — the Copilot plugin id is listed, mirroring the
  existing `test_vscode_keymap_plugin_listed`.
- `tests/test_claude.py` — `settings.json` parses; `autoMode.environment`
  contains no `second-brain` or `6-Work` strings.

`python -m pytest tests/` must pass before committing.

## Sequencing

1. Record the baseline: `/context` and `/usage` in a fresh session in this repo,
   and the premium request counter in GitHub billing settings.
2. Section 1 changes (Claude).
3. Section 2 changes (VS Code and Copilot), then `./install.py install vscode`.
4. Section 3 changes (JetBrains documentation and plugin list).
5. Re-measure `/context` in a fresh session; compare. Re-check the Copilot
   counter after a full week of comparable work.

## Risks and how they are handled

- **Sonnet default degrades output.** The only genuine quality trade here. There
  is no rigorous A/B available, so the guard is structural: `effortLevel: high`
  stays, plan mode stays, and reverting is one line plus one `/model` command.
  More re-prompting on personal projects is the signal to revert.
- **Disabling a plugin that turns out to be needed.** Each demoted plugin is
  re-enabled per project, which is the pattern `~/.claude/CLAUDE.md` already
  documents for `vercel` and `frontend-design`.
- **Copilot settings landing on machines that lack the extension.** Inert. Keys
  for an uninstalled extension are ignored.
- **Removing a skill with a hidden dependent.** Addressed by checking
  `agent-skills/install.py` requirements before removal; `context-map` was
  retained precisely because that check caught it.

## Results

To be filled in during implementation.

| Measurement | Before | After |
| --- | --- | --- |
| `/context` always-loaded, fresh session in `.dotfiles` | | |
| `/usage` 7-day | | |
| Copilot premium requests, one week | | |
