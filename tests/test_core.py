# tests/test_core.py
from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from lib import core


class LinkFileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "repo" / "conf"
        self.src.parent.mkdir()
        self.src.write_text("repo content")
        self.target = self.root / "home" / ".conf"

    def bak(self):
        return self.target.with_name(self.target.name + ".bak-" + date.today().isoformat())

    def test_creates_symlink(self):
        core.link_file(self.src, self.target)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.target.resolve(), self.src.resolve())

    def test_idempotent(self):
        core.link_file(self.src, self.target)
        core.link_file(self.src, self.target)  # no error, still linked
        self.assertEqual(self.target.resolve(), self.src.resolve())

    def test_backs_up_existing_file(self):
        self.target.parent.mkdir()
        self.target.write_text("old content")
        core.link_file(self.src, self.target)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.bak().read_text(), "old content")

    def test_second_backup_same_day_not_overwritten(self):
        self.target.parent.mkdir()
        self.target.write_text("original")
        core.link_file(self.src, self.target)
        self.target.unlink()
        self.target.write_text("newer stale")
        core.link_file(self.src, self.target)
        self.assertEqual(self.bak().read_text(), "original")
        self.assertTrue(self.target.is_symlink())

    def test_missing_source_raises(self):
        with self.assertRaises(core.DotfilesError):
            core.link_file(self.root / "nope", self.target)


class UnlinkFileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "repo" / "conf"
        self.src.parent.mkdir()
        self.src.write_text("repo content")
        self.target = self.root / "home" / ".conf"

    def test_removes_our_link_and_restores_backup(self):
        self.target.parent.mkdir()
        self.target.write_text("old content")
        core.link_file(self.src, self.target)
        removed = core.unlink_file(self.src, self.target)
        self.assertTrue(removed)
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_text(), "old content")

    def test_removes_link_no_backup(self):
        core.link_file(self.src, self.target)
        self.assertTrue(core.unlink_file(self.src, self.target))
        self.assertFalse(self.target.exists())

    def test_leaves_foreign_file(self):
        self.target.parent.mkdir()
        self.target.write_text("mine, not yours")
        self.assertFalse(core.unlink_file(self.src, self.target))
        self.assertEqual(self.target.read_text(), "mine, not yours")

    def test_leaves_foreign_symlink(self):
        other = self.root / "other"
        other.write_text("x")
        self.target.parent.mkdir()
        self.target.symlink_to(other)
        self.assertFalse(core.unlink_file(self.src, self.target))
        self.assertTrue(self.target.is_symlink())

    def test_missing_target_ok(self):
        self.assertFalse(core.unlink_file(self.src, self.target))


class CopyFileTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.src = self.root / "repo.json"
        self.src.write_text("repo content")
        self.target = self.root / "deployed.json"

    def test_copies_and_backs_up(self):
        self.target.write_text("old")
        core.copy_file(self.src, self.target)
        self.assertEqual(self.target.read_text(), "repo content")
        bak = self.target.with_name(
            self.target.name + ".bak-" + date.today().isoformat())
        self.assertEqual(bak.read_text(), "old")

    def test_uncopy_removes_identical_and_restores(self):
        self.target.write_text("old")
        core.copy_file(self.src, self.target)
        self.assertTrue(core.uncopy_file(self.src, self.target))
        self.assertEqual(self.target.read_text(), "old")

    def test_uncopy_leaves_modified_target(self):
        core.copy_file(self.src, self.target)
        self.target.write_text("user edited this")
        self.assertFalse(core.uncopy_file(self.src, self.target))
        self.assertEqual(self.target.read_text(), "user edited this")


class DetectOsTest(unittest.TestCase):
    def test_returns_known_value(self):
        self.assertIn(core.detect_os(), ("macos", "linux", "gitbash"))


class ToolStatusTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "a").write_text("a")
        (self.root / "b").write_text("b")
        self.tool = core.Tool(
            name="fake", doc="fake tool", platforms=frozenset({"macos", "linux"}),
            links=(core.Link(str(self.root / "a"), str(self.root / "home_a")),
                   core.Link(str(self.root / "b"), str(self.root / "home_b"))))

    def test_not_installed(self):
        self.assertEqual(core.tool_status(self.tool), core.NOT_INSTALLED)

    def test_partial_then_installed(self):
        core.link_file(self.root / "a", self.root / "home_a")
        self.assertEqual(core.tool_status(self.tool), core.PARTIAL)
        core.link_file(self.root / "b", self.root / "home_b")
        self.assertEqual(core.tool_status(self.tool), core.INSTALLED)

    def test_probe_used_when_no_links(self):
        probed = core.Tool(name="p", doc="", platforms=frozenset({"macos"}),
                           status_probe=lambda: True)
        self.assertEqual(core.tool_status(probed), core.INSTALLED)


class InstallUninstallTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "conf").write_text("repo")
        self.target = self.root / ".conf"
        self.events = []
        self.tool = core.Tool(
            name="fake", doc="", platforms=frozenset({"macos", "linux"}),
            brew=("somepkg",),
            links=(core.Link(str(self.root / "conf"), str(self.target)),),
            post_install=lambda: self.events.append("post"),
            extra_uninstall=lambda: self.events.append("cleanup"))

    def test_install_orders_brew_links_post(self):
        with mock.patch.object(core, "brew_install") as bi, \
             mock.patch.object(core, "ensure_brew", return_value="brew"):
            core.install_tool(self.tool)
        bi.assert_called_once_with("somepkg", cask=False)
        self.assertTrue(self.target.is_symlink())
        self.assertEqual(self.events, ["post"])

    def test_uninstall_symmetry(self):
        self.target.write_text("pre-existing")
        with mock.patch.object(core, "brew_install"), \
             mock.patch.object(core, "ensure_brew", return_value="brew"):
            core.install_tool(self.tool)
        core.uninstall_tool(self.tool)
        self.assertEqual(self.events, ["post", "cleanup"])
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.target.read_text(), "pre-existing")
        self.assertEqual(core.tool_status(self.tool), core.NOT_INSTALLED)


if __name__ == "__main__":
    unittest.main()
