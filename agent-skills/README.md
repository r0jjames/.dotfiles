# agent-skills

Custom agent skills usable by both GitHub Copilot and Claude Code, plus an
installer. One `SKILL.md` format serves both platforms.

## Layout

- `skills/explain-logic/` — guided code-comprehension walkthroughs
  (PR/branch diffs, files, functions) with language lenses.
- `skills/soundboarding/` — story → SB document → task-by-task
  implementation workflow (bundled `SB-template.md` + examples).
- `prompts/` — Copilot/VS Code `.prompt.md` slash commands
  (`/explain-code`, `/explain-and-review`, `/create-sb`, `/implement-sb`,
  `/create-implement-sb`). Not used by Claude.
- `install.py` — cross-platform installer (Python >= 3.8, stdlib only).

## Install

```bash
python3 install.py --target claude    # home: symlinks into ~/.claude/skills
python3 install.py --target copilot   # work: copies into ~/.copilot/skills
python3 install.py --target both
python3 install.py                    # interactive: pick target + items
```

Flags: `--dry-run` (print planned actions), `--skills-only` (skip the
community-skill fetch — offline or behind a proxy).

Interactive runs (no flags) show an item picker: toggle individual skills,
prompt files, and community skills by number, `a` for all, enter to
confirm. Flag runs install everything, unchanged.

Also fetched into `~/.agent-skills-cache/` and installed/updated in place
(missing = install, present = update, unchanged = up to date):

- From `github/awesome-copilot`: code-tour, acquire-codebase-knowledge,
  context-map, architecture-blueprint-generator, add-educational-comments.
- From `juliusbrussee/caveman`: the caveman terse-output skill (token
  saver). explain-logic points at it for terse mode.

`./install.py install agent-skills` from the repo root runs the Claude
install (custom skills only) as part of normal dotfiles setup.

## Work VDI (Windows, Git Bash)

1. Copy this folder over (or clone the repo).
2. `python3 install.py --target copilot --dry-run` — sanity-check paths.
3. `python3 install.py --target copilot`
4. If the proxy blocks the clone, follow the printed ZIP fallback, or use
   `--skills-only`.

Team distribution per repo: copy `skills/*` into the repo's
`.github/skills/` and `prompts/*` into `.github/prompts/`, then PR.

## Usage

Per-skill guides with copy-paste examples for VS Code, IntelliJ, and
Claude Code:

- [explain-logic](skills/explain-logic/USAGE.md)
- [soundboarding](skills/soundboarding/USAGE.md)
- [community skills](docs/community-skills.md) (code-tour, caveman, ...)

## Tests

```bash
cd agent-skills && python3 -m unittest test_install -v
```
