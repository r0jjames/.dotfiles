# git

The **global** git excludes file — patterns that should never be committed in
any repository, kept in one place instead of edited into each repo's
`.gitignore`.

## Run

```sh
./install.py install git
```

## What it does

- Symlinks [`ignore`](ignore) to `~/.config/git/ignore`
  (Windows/Git Bash: copies — re-run after editing)
- Points `core.excludesFile` at it, but **only when that setting is unset**.
  Pointing elsewhere already? The installer says so and leaves it alone.

## What it ignores

| Pattern | Why |
|---|---|
| `**/.claude/settings.local.json` | Per-machine Claude Code settings, never shared |
| `.tours/` | CodeTour walkthroughs written by the agent skills — a personal reading aid, not a team artifact |

The `.tours/` entry pairs with the walkthrough skills (`explain-logic`,
`investigate-issue`, `soundboarding`, `acquire-codebase-knowledge`), which
write a `.tour` file at the end of a run. `vsls-contrib.codetour` in
[`vscode/extensions.txt`](../vscode/extensions.txt) opens them.

## Uninstall

```sh
./install.py uninstall git
```

Removes the link (restoring any `.bak-*` backup) and leaves `core.excludesFile`
alone — unset it yourself if you want it gone:

```sh
git config --global --unset core.excludesFile
```

## Not managed here

Identity (`user.name`, `user.email`), aliases and other `~/.gitconfig`
settings stay machine-local — the work machine and this one differ.
