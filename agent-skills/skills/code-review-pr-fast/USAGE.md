# code-review-pr-fast — usage

A short chat-only pass over the current branch diff. No report file, no
CodeTour, no command other than `git`.

## When to use

- Mid-work sanity check before committing or pushing.
- A small diff where the full review would cost more than it returns.

Use `code-review-pr` instead when the change is going into a PR, when you
want the change explained as well as reviewed, or when Bamboo specs,
Dockerfiles, Kubernetes manifests or Helm charts are involved.

## Invoking

    quick review
    fast review of my changes
    sanity check this branch

## What it does

Resolves the base the same way `code-review-pr` does, takes
`git diff <base>...HEAD`, reads the whole file where context matters, and
reviews the changed hunks only. No caller search, no configuration-to-code
coupling check, no test analysis — the output says so explicitly at the end,
so nothing is silently skipped.

Findings use the same severity and confidence scales as the full skill, with
the same gates: nothing below Probable is reported, a Blocker must be
Confirmed, and every Major or Blocker states a concrete failure scenario.
Capped at five findings.

## Relationship to code-review-pr

The severity, confidence and suppression rules are read from the installed
`code-review-pr` skill's `references/review-method.md`, so there is one
source of truth. When that skill is not installed, condensed tables inlined
in this skill's `SKILL.md` take over. Installing both is recommended.

## Install

From the repo root:

    python3 agent-skills/install.py --target claude    # mac / Claude Code
    python3 agent-skills/install.py --target copilot   # work / GitHub Copilot
