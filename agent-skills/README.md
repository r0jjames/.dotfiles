# agent-skills

Custom agent skills usable by GitHub Copilot (VS Code and JetBrains IDEs) and
Claude Code, plus an installer. One `SKILL.md` format serves every platform.

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
- `prompts/` — Copilot `.prompt.md` slash commands (`/explain-code`,
  `/explain-and-review`, `/create-sb`, `/implement-sb`,
  `/create-implement-sb`). Prompt files are **repo-scoped**: Copilot reads
  them from `<repo>/.github/prompts/`, which is the only place JetBrains
  looks. VS Code additionally reads a user-profile copy, which is why the
  slash commands appear there without seeding a repo. Not used by Claude.
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

Repo scope — seeds `<repo>/.github/skills` and `<repo>/.github/prompts`, the
only scope JetBrains Copilot reads prompt files from:

```bash
python3 install.py --repo .                 # seed the repo you are standing in
python3 install.py --repo . --skills-only   # our skills + prompts, no third-party
python3 install.py --repo . --status        # what a project already carries
python3 install.py --repo . --uninstall prompt:create-sb
python3 install.py --target copilot --repo .   # personal + repo in one run
```

`--repo` writes copies only (never symlinks) and seeds `.github/` only —
`.claude/skills` and `.agents/skills` workspace scopes are left alone.

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
`~/.copilot/skills`, and `%APPDATA%\Code\User\prompts`. Repo scope resolves
to `<repo>\.github\skills` and `<repo>\.github\prompts`.

Team distribution per repo: `python install.py --repo <path>`, then PR the
`.github/` additions. Two things to check before committing them — the three
SB prompts hardcode `SOUNDBOARD_DIR: /c/dev/projects/wr/soundboard`, which is
a personal machine path, and a team repo may already own a prompt file of the
same name (`--dry-run` shows `updated` when a seed would overwrite one). To
keep a seed local instead, `echo .github/ >> .git/info/exclude` — per-repo and
invisible to teammates. Do not add these paths to the global
[`git/ignore`](../git/ignore): `.github/prompts/` is GitHub's own mechanism
for team sharing, and a global rule would suppress intentional additions
everywhere.

## JetBrains (IntelliJ / PyCharm / GoLand)

Copilot reads the two customization kinds from different scopes, which is why
skills and slash commands do not arrive together:

| Kind | Personal scope | Repo scope | JetBrains |
| --- | --- | --- | --- |
| Skills (`SKILL.md`) | `~/.copilot/skills` | `.github/skills/` | both work |
| Prompt files (`.prompt.md`) | VS Code profile only | `.github/prompts/` | repo scope only |

So `~/.copilot/skills` already covers every JetBrains project, but a slash
command like `/create-sb` only exists in a repo that has been seeded. Skills
are also never invoked as `/name` — Copilot loads them from their
`description` when the phrasing matches, so ask for them in plain English.

Setup checklist:

1. GitHub Copilot plugin installed from the JetBrains Marketplace, up to
   date, signed in.
2. **Settings → Languages & Frameworks → GitHub Copilot → Chat → Agent** —
   enable agent mode. Restart the IDE if the toggle has just appeared.
3. Copilot Chat panel → settings gear → **Customizations**. Personal-scope
   skills from `~/.copilot/skills` should be listed. If not, run
   `python install.py --target copilot --skills-only` and reopen the panel.
4. `python install.py --repo . --skills-only --dry-run` in the project, then
   the same without `--dry-run`.
5. Reopen the project. In Copilot Chat **in agent mode**, type `/` — all five
   prompts list as slash commands.

Nothing shows up: confirm the files are at `<project root>/.github/prompts/`
(the folder open in the IDE, not a submodule), that their frontmatter says
`mode: agent`, that chat is in agent mode, and that the plugin is current.

One caveat: `${selection}` in `explain-code.prompt.md` and
`explain-and-review.prompt.md` is a VS Code prompt variable and is not
guaranteed to expand in JetBrains. Both prompts already fall back to asking
which branch, PR, or file you mean.

## Usage

Per-skill guides with copy-paste examples for VS Code, JetBrains IDEs, and
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
