# tests/test_copilot.py
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import copilot


class CopilotToolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        (self.repo / "copilot").mkdir(parents=True)
        (self.repo / "copilot" / "personal.instructions.md").write_text(
            "---\napplyTo: \"**\"\n---\n")
        (self.repo / "copilot" / "README.md").write_text("not an instruction\n")
        patches = [
            mock.patch.object(core, "REPO_ROOT", self.repo),
            mock.patch.object(copilot.core, "REPO_ROOT", self.repo),
            mock.patch.object(Path, "home", classmethod(lambda cls: self.tmp)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.dest = self.tmp / ".copilot" / "instructions"

    def os_is(self, name):
        return mock.patch.object(copilot.core, "detect_os", return_value=name)

    def test_runs_on_every_platform(self):
        self.assertEqual(copilot.TOOL.platforms,
                         frozenset({"macos", "linux", "gitbash"}))

    def test_only_instruction_files_are_installed(self):
        """README.md sits beside the instruction files and must stay put."""
        with self.os_is("macos"):
            copilot._post()
        self.assertTrue((self.dest / "personal.instructions.md").is_symlink())
        self.assertFalse((self.dest / "README.md").exists())

    def test_macos_symlinks_gitbash_copies(self):
        for os_name, is_link in (("macos", True), ("gitbash", False)):
            with self.subTest(os_name):
                shutil.rmtree(self.dest, ignore_errors=True)
                with self.os_is(os_name):
                    copilot._post()
                t = self.dest / "personal.instructions.md"
                self.assertEqual(t.is_symlink(), is_link)
                self.assertTrue(t.exists())

    def test_creates_the_instructions_dir_when_absent(self):
        """A fresh machine has no ~/.copilot at all."""
        self.assertFalse(self.dest.exists())
        with self.os_is("macos"):
            copilot._post()
        self.assertTrue(self.dest.is_dir())

    def test_probe_false_before_install_true_after(self):
        with self.os_is("macos"):
            self.assertFalse(copilot._probe())
            copilot._post()
            self.assertTrue(copilot._probe())

    def test_probe_false_when_copy_is_stale(self):
        with self.os_is("gitbash"):
            copilot._post()
            (self.dest / "personal.instructions.md").write_text("edited\n")
            self.assertFalse(copilot._probe())

    def test_uninstall_removes_our_files(self):
        with self.os_is("macos"):
            copilot._post()
            copilot._uninstall()
        self.assertFalse((self.dest / "personal.instructions.md").exists())

    def test_uninstall_leaves_a_user_edited_copy(self):
        with self.os_is("gitbash"):
            copilot._post()
            (self.dest / "personal.instructions.md").write_text("mine\n")
            copilot._uninstall()
        self.assertTrue((self.dest / "personal.instructions.md").exists())


class RepoInstructionsTest(unittest.TestCase):
    """The shipped file has to be a valid instruction file, and must not carry
    employer-confidential content into a personal repository."""

    def path(self):
        return (Path(__file__).resolve().parents[1]
                / "copilot" / "personal.instructions.md")

    def test_shipped_file_exists_with_applyto_frontmatter(self):
        text = self.path().read_text()
        self.assertTrue(text.startswith("---\n"))
        head = text.split("---", 2)[1]
        self.assertIn("applyTo:", head)
        self.assertIn("description:", head)

    def test_registered_in_the_tool_registry(self):
        from lib.tools import REGISTRY
        self.assertIn("copilot", REGISTRY)


if __name__ == "__main__":
    unittest.main()
