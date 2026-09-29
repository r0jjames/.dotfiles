# Copilot instructions template

Copy this file to `.github/copilot-instructions.md` in a project and fill it
in. VS Code picks it up automatically
(`github.copilot.chat.codeGeneration.useInstructionFiles`, pinned `true` in
`vscode/settings.json`).

**Why this file pays for itself.** Copilot bills one premium request per prompt
you send. Every "no, I meant..." follow-up is another request. Instructions that
prevent one wrong answer per session pay for themselves immediately.

**Keep it short.** GitHub's guidance is to record only what cannot be inferred
from the code. Architecture, boundaries and conventions qualify. Restating what
any reader can see in the source does not, and a long file crowds out the
context that would have produced a better answer.

For rules that apply only to some files, prefer a scoped
`.github/instructions/<name>.instructions.md` with an `applyTo` pattern over
adding to the project-wide file. VS Code attaches those automatically when the
agent touches a matching file (`chat.includeApplyingInstructions`).

---

## Template — copy from here down

```markdown
# <project name>

<One or two sentences: what this project is and who uses it.>

## Architecture

- <Major components and how they talk to each other.>
- <Module boundaries that are not obvious from the directory layout.>

## Conventions

- <Naming, error handling, logging — only where the codebase is consistent
  and a newcomer would guess wrong.>
- <Testing: framework, where tests live, what a test is expected to cover.>

## Constraints

- <Things that look reasonable but are wrong here, and why.>
- <External systems that cannot be called from tests.>

## Commands

- Build: `<command>`
- Test: `<command>`
- Lint: `<command>`
```

---

## Scoped instructions example

`.github/instructions/python.instructions.md`:

```markdown
---
applyTo: "**/*.py"
description: Python conventions for this project
---

- Type-annotate every public function.
- Prefer `pathlib` over `os.path`.
- Tests use pytest; no unittest.TestCase subclasses.
```

The `description` is what the agent reads when deciding whether to load the
file, so make it specific.
