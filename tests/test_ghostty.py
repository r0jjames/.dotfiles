# tests/test_ghostty.py
from __future__ import annotations

import textwrap
import unittest
from unittest import mock

from lib import core
from lib.tools import ghostty


def _query(value: str) -> str:
    return textwrap.dedent(f"""\
        Name: x-terminal-emulator
        Link: /usr/bin/x-terminal-emulator
        Status: manual
        Best: /usr/bin/gnome-terminal.wrapper
        Value: {value}

        Alternative: /usr/bin/ghostty
        Priority: 40
        """)


class DefaultTerminalTest(unittest.TestCase):
    def _with_query(self, stdout: str, returncode: int = 0):
        return mock.patch.object(
            core, "run",
            return_value=mock.Mock(returncode=returncode, stdout=stdout))

    def test_true_when_alternative_points_at_ghostty(self):
        with mock.patch.object(core, "have", return_value=True), \
             self._with_query(_query("/usr/bin/ghostty")):
            self.assertTrue(ghostty.is_default_terminal())

    def test_false_when_another_terminal_wins(self):
        with mock.patch.object(core, "have", return_value=True), \
             self._with_query(_query("/usr/bin/gnome-terminal.wrapper")):
            self.assertFalse(ghostty.is_default_terminal())

    def test_false_when_no_value_line(self):
        with mock.patch.object(core, "have", return_value=True), \
             self._with_query("Name: x-terminal-emulator\n"):
            self.assertFalse(ghostty.is_default_terminal())

    def test_false_when_link_group_is_unknown(self):
        """update-alternatives exits non-zero when nothing registered it."""
        with mock.patch.object(core, "have", return_value=True), \
             self._with_query("", returncode=2):
            self.assertFalse(ghostty.is_default_terminal())

    def test_false_without_update_alternatives(self):
        with mock.patch.object(core, "have", return_value=False):
            self.assertFalse(ghostty.is_default_terminal())

    def test_does_not_match_a_lookalike_path(self):
        """endswith('/ghostty') must not accept 'not-ghostty'."""
        with mock.patch.object(core, "have", return_value=True), \
             self._with_query(_query("/usr/bin/not-ghostty")):
            self.assertFalse(ghostty.is_default_terminal())


class SetDefaultTerminalTest(unittest.TestCase):
    def test_skips_when_ghostty_is_not_installed(self):
        with mock.patch.object(ghostty.shutil, "which", return_value=None), \
             mock.patch.object(core, "run") as run:
            ghostty._set_default_terminal()
        run.assert_not_called()

    def test_does_not_re_set_when_already_default(self):
        with mock.patch.object(ghostty.shutil, "which",
                               return_value="/usr/bin/ghostty"), \
             mock.patch.object(ghostty, "is_default_terminal",
                               return_value=True), \
             mock.patch.object(core, "have", return_value=False), \
             mock.patch.object(core, "run") as run:
            ghostty._set_default_terminal()
        for call in run.call_args_list:
            self.assertNotIn("update-alternatives", call.args[0])


class ToolShapeTest(unittest.TestCase):
    def test_macos_and_linux(self):
        self.assertEqual(ghostty.TOOL.platforms,
                         frozenset({"macos", "linux"}))

    def test_no_apt_list_ppa_is_handled_in_post(self):
        self.assertEqual(ghostty.TOOL.apt, ())


if __name__ == "__main__":
    unittest.main()
