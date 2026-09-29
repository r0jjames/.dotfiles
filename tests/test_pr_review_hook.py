# tests/test_pr_review_hook.py
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import unittest
from pathlib import Path
from unittest import mock

_PATH = Path(__file__).resolve().parents[1] / "claude" / "pr_review_hook.py"
_spec = importlib.util.spec_from_file_location("pr_review_hook", _PATH)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)

URL = "https://github.com/r0jjames/demo/pull/7"


def payload(command="gh pr create --fill", stdout=URL + "\n", response=None):
    if response is None:
        response = {"stdout": stdout, "stderr": "", "interrupted": False}
    return json.dumps({"hook_event_name": "PostToolUse", "tool_name": "Bash",
                       "tool_input": {"command": command},
                       "tool_response": response})


def run(raw, owners="r0jjames", copilot="0"):
    out = io.StringIO()
    code = hook.main(io.StringIO(raw), out,
                     {"PR_REVIEW_OWNERS": owners, "PR_REVIEW_COPILOT": copilot})
    return code, out.getvalue()


class TriggerTest(unittest.TestCase):
    def test_create_with_allowed_owner_emits_context(self):
        code, out = run(payload())
        self.assertEqual(code, 0)
        data = json.loads(out)["hookSpecificOutput"]
        self.assertEqual(data["hookEventName"], "PostToolUse")
        self.assertIn(URL, data["additionalContext"])
        self.assertIn(hook.SKILL_PATH, data["additionalContext"])

    def test_disallowed_owner_is_silent(self):
        self.assertEqual(run(payload(), owners="someone-else"), (0, ""))

    def test_other_command_is_silent(self):
        self.assertEqual(run(payload(command="gh pr view 7")), (0, ""))

    def test_failed_create_is_silent(self):
        self.assertEqual(
            run(payload(stdout="", response={"stdout": "",
                                             "stderr": "no commits"})),
            (0, ""))

    def test_echo_without_url_does_not_trigger(self):
        self.assertEqual(
            run(payload(command='echo "gh pr create"', stdout="gh pr create\n")),
            (0, ""))

    def test_malformed_stdin_is_silent(self):
        for raw in ("", "not json", "[]", '{"tool_input": "x"}'):
            self.assertEqual(run(raw), (0, ""), raw)

    def test_existing_pr_error_on_stderr_is_silent(self):
        """gh pr create prints the *old* PR's URL to stderr when one exists."""
        err = ('a pull request for branch "x" into branch "main" already '
               "exists:\n" + URL + "\n")
        self.assertEqual(
            run(payload(command="gh pr create --fill; echo done",
                        response={"stdout": "done\n", "stderr": err})),
            (0, ""))

    def test_string_tool_response(self):
        code, out = run(payload(response=URL))
        self.assertIn(URL, out)

    def test_multiple_owners_case_insensitive(self):
        code, out = run(payload(), owners="some-org, R0JJames")
        self.assertIn(URL, out)

    def test_empty_owners_disables(self):
        self.assertEqual(run(payload(), owners=""), (0, ""))


class CopilotTest(unittest.TestCase):
    def test_off_by_default_never_calls_gh(self):
        with mock.patch.object(hook.subprocess, "run") as sp:
            run(payload())
        sp.assert_not_called()

    def test_on_requests_copilot_reviewer(self):
        with mock.patch.object(hook.subprocess, "run",
                               return_value=mock.Mock(returncode=0)) as sp:
            code, out = run(payload(), copilot="1")
        args = sp.call_args[0][0]
        self.assertEqual(args[:4], ["gh", "api", "-X", "POST"])
        self.assertIn("repos/r0jjames/demo/pulls/7/requested_reviewers", args)
        self.assertIn("reviewers[]=copilot-pull-request-reviewer[bot]", args)
        self.assertIn("Copilot review was also requested", out)

    def test_failed_request_still_emits_review_context(self):
        with mock.patch.object(hook.subprocess, "run",
                               return_value=mock.Mock(returncode=1)):
            code, out = run(payload(), copilot="1")
        self.assertIn(hook.SKILL_PATH, out)
        self.assertIn("Copilot review failed", out)

    def test_copilot_gh_missing(self):
        with mock.patch.object(hook.subprocess, "run",
                               side_effect=FileNotFoundError("gh")):
            code, out = run(payload(), copilot="1")
        self.assertEqual(code, 0)
        self.assertIn("Copilot review failed", out)

    def test_copilot_timeout(self):
        with mock.patch.object(hook.subprocess, "run",
                               side_effect=subprocess.TimeoutExpired("gh", 30)):
            code, out = run(payload(), copilot="1")
        self.assertIn("Copilot review failed", out)


if __name__ == "__main__":
    unittest.main()
