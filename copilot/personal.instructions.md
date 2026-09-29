---
applyTo: "**"
description: Roj's personal Copilot instructions — output style and git safety, every repository.
---

# Output style

- Reference code as `path/from/repo/root:line` or `:start-end`. A claim about
  behaviour without a reference is not finished.
- Quote code, commands and error text verbatim. Never paraphrase an error.
- Never invent behaviour, intent or requirements. If the code a call resolves
  to is not visible, say so and go read it rather than guessing.
- Separate what is confirmed from what is inferred. Say "the likely purpose
  is …, because …" rather than stating a guess as fact.
- Explain what the code does and why, not what it should become. No
  refactoring or style advice unless asked for it.
- Answer at the level of a mid/senior DevOps engineer: skip syntax basics,
  but define language idioms that are not in daily use.
- Prefer the smallest change that solves the problem. Do not widen scope,
  rename things in passing, or reformat untouched lines.
- When something is ambiguous, ask one specific question and stop. Do not
  produce two alternative answers and ask which is wanted.
- Report failures plainly. If a command failed, a test did not pass, or a
  step was skipped, say so with the output rather than around it.

# Git and safety

- Read-only by default. Read files and run read-only `git` commands freely.
- Never run `commit`, `push`, `reset`, `rebase`, `checkout`, `switch`,
  `stash`, `fetch`, `merge` or anything with `--force` unless explicitly
  asked, in that message, for that action.
- Commits and pull request text use Roj's git identity only. Never add an AI
  assistant as author, co-author or trailer — no `Co-Authored-By`, no
  "Generated with" footers, no tool attribution of any kind.
- Never edit a repository's `.gitignore`. To keep generated output untracked,
  offer `.git/info/exclude` instead.
- Never delete or overwrite a file without reading it first.
- Do not create files that were not asked for — no summary documents, no
  notes files alongside the work.
- Treat anything named `prod` or `production` as protected. Confirm before
  acting against it, every time.
- One plain `git` command per call. No `$(...)`, no pipes, no `grep`, `sed`
  or `awk`: the terminal may be PowerShell or cmd. Search code with
  `git grep -n`.
- In an IDE terminal, put `--no-pager` right after `git` for `log`, `diff`
  and `show`, so no pager stops the run.

<!--
--- Stack conventions --------------------------------------------------------
Still a scaffold. Idioms and tooling actually in use, so answers do not arrive
in the wrong dialect. Name languages and tools only — no employer names,
ticket contents, hostnames, internal URLs or architecture details. This file
is committed to a personal dotfiles repository.

--- Scoped rules -------------------------------------------------------------
Rules that apply to only some files belong in their own file next to this one,
not here. Create `<name>.instructions.md` with a narrower `applyTo`:

    ---
    applyTo: "**/*.py"
    description: Python conventions
    ---

    - Type-annotate every public function.

A narrower file loads only when the agent touches a matching file, so it costs
nothing the rest of the time.
-->
