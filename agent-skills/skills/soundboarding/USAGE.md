# Using the soundboarding skill

Turns a user story (`LISA-<id>.md`) into a soundboarding (SB) document with
codebase-investigated core tasks, then implements the SB task by task with a
review stop after every task. Never touches git — you review and commit
manually.

## When to use

- A user story needs refinement into concrete, investigated tasks before
  the team commits to it → **create**.
- A refined SB document is ready to execute → **implement**.
- Solo story, no team refinement needed → **create + implement** chained.

## Commands per platform

| Flow | VS Code Copilot (slash) | IntelliJ Copilot / any chat | Claude Code |
|---|---|---|---|
| Create SB | `/create-sb LISA-110278.md` | `Use the soundboarding skill: create an SB from LISA-110278.md` | `create an SB document from LISA-110278.md` |
| Implement SB | `/implement-sb SB-LISA-110278` | `Use the soundboarding skill: implement SB-LISA-110278` | `implement SB-LISA-110278` |
| Both chained | `/create-implement-sb LISA-110278.md` | `Use the soundboarding skill: create and implement LISA-110278.md` | `create and implement an SB from LISA-110278.md` |

Paths default to the work layout (`/c/dev/projects/wr/soundboard`,
`/c/dev/projects`). Override by saying so, e.g.
`create an SB from story.md — soundboard dir is ~/Dev/soundboard`.

## Worked example

Story input: [`examples/LISA-110278.md`](examples/LISA-110278.md) — upgrade
Bamboo API to v12.1.6 and verify agents/plans still work.

1. `/create-sb LISA-110278.md` — the skill reads the story, finds the
   impacted repos under the projects root, records exact current versions
   from the POMs and config files it can read, and writes
   `SB-LISA-110278.md` following `SB-template.md`. Unverifiable claims land
   in Questions, not in Core tasks. Output shape:
   [`examples/sb-LISA-110278.md`](examples/sb-LISA-110278.md).
2. Team refines the SB (acceptance criteria, task list, testing table).
3. From the repo where the work happens: `/implement-sb SB-LISA-110278` —
   executes core tasks one at a time, stops after each for
   approve/revise/skip, ticks checkboxes in the SB file, fills the Testing
   table Log column with real command results.
4. You review the working tree and commit manually.
