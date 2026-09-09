from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import zsh

_ZSH = "/usr/bin/zsh"

_STOCK_BASHRC = (
    "# ~/.bashrc: executed by bash(1) for non-login shells.\n"
    "case $- in\n"
    "    *i*) ;;\n"
    "      *) return;;\n"
    "esac\n"
)


class HandoffBlockTest(unittest.TestCase):
    """The ~/.bashrc block itself: shape, and the guards it must keep."""

    def test_execs_the_zsh_that_was_found(self):
        block = zsh._handoff_block("/opt/homebrew/bin/zsh")
        self.assertIn("exec /opt/homebrew/bin/zsh -l", block)

    def test_guards_on_interactive_and_on_not_already_zsh(self):
        block = zsh._handoff_block(_ZSH)
        self.assertIn("case $- in", block)
        self.assertIn('[ -z "$ZSH_VERSION" ]', block)
        self.assertIn(f"[ -x {_ZSH} ]", block)

    def test_is_delimited_by_both_markers(self):
        block = zsh._handoff_block(_ZSH)
        self.assertTrue(block.startswith(zsh._HANDOFF_BEGIN))
        self.assertTrue(block.rstrip("\n").endswith(zsh._HANDOFF_END))


class BashrcEditTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.rc = Path(self._tmp.name) / ".bashrc"
        patcher = mock.patch.object(zsh, "_bashrc", return_value=self.rc)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_appends_below_existing_content(self):
        self.rc.write_text(_STOCK_BASHRC)
        zsh.install_handoff(_ZSH)
        text = self.rc.read_text()
        self.assertTrue(text.startswith(_STOCK_BASHRC))
        self.assertIn(f"exec {_ZSH} -l", text)

    def test_creates_the_file_when_absent(self):
        zsh.install_handoff(_ZSH)
        self.assertIn(zsh._HANDOFF_BEGIN, self.rc.read_text())

    def test_install_is_idempotent(self):
        self.rc.write_text(_STOCK_BASHRC)
        zsh.install_handoff(_ZSH)
        once = self.rc.read_text()
        zsh.install_handoff(_ZSH)
        self.assertEqual(once, self.rc.read_text())

    def test_rewrites_a_stale_block_rather_than_stacking_one(self):
        self.rc.write_text(_STOCK_BASHRC)
        zsh.install_handoff("/usr/local/bin/zsh")
        zsh.install_handoff(_ZSH)
        text = self.rc.read_text()
        self.assertEqual(1, text.count(zsh._HANDOFF_BEGIN))
        self.assertNotIn("/usr/local/bin/zsh", text)
        self.assertIn(f"exec {_ZSH} -l", text)

    def test_removal_leaves_the_rest_of_the_file_intact(self):
        self.rc.write_text(_STOCK_BASHRC)
        zsh.install_handoff(_ZSH)
        zsh.remove_handoff()
        self.assertEqual(_STOCK_BASHRC, self.rc.read_text())

    def test_removal_is_a_no_op_without_a_block(self):
        self.rc.write_text(_STOCK_BASHRC)
        zsh.remove_handoff()
        self.assertEqual(_STOCK_BASHRC, self.rc.read_text())

    def test_removal_survives_a_missing_file(self):
        zsh.remove_handoff()
        self.assertFalse(self.rc.exists())


class LoginShellTest(unittest.TestCase):
    """Which of the two paths -- chsh or hand-off -- each account takes."""

    def setUp(self):
        for name in ("install_handoff", "remove_handoff"):
            patcher = mock.patch.object(zsh, name)
            setattr(self, name, patcher.start())
            self.addCleanup(patcher.stop)

    def _run(self, *, shell: str, local: bool, chsh_rc: int = 0):
        with mock.patch.object(zsh, "login_shell", return_value=shell), \
             mock.patch.object(zsh, "is_local_account", return_value=local), \
             mock.patch.object(
                 core, "run",
                 return_value=mock.Mock(returncode=chsh_rc)) as run:
            zsh._set_login_shell(_ZSH)
        return run

    def test_local_account_uses_chsh(self):
        run = self._run(shell="/bin/bash", local=True)
        run.assert_called_once_with(["chsh", "-s", _ZSH], check=False)
        self.install_handoff.assert_not_called()

    def test_directory_account_skips_chsh_entirely(self):
        """chsh writes /etc/passwd, so an AD account cannot be moved by it —
        prompting for a password there would only fail."""
        run = self._run(shell="/bin/bash", local=False)
        run.assert_not_called()
        self.install_handoff.assert_called_once_with(_ZSH)

    def test_failed_chsh_falls_back_to_the_handoff(self):
        self._run(shell="/bin/bash", local=True, chsh_rc=1)
        self.install_handoff.assert_called_once_with(_ZSH)

    def test_nothing_to_do_when_zsh_is_already_the_login_shell(self):
        run = self._run(shell="/usr/bin/zsh", local=True)
        run.assert_not_called()
        self.install_handoff.assert_not_called()

    def test_a_real_chsh_retires_an_earlier_handoff(self):
        self._run(shell="/bin/bash", local=True, chsh_rc=0)
        self.remove_handoff.assert_called_once()

    def test_already_zsh_retires_an_earlier_handoff(self):
        self._run(shell="/usr/bin/zsh", local=True)
        self.remove_handoff.assert_called_once()


class AccountKindTest(unittest.TestCase):
    def _passwd(self, text: str, user: str = "roj"):
        entry = mock.Mock(pw_name=user)
        return mock.patch.multiple(
            zsh,
            pwd=mock.Mock(getpwuid=mock.Mock(return_value=entry)),
            Path=mock.Mock(return_value=mock.Mock(
                read_text=mock.Mock(return_value=text))))

    def test_true_for_a_user_present_in_etc_passwd(self):
        with self._passwd("root:x:0:0::/root:/bin/bash\n"
                          "roj:x:1000:1000::/home/roj:/bin/bash\n"):
            self.assertTrue(zsh.is_local_account())

    def test_false_for_an_ad_account(self):
        with self._passwd("root:x:0:0::/root:/bin/bash\n"):
            self.assertFalse(zsh.is_local_account())

    def test_does_not_match_a_username_prefix(self):
        """'roj' must not be satisfied by a 'rojas' line."""
        with self._passwd("rojas:x:1001:1001::/home/rojas:/bin/bash\n"):
            self.assertFalse(zsh.is_local_account())


if __name__ == "__main__":
    unittest.main()
