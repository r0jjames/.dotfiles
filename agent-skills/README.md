# agent-skills

Custom agent skills usable by both GitHub Copilot and Claude Code, plus an
installer. One `SKILL.md` format serves both platforms.

## Layout

- `skills/explain-logic/` — guided code-comprehension walkthroughs
  (PR/branch diffs, files, functions) with language lenses.
- `skills/caveman-mode/` — portable terse-output mode (token saver).
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

Also fetched (Copilot community catalog, sparse-cloned into
`~/.agent-skills-cache/`): code-tour, acquire-codebase-knowledge,
context-map, architecture-blueprint-generator, add-educational-comments.

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

## Tests

```bash
cd agent-skills && python3 -m unittest test_install -v
```
