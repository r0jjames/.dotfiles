# agent-skills

Custom agent skills usable by both GitHub Copilot and Claude Code, plus an
installer. One `SKILL.md` format serves both platforms.

## Layout

- `skills/explain-logic/` — guided code-comprehension walkthroughs
  (PR/branch diffs, files, functions) with language lenses.
- `skills/soundboarding/` — story → SB document → task-by-task
  implementation workflow (bundled `SB-template.md` + examples).
- `skills/interview-prep/` — DevOps interview doc generator from a CV
  (vault-aware, bundled calibration references).
- `skills/investigate-issue/` — problem `.md` in, validated root cause +
  fix-steps `-investigation.md` out (Bamboo plans/agents, Java, Python,
  Bash, Go, Docker, k8s).
- `prompts/` — Copilot/VS Code `.prompt.md` slash commands
  (`/explain-code`, `/explain-and-review`, `/create-sb`, `/implement-sb`,
  `/create-implement-sb`). Not used by Claude.
- `install.py` — installer for macOS, Linux and Windows/Git Bash
  (Python >= 3.8, stdlib only).

`explain-logic`, `soundboarding` and `investigate-issue` each end a run by
writing a CodeTour file into `.tours/` in the repo they worked on (chaining to
the community `code-tour` skill), skipping only trivial single-file cases. The
[`git`](../git/README.md) tool keeps `.tours/` out of every repository, and
`vsls-contrib.codetour` in [`vscode/extensions.txt`](../vscode/extensions.txt)
opens the files.

## Install

```bash
python3 install.py --target claude    # home: symlinks into ~/.claude/skills
python3 install.py --target copilot   # work: copies into ~/.copilot/skills
python3 install.py --target both
python3 install.py                    # interactive: pick target + items
python3 install.py --status                      # what is installed where + conflicts
python3 install.py --uninstall caveman --target copilot
python3 install.py --uninstall prompt:create-sb --target copilot
```

Flags: `--dry-run` (print planned actions), `--skills-only` (skip the
community-skill fetch — offline or behind a proxy), `--force` (bypass unknown-name
checks on uninstall).

Interactive runs (no flags) show an item picker: toggle individual skills,
prompt files, and community skills by number, `a` for all, enter to
confirm. Flag runs install custom skills, prompts, and the default community set; cherry-picks are interactive-only. Interactive picker tags items
as `[installed]`, `[update]`, or `[conflict]`.

Community skills are fetched into `~/.agent-skills-cache/` and installed/updated
in place (missing = install, present = update, unchanged = up to date):

**Default (both targets, unless noted):**
- From `github/awesome-copilot`: code-tour, acquire-codebase-knowledge,
  context-map, architecture-blueprint-generator, add-educational-comments.
- From `juliusbrussee/caveman`: caveman terse-output skill (Copilot only; Claude
  uses the caveman plugin). explain-logic points at it for terse mode.
- From `addyosmani/agent-skills`: debugging-and-error-recovery (Copilot only;
  Claude uses superpowers:systematic-debugging). investigate-issue chains it
  when present.

**Cherry-picks (interactive mode only, default unchecked):**
- From `addyosmani/agent-skills`: observability-and-instrumentation,
  ci-cd-and-automation, security-and-hardening, deprecation-and-migration.
- From `anthropics/skills`: pdf, docx, pptx, xlsx.

`./install.py install agent-skills` from the repo root runs the custom-skill
install (no community fetch) as part of normal dotfiles setup — Claude only on
macOS/Linux, **both** Claude and Copilot on Windows (Git Bash).

## Work VDI (Windows, Git Bash)

Run everything with `python` (Git Bash has no `python3` unless you alias it).

1. Copy this folder over (or clone the repo).
2. `python install.py --target both --dry-run` — sanity-check paths.
3. `python install.py --status` — check what's currently installed.
4. `python install.py --target both` — or `python install.py` for the
   interactive picker (recommended: it also offers the community skills and
   the VS Code prompt files).
5. `python install.py --status` — verify new installs.
6. If the proxy blocks the clone, follow the printed ZIP fallback, or use
   `--skills-only`.

From the repo root, `python install.py install agent-skills` does steps 1–4
for the custom skills only.

**Symlinks on Windows** need Developer Mode or an admin shell. Without them the
installer detects this up front, prints `symlinks unsupported in <dir> —
installing copies`, and installs copies to both targets instead. Copies are
snapshots: **re-run the installer after editing a skill** to refresh them.
`--status` flags any leftover `<skill>.bak` directory from an older run — delete
those, the agents load them as extra skills.

Paths on Windows resolve under `%USERPROFILE%`: `~/.claude/skills`,
`~/.copilot/skills`, and `%APPDATA%\Code\User\prompts`.

Team distribution per repo: copy `skills/*` into the repo's
`.github/skills/` and `prompts/*` into `.github/prompts/`, then PR.

## Usage

Per-skill guides with copy-paste examples for VS Code, IntelliJ, and
Claude Code:

- [explain-logic](skills/explain-logic/USAGE.md)
- [soundboarding](skills/soundboarding/USAGE.md)
- [interview-prep](skills/interview-prep/USAGE.md)
- [investigate-issue](skills/investigate-issue/USAGE.md)
- [community skills](docs/community-skills.md) (code-tour, caveman, ...)

## Tests

```bash
cd agent-skills && python3 -m unittest test_install -v
```
