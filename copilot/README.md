# copilot

Personal GitHub Copilot instruction files. Installed to
`~/.copilot/instructions/`, which every Copilot surface reads: the CLI, VS Code
and JetBrains.

Copilot Business on the work Windows machine, Copilot Pro personally. Both read
the same files.

## Files

- [`personal.instructions.md`](personal.instructions.md) — applies to every
  repository (`applyTo: "**"`). Currently a commented scaffold; fill it in.

Add more files beside it. Every `*.instructions.md` in this directory is
installed; anything else (this README) is ignored.

## Run

```sh
./install.py install copilot
```

macOS and Linux symlink, so an edit here is live immediately. Windows and Git
Bash copy — re-run after editing.

## Why here and not in a repo

Three reasons this beats `.github/copilot-instructions.md`:

1. It applies to **every** repository, including work repositories you should
   not be committing personal preferences into.
2. VS Code's documentation states that Agent Host folders such as
   `~/.copilot/instructions` **do not roam through Settings Sync**. Dotfiles is
   the only thing that gets them onto a second machine.
3. Per-repo instructions still win where they exist, so a project that ships
   its own `.github/copilot-instructions.md` is unaffected.

A per-project file is still the right home for project-specific rules — see
[`../vscode/copilot-instructions.template.md`](../vscode/copilot-instructions.template.md).

## Why instructions are the lever that matters

Copilot bills **one premium request per prompt you send**, times the model
multiplier. Autonomous steps the agent takes inside a single prompt are not
billed separately. So the expensive event is the **retry** after a wrong
answer, not a large context.

That inverts the usual advice. Extra context per prompt is free here; a rule
that prevents one misunderstanding per session has already paid for itself.
The related VS Code settings in [`../vscode/settings.json`](../vscode/settings.json)
deliberately *widen* context for the same reason.

Two habits still outweigh every file in this directory:

- **Do not run Copilot code review casually — 13 premium requests per review.**
- **Default to an included model**; reach for a premium one only for
  architecture and debugging.

## Confidentiality

These files are committed to a personal dotfiles repository. No employer
names, ticket contents, hostnames, internal URLs or architecture details.
Write rules about how you want to be helped, not about what you work on.

## Scoping

`applyTo` is a glob relative to the workspace root. A narrower file loads only
when the agent touches a matching file, so it costs nothing the rest of the
time:

```markdown
---
applyTo: "**/*.py"
description: Python conventions
---

- Type-annotate every public function.
```

`description` is what the agent reads when deciding whether to load the file,
so make it specific.

## Not managed here

- **The Copilot extension** — ships built into VS Code from 1.139
  (`GitHub.copilot-chat` 0.67.0). See [`../vscode/README.md`](../vscode/README.md).
- **VS Code Copilot settings** — [`../vscode/settings.json`](../vscode/settings.json),
  since they are VS Code-specific.
- **JetBrains Copilot settings** — UI-only; its `github-copilot.xml` holds
  plugin-owned auth state, not settings. See
  [`../jetbrains/README.md`](../jetbrains/README.md).
- **Prompt files and skills** — [`../agent-skills/`](../agent-skills/README.md).

## Uninstall

```sh
./install.py uninstall copilot
```

Removes only files identical to the repo copy; anything edited in place is
left alone.
