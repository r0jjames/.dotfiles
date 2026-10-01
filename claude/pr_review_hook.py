#!/usr/bin/env python3
"""Claude Code PostToolUse hook: auto-review PRs Claude opens.

After a Bash call that ran `gh pr create` and printed a new PR URL, if the
repo owner is in PR_REVIEW_OWNERS, tell Claude to review the PR by reading
the roj-review-pr-comment skill file. With PR_REVIEW_COPILOT=1, also request a
Copilot review.

The first github.com PR URL in the output is used, so a command that chains
`gh pr create` with another command printing PR URLs may pick the wrong one.

Always exits 0 with no output unless it is triggering a review — a hook
must never block or break the tool call it follows.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from typing import Optional, Tuple

SKILL_PATH = "~/.claude/skills/roj-review-pr-comment/SKILL.md"
COPILOT_BOT = "copilot-pull-request-reviewer[bot]"
PR_URL = re.compile(r"https://github\.com/([\w.-]+)/([\w.-]+)/pull/(\d+)")


def parse_payload(raw: str) -> Tuple[str, str]:
    """(command, output) from the hook payload; ("", "") if malformed."""
    try:
        data = json.loads(raw)
    except ValueError:
        return "", ""
    if not isinstance(data, dict):
        return "", ""
    tool_input = data.get("tool_input")
    command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""
    response = data.get("tool_response")
    if isinstance(response, dict):
        # stdout only: gh pr create prints the new URL there, and prints an
        # *existing* PR's URL to stderr when the branch already has one.
        output = str(response.get("stdout") or "")
    else:
        output = str(response or "")
    return str(command), output


def find_pr(command: str, output: str) -> Optional[Tuple[str, str, int]]:
    """(owner, repo, number) when the command created a PR, else None."""
    if "gh pr create" not in command:
        return None
    match = PR_URL.search(output)
    if match is None:
        return None
    return match.group(1), match.group(2), int(match.group(3))


def owner_allowed(owner: str, owners_env: str) -> bool:
    allowed = {o.strip().lower() for o in owners_env.split(",") if o.strip()}
    return owner.lower() in allowed


def request_copilot(owner: str, repo: str, number: int) -> bool:
    """gh 2.64 does not document @copilot for --add-reviewer; use REST."""
    try:
        result = subprocess.run(
            ["gh", "api", "-X", "POST",
             f"repos/{owner}/{repo}/pulls/{number}/requested_reviewers",
             "-f", f"reviewers[]={COPILOT_BOT}"],
            capture_output=True, text=True, timeout=30)
    except (OSError, subprocess.SubprocessError):
        return False
    return result.returncode == 0


def build_output(url: str, copilot: Optional[bool]) -> dict:
    context = (f"A PR was just opened at {url} in an allowlisted repository. "
               f"Review it now: read {SKILL_PATH} and follow it for this PR.")
    if copilot is True:
        context += " A Copilot review was also requested."
    elif copilot is False:
        context += (" Requesting a Copilot review failed; continue with the "
                    "Claude review and mention it in the final report.")
    return {"hookSpecificOutput": {"hookEventName": "PostToolUse",
                                   "additionalContext": context}}


def main(stdin=sys.stdin, out=sys.stdout, env=os.environ) -> int:
    pr = find_pr(*parse_payload(stdin.read()))
    if pr is None:
        return 0
    owner, repo, number = pr
    if not owner_allowed(owner, env.get("PR_REVIEW_OWNERS", "")):
        return 0
    copilot = (request_copilot(owner, repo, number)
               if env.get("PR_REVIEW_COPILOT") == "1" else None)
    url = f"https://github.com/{owner}/{repo}/pull/{number}"
    out.write(json.dumps(build_output(url, copilot)) + "\n")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # never break the tool call this hook follows
        sys.exit(0)
