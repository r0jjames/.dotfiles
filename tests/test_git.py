# tests/test_git.py
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import git


class GitToolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        (self.repo / "git").mkdir(parents=True)
        (self.repo / "git" / "ignore").write_text(".tours/\n")
        patches = [
            mock.patch.object(core, "REPO_ROOT", self.repo),
            mock.patch.object(Path, "home", classmethod(lambda cls: self.tmp)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def os_is(self, name):
        return mock.patch.object(git.core, "detect_os", return_value=name)

    def no_git_config(self):
        """Skip the git config step — post_install runs it last."""
        return mock.patch.object(git, "_point_git_at")

    @property
    def target(self) -> Path:
        return self.tmp / ".config" / "git" / "ignore"

    # ---- platform gating ----
    def test_runs_everywhere(self):
        self.assertEqual(git.TOOL.platforms,
                         frozenset({"macos", "linux", "gitbash"}))

    def test_target_mode_per_os(self):
        with self.os_is("macos"):
            self.assertEqual(git._target()[1], "link")
        with self.os_is("linux"):
            self.assertEqual(git._target()[1], "link")
        with self.os_is("gitbash"):
            self.assertEqual(git._target()[1], "copy")

    # ---- install ----
    def test_macos_symlinks_excludes_file(self):
        with self.os_is("macos"), self.no_git_config():
            git._post()
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.target.resolve(),
                         (self.repo / "git" / "ignore").resolve())

    def test_gitbash_copies_excludes_file(self):
        with self.os_is("gitbash"), self.no_git_config():
            git._post()
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_text(), ".tours/\n")

    def test_install_backs_up_existing_file(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("mine\n")
        with self.os_is("macos"), self.no_git_config():
            git._post()
        backups = list(self.target.parent.glob("ignore.bak-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "mine\n")

    # ---- git config wiring ----
    def test_sets_excludes_file_when_unset(self):
        with mock.patch.object(core, "have", return_value=True), \
                mock.patch.object(core, "run") as run:
            run.return_value = mock.Mock(returncode=1, stdout="")
            git._point_git_at(self.target)
        self.assertEqual(run.call_args[0][0],
                         ["git", "config", "--global", "core.excludesFile",
                          str(self.target)])

    def test_leaves_foreign_excludes_file_alone(self):
        with mock.patch.object(core, "have", return_value=True), \
                mock.patch.object(core, "run") as run:
            run.return_value = mock.Mock(returncode=0, stdout="/elsewhere\n")
            git._point_git_at(self.target)
        self.assertEqual(run.call_count, 1, "should only have read the key")

    def test_no_git_binary_warns_without_raising(self):
        with mock.patch.object(core, "have", return_value=False):
            git._point_git_at(self.target)  # must not raise

    # ---- status probe ----
    def test_probe_false_before_install(self):
        with self.os_is("macos"):
            self.assertFalse(git._probe())

    def test_probe_true_after_install(self):
        for os_name in ("macos", "gitbash"):
            with self.subTest(os_name), self.os_is(os_name), \
                    self.no_git_config():
                git._post()
                self.assertTrue(git._probe())
            self.target.unlink()

    def test_probe_false_when_copy_is_stale(self):
        with self.os_is("gitbash"), self.no_git_config():
            git._post()
            (self.repo / "git" / "ignore").write_text(".tours/\nnewer\n")
            self.assertFalse(git._probe())

    # ---- uninstall ----
    def test_uninstall_removes_link(self):
        with self.os_is("macos"), self.no_git_config():
            git._post()
            git._uninstall()
        self.assertFalse(self.target.exists())

    def test_uninstall_restores_backup(self):
        self.target.parent.mkdir(parents=True)
        self.target.write_text("mine\n")
        with self.os_is("macos"), self.no_git_config():
            git._post()
            git._uninstall()
        self.assertEqual(self.target.read_text(), "mine\n")

    def test_uninstall_leaves_user_edited_copy(self):
        with self.os_is("gitbash"), self.no_git_config():
            git._post()
            self.target.write_text("mine\n")
            git._uninstall()
        self.assertEqual(self.target.read_text(), "mine\n")


class ShippedIgnoreTest(unittest.TestCase):
    """The file that actually ships has to carry the patterns it exists for."""

    def test_ignores_tours_and_claude_local_settings(self):
        text = (Path(__file__).resolve().parents[1] / "git" / "ignore").read_text()
        lines = [l.strip() for l in text.splitlines() if l.strip()
                 and not l.strip().startswith("#")]
        self.assertIn(".tours/", lines)
        self.assertIn("**/.claude/settings.local.json", lines)


if __name__ == "__main__":
    unittest.main()
