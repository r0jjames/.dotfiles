---
applyTo: "**"
description: Roj's personal Copilot instructions — apply on every repository, both machines.
---

<!--
SCAFFOLD — intentionally empty. Delete a comment block and write the rule
underneath it. Everything here is sent with every Copilot prompt on this
machine, so keep it short and keep it true.

Why this file earns its keep: Copilot bills one premium request per prompt
you send, not per token. Extra context costs nothing; the retry after a wrong
answer costs a whole request. A rule that prevents one misunderstanding per
session has already paid for itself.

Why it lives in dotfiles rather than a repo: `~/.copilot/instructions/` applies
to every repository without committing anything to a shared work repo, and it
does NOT roam through Settings Sync — so each machine needs it installed.

CONFIDENTIALITY: this file is committed to a personal dotfiles repository.
No employer names, ticket contents, hostnames, internal URLs or architecture
details. Write rules about how you want to be helped, not about what you work
on.

--- Output style -------------------------------------------------------------
How answers should be shaped. For example: cite code as `path:line`; quote
errors verbatim; state assumptions rather than guessing; no refactoring advice
unless asked.

--- Stack conventions --------------------------------------------------------
Idioms and tooling you actually use, so answers do not arrive in the wrong
dialect. Name languages and tools only.

--- Git and safety -----------------------------------------------------------
What must never happen without being asked — commit, push, rebase, force,
delete. Mirror the rules in `claude/CLAUDE.md` so both assistants behave the
same way.

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
