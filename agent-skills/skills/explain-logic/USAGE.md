# Using the explain-logic skill

Guided, step-by-step code comprehension: PR/branch diffs, files, functions —
explained as Concept → Code flow → Why → Gotchas, with the matching language
lens (Java / Python / Go / shell / Bamboo API).

## Commands per platform

VS Code gets the `/explain-code` and `/explain-and-review` slash commands
(from `prompts/`). IntelliJ has no prompt files — use the plain-English
prompts; the skill triggers on the phrasing. If a skill doesn't trigger,
name it once ("Use the explain-logic skill to ...") — after one explicit
use it picks up reliably. Claude Code triggers on the same phrasing.

| Goal | VS Code | IntelliJ / Claude Code |
|---|---|---|
| Understand a feature branch | `/explain-code the changes in this branch vs main` | `Use the explain-logic skill: walk me through the changes in this branch vs main` |
| Understand a PR | `/explain-code PR #142` | `Use the explain-logic skill: explain PR #142` |
| Understand a file | `/explain-code src/foo/bar.py` | `Use the explain-logic skill: explain the logic in src/foo/bar.py` |
| Understand a selection | select code → `/explain-code` | select code → `Explain the logic in this selection step by step` |
| Understand + flag risks | `/explain-and-review PR #142` | `Explain and review PR #142 — walkthrough first, then flag anything risky` |
| New repo, big picture first | `/explain-code — onboard me to this repo first, then explain branch feature/x` | `Onboard me to this repo first, then explain branch feature/x` |
| Save as replayable tour | add `then create a code tour` to any prompt | same phrasing (needs CodeTour extension in VS Code) |
| Terse output (save tokens) | add `use caveman mode` to any prompt | `Caveman mode: explain the changes in this branch vs main` |

## Worked example

`/explain-and-review PR #142` pulls the real diff, reads surrounding code,
callers, and tests, explains the change step by step, then a clearly
separated review phase rates findings 🔴 likely bug / 🟡 risky / 🟢 style.
