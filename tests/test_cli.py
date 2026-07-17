# tests/test_cli.py
from __future__ import annotations

import contextlib
import io
import unittest
from unittest import mock

import install
from lib import core, tools


def run_main(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = install.main(argv)
    return code, out.getvalue()


class CliTest(unittest.TestCase):
    def test_list(self):
        code, out = run_main(["list"])
        self.assertEqual(code, 0)
        for name in tools.REGISTRY:
            self.assertIn(name, out)

    def test_status_lists_all_tools(self):
        code, out = run_main(["status"])
        self.assertEqual(code, 0)
        for name in tools.REGISTRY:
            self.assertIn(name, out)

    def test_unknown_tool_fails(self):
        code, _ = run_main(["install", "nosuchtool"])
        self.assertEqual(code, 1)

    def test_uninstall_requires_tools(self):
        code, _ = run_main(["uninstall"])
        self.assertEqual(code, 1)

    def test_install_runs_batch(self):
        with mock.patch.object(core, "install_tool") as it:
            code, _ = run_main(["install", "starship"])
        self.assertEqual(code, 0)
        it.assert_called_once_with(tools.REGISTRY["starship"])

    def test_uninstall_with_yes_skips_prompt(self):
        with mock.patch.object(core, "uninstall_tool") as ut:
            code, _ = run_main(["--yes", "uninstall", "starship"])
        self.assertEqual(code, 0)
        ut.assert_called_once_with(tools.REGISTRY["starship"])

    def test_batch_failure_continues_and_exits_1(self):
        with mock.patch.object(core, "install_tool",
                               side_effect=core.DotfilesError("boom")):
            code, out = run_main(["install", "starship", "claude"])
        self.assertEqual(code, 1)
        self.assertIn("starship", out)
        self.assertIn("claude", out)

    def test_not_applicable_tool_skipped_on_install_all(self):
        with mock.patch.object(core, "install_tool") as it, \
             mock.patch.object(install, "current_os", return_value="linux"):
            code, _ = run_main(["install"])
        self.assertEqual(code, 0)
        installed = {call.args[0].name for call in it.call_args_list}
        self.assertNotIn("citrix-vdi", installed)
        self.assertIn("zsh", installed)


if __name__ == "__main__":
    unittest.main()
