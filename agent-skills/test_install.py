import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import install


class TempDirTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)

    def make_skill(self, root, name="skill-a", content="hello"):
        d = self.tmp / root / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(content)
        return d


class TestDirsEqual(TempDirTest):
    def test_identical_trees_equal(self):
        a = self.make_skill("a")
        b = self.make_skill("b")
        self.assertTrue(install.dirs_equal(a, b))

    def test_different_file_content_not_equal(self):
        a = self.make_skill("a", content="one")
        b = self.make_skill("b", content="two")
        self.assertFalse(install.dirs_equal(a, b))

    def test_extra_file_not_equal(self):
        a = self.make_skill("a")
        b = self.make_skill("b")
        (b / "extra.md").write_text("x")
        self.assertFalse(install.dirs_equal(a, b))

    def test_nested_difference_detected(self):
        a = self.make_skill("a")
        b = self.make_skill("b")
        (a / "sub").mkdir()
        (a / "sub" / "f.txt").write_text("1")
        (b / "sub").mkdir()
        (b / "sub" / "f.txt").write_text("2")
        self.assertFalse(install.dirs_equal(a, b))


class TestInstallCopy(TempDirTest):
    def test_new_install(self):
        src = self.make_skill("src")
        dest = self.tmp / "dest" / "skill-a"
        status = install.install_copy(src, dest, dry_run=False)
        self.assertEqual(status, "installed")
        self.assertEqual((dest / "SKILL.md").read_text(), "hello")

    def test_up_to_date(self):
        src = self.make_skill("src")
        dest = self.tmp / "dest" / "skill-a"
        install.install_copy(src, dest, dry_run=False)
        self.assertEqual(install.install_copy(src, dest, dry_run=False), "up to date")

    def test_updated(self):
        src = self.make_skill("src")
        dest = self.tmp / "dest" / "skill-a"
        install.install_copy(src, dest, dry_run=False)
        (src / "SKILL.md").write_text("changed")
        self.assertEqual(install.install_copy(src, dest, dry_run=False), "updated")
        self.assertEqual((dest / "SKILL.md").read_text(), "changed")

    def test_dry_run_writes_nothing(self):
        src = self.make_skill("src")
        dest = self.tmp / "dest" / "skill-a"
        status = install.install_copy(src, dest, dry_run=True)
        self.assertEqual(status, "installed")
        self.assertFalse(dest.exists())

    def test_replaces_symlink_with_copy(self):
        src = self.make_skill("src")
        other = self.make_skill("other", name="skill-b")
        dest = self.tmp / "dest" / "skill-a"
        dest.parent.mkdir(parents=True)
        dest.symlink_to(other)
        status = install.install_copy(src, dest, dry_run=False)
        self.assertEqual(status, "updated")
        self.assertFalse(dest.is_symlink())
        self.assertEqual((dest / "SKILL.md").read_text(), "hello")


class TestInstallSymlink(TempDirTest):
    def test_creates_link(self):
        src = self.make_skill("src")
        dest = self.tmp / "dest" / "skill-a"
        status = install.install_symlink(src, dest, dry_run=False)
        self.assertEqual(status, "linked")
        self.assertTrue(dest.is_symlink())
        self.assertEqual(dest.resolve(), src.resolve())

    def test_already_linked(self):
        src = self.make_skill("src")
        dest = self.tmp / "dest" / "skill-a"
        install.install_symlink(src, dest, dry_run=False)
        self.assertEqual(install.install_symlink(src, dest, dry_run=False),
                         "already linked")

    def test_wrong_link_replaced(self):
        src = self.make_skill("src")
        other = self.make_skill("other", name="skill-b")
        dest = self.tmp / "dest" / "skill-a"
        dest.parent.mkdir(parents=True)
        dest.symlink_to(other)
        status = install.install_symlink(src, dest, dry_run=False)
        self.assertEqual(status, "linked")
        self.assertEqual(dest.resolve(), src.resolve())

    def test_broken_link_replaced(self):
        src = self.make_skill("src")
        dest = self.tmp / "dest" / "skill-a"
        dest.parent.mkdir(parents=True)
        dest.symlink_to(self.tmp / "gone")
        status = install.install_symlink(src, dest, dry_run=False)
        self.assertEqual(status, "linked")
        self.assertEqual(dest.resolve(), src.resolve())

    def test_real_dir_backed_up(self):
        src = self.make_skill("src")
        dest = self.make_skill("dest", content="old local copy")
        status = install.install_symlink(src, dest, dry_run=False)
        self.assertEqual(status, "linked")
        self.assertTrue(dest.is_symlink())
        backup = dest.parent / (dest.name + ".bak")
        self.assertEqual((backup / "SKILL.md").read_text(), "old local copy")

    def test_dry_run_writes_nothing(self):
        src = self.make_skill("src")
        dest = self.tmp / "dest" / "skill-a"
        status = install.install_symlink(src, dest, dry_run=True)
        self.assertEqual(status, "linked")
        self.assertFalse(dest.exists())


if __name__ == "__main__":
    unittest.main()
