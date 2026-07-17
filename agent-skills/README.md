# agent-skills

Custom agent skills usable by both GitHub Copilot and Claude Code, plus an
installer. One `SKILL.md` format serves both platforms.

## Layout

- `skills/explain-logic/` — guided code-comprehension walkthroughs
  (PR/branch diffs, files, functions) with language lenses.
- `prompts/` — Copilot/VS Code `.prompt.md` slash commands
  (`/explain-code`, `/explain-and-review`). Not used by Claude.
- `install.py` — cross-platform installer (Python >= 3.8, stdlib only).

## Install

```bash
python3 install.py --target claude    # home: symlinks into ~/.claude/skills
python3 install.py --target copilot   # work: copies into ~/.copilot/skills
python3 install.py --target both
python3 install.py                    # interactive menu
```

Flags: `--dry-run` (print planned actions), `--skills-only` (skip the
community-skill fetch — offline or behind a proxy).

Also fetched into `~/.agent-skills-cache/` and installed/updated in place
(missing = install, present = update, unchanged = up to date):

- From `github/awesome-copilot`: code-tour, acquire-codebase-knowledge,
  context-map, architecture-blueprint-generator, add-educational-comments.
- From `juliusbrussee/caveman`: the caveman terse-output skill (token
  saver). explain-logic points at it for terse mode.

`./install.sh agent-skills` from the repo root runs the Claude install
(custom skills only) as part of normal dotfiles setup.

## Work VDI (Windows, Git Bash)

1. Copy this folder over (or clone the repo).
2. `python3 install.py --target copilot --dry-run` — sanity-check paths.
3. `python3 install.py --target copilot`
4. If the proxy blocks the clone, follow the printed ZIP fallback, or use
   `--skills-only`.

Team distribution per repo: copy `skills/*` into the repo's
`.github/skills/` and `prompts/*` into `.github/prompts/`, then PR.

## Usage (VS Code / IntelliJ Copilot chat, agent mode)

VS Code gets the `/explain-code` and `/explain-and-review` slash commands
(from `prompts/`). IntelliJ has no prompt files — use the plain-English
prompts; the skill triggers on the phrasing. If a skill doesn't trigger,
name it once ("Use the explain-logic skill to ...") — after one explicit
use it picks up reliably.

Copy-paste prompts:

| Goal | VS Code | IntelliJ (or any chat) |
|---|---|---|
| Understand a feature branch | `/explain-code the changes in this branch vs main` | `Use the explain-logic skill: walk me through the changes in this branch vs main` |
| Understand a PR | `/explain-code PR #142` | `Use the explain-logic skill: explain PR #142` |
| Understand a file | `/explain-code src/foo/bar.py` | `Use the explain-logic skill: explain the logic in src/foo/bar.py` |
| Understand a selection | select code → `/explain-code` | select code → `Explain the logic in this selection step by step` |
| Understand + flag risks | `/explain-and-review PR #142` | `Explain and review PR #142 — walkthrough first, then flag anything risky` |
| New repo, big picture first | `/explain-code — onboard me to this repo first, then explain branch feature/x` | `Onboard me to this repo first, then explain branch feature/x` |
| Save as replayable tour | add `then create a code tour` to any prompt | same phrasing (needs CodeTour extension in VS Code) |
| Terse output (save tokens) | add `use caveman mode` to any prompt | `Caveman mode: explain the changes in this branch vs main` |

What the explain flow does: pulls the real diff → reads surrounding code,
callers, and tests → explains Concept → Code flow → Why → Gotchas, with
the matching language lens (Java / Python / Go / shell / Bamboo API).
`/explain-and-review` adds a clearly separated second phase rating findings
🔴 likely bug / 🟡 risky / 🟢 style.

## Tests

```bash
cd agent-skills && python3 -m unittest test_install -v
```
