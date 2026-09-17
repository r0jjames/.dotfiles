# tests/test_vscode.py
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import vscode

SAMPLE = """\
# ---- AI ----
anthropic.claude-code @macos @linux
github.copilot @windows  # work machine
ms-python.python
ms-vscode-remote.remote-wsl @windows

# comment-only line
golang.go  # untagged with comment
"""


class ParseExtensionsTest(unittest.TestCase):
    def test_macos_gets_untagged_and_macos_only(self):
        self.assertEqual(
            vscode.parse_extensions(SAMPLE, "macos"),
            ["anthropic.claude-code", "ms-python.python", "golang.go"])

    def test_linux_gets_untagged_and_linux_only(self):
        self.assertEqual(
            vscode.parse_extensions(SAMPLE, "linux"),
            ["anthropic.claude-code", "ms-python.python", "golang.go"])

    def test_gitbash_gets_untagged_and_windows_only(self):
        self.assertEqual(
            vscode.parse_extensions(SAMPLE, "gitbash"),
            ["github.copilot", "ms-python.python",
             "ms-vscode-remote.remote-wsl", "golang.go"])

    def test_unknown_tag_never_matches(self):
        self.assertEqual(
            vscode.parse_extensions("some.ext @bsd\n", "macos"), [])
        self.assertEqual(
            vscode.parse_extensions("some.ext @bsd\n", "linux"), [])

    def test_multiple_tags_match_any(self):
        text = "some.ext @macos @windows\n"
        self.assertEqual(vscode.parse_extensions(text, "macos"), ["some.ext"])
        self.assertEqual(vscode.parse_extensions(text, "gitbash"), ["some.ext"])
        self.assertEqual(vscode.parse_extensions(text, "linux"), [])

    def test_repo_extensions_file_parses_on_every_platform(self):
        text = (core.REPO_ROOT / "vscode" / "extensions.txt").read_text()
        mac = vscode.parse_extensions(text, "macos")
        linux = vscode.parse_extensions(text, "linux")
        win = vscode.parse_extensions(text, "gitbash")
        # Claude Code rides the personal machines, Copilot the work Windows one.
        for name in ("anthropic.claude-code",
                     "yahyashareef.claude-code-usage-tracker"):
            self.assertIn(name, mac)
            self.assertIn(name, linux)
            self.assertNotIn(name, win)
        self.assertIn("github.copilot", win)
        self.assertNotIn("github.copilot", mac)
        self.assertNotIn("github.copilot", linux)
        # Untagged lines reach all three.
        for exts in (mac, linux, win):
            self.assertIn("ms-python.python", exts)
            self.assertIn("golang.go", exts)
            self.assertIn("ms-vscode.makefile-tools", exts)
        # Windows-only extensions stay off the Unix machines.
        self.assertIn("ms-vscode-remote.remote-wsl", win)
        self.assertNotIn("ms-vscode-remote.remote-wsl", linux)


class TargetDirTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        p = mock.patch.object(Path, "home", classmethod(lambda cls: self.tmp))
        p.start()
        self.addCleanup(p.stop)

    def os_is(self, name):
        return mock.patch.object(vscode.core, "detect_os", return_value=name)

    def test_macos_user_dir(self):
        with self.os_is("macos"):
            self.assertEqual(
                vscode._target(),
                self.tmp / "Library/Application Support/Code/User")

    def test_linux_user_dir(self):
        with self.os_is("linux"):
            self.assertEqual(vscode._target(),
                             self.tmp / ".config/Code/User")

    def test_gitbash_user_dir_from_appdata(self):
        with self.os_is("gitbash"), \
                mock.patch.dict(os.environ, {"APPDATA": str(self.tmp / "AD")}):
            self.assertEqual(vscode._target(), self.tmp / "AD/Code/User")

    def test_gitbash_without_appdata_raises(self):
        with self.os_is("gitbash"), \
                mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(core.DotfilesError):
                vscode._target()

    def test_unsupported_platform_raises(self):
        with self.os_is("plan9"):
            with self.assertRaises(core.DotfilesError):
                vscode._target()


class InstallTest(unittest.TestCase):
    """Copy mode on every platform: Settings Sync owns the installed file,
    so nothing may write back into the repo."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        (self.repo / "vscode").mkdir(parents=True)
        for name in vscode._FILES:
            (self.repo / "vscode" / name).write_text(f"{name} contents\n")
        (self.repo / "vscode" / "extensions.txt").write_text("golang.go\n")
        patches = [
            mock.patch.object(core, "REPO_ROOT", self.repo),
            mock.patch.object(vscode.core, "REPO_ROOT", self.repo),
            mock.patch.object(Path, "home", classmethod(lambda cls: self.tmp)),
            mock.patch.object(vscode, "_install_extensions"),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        self.user = self.tmp / ".config/Code/User"

    def os_is(self, name="linux"):
        return mock.patch.object(vscode.core, "detect_os", return_value=name)

    def test_every_platform_copies_never_links(self):
        for os_name in ("macos", "linux", "gitbash"):
            with self.subTest(os_name), self.os_is(os_name), \
                    mock.patch.dict(os.environ,
                                    {"APPDATA": str(self.tmp / "AD")}):
                vscode._post()
                for name in vscode._FILES:
                    t = vscode._target() / name
                    self.assertFalse(t.is_symlink(), name)
                    self.assertEqual(t.read_text(), f"{name} contents\n")

    def test_rerun_refreshes_edited_file(self):
        with self.os_is():
            vscode._post()
            (self.repo / "vscode" / "settings.json").write_text("edited\n")
            vscode._post()
        self.assertEqual((self.user / "settings.json").read_text(), "edited\n")

    def test_probe_false_before_install(self):
        with self.os_is():
            self.assertFalse(vscode._probe())

    def test_probe_true_after_install(self):
        with self.os_is():
            vscode._post()
            self.assertTrue(vscode._probe())

    def test_probe_false_when_copy_is_stale(self):
        with self.os_is():
            vscode._post()
            (self.repo / "vscode" / "keybindings.json").write_text("newer\n")
            self.assertFalse(vscode._probe())

    def test_uninstall_removes_copies(self):
        with self.os_is():
            vscode._post()
            vscode._uninstall()
        for name in vscode._FILES:
            self.assertFalse((self.user / name).exists(), name)

    def test_uninstall_leaves_user_edited_copy(self):
        with self.os_is():
            vscode._post()
            (self.user / "settings.json").write_text("mine\n")
            vscode._uninstall()
        self.assertEqual((self.user / "settings.json").read_text(), "mine\n")


class LegacySymlinkTest(unittest.TestCase):
    """Machines installed under the old link mode still hold symlinks into
    the repo. Copying onto one would write straight through it."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.src = self.tmp / "settings.json"
        self.src.write_text("repo\n")
        self.target = self.tmp / "user" / "settings.json"
        self.target.parent.mkdir()

    def test_removes_symlink_pointing_at_repo(self):
        self.target.symlink_to(self.src)
        vscode._unlink_legacy(self.src, self.target)
        self.assertFalse(self.target.exists())
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(self.src.read_text(), "repo\n")

    def test_backs_up_symlink_pointing_elsewhere(self):
        other = self.tmp / "other.json"
        other.write_text("theirs\n")
        self.target.symlink_to(other)
        vscode._unlink_legacy(self.src, self.target)
        self.assertFalse(self.target.is_symlink())
        self.assertEqual(other.read_text(), "theirs\n")
        backups = list(self.target.parent.glob("settings.json.bak-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "theirs\n")

    def test_removes_broken_symlink(self):
        self.target.symlink_to(self.tmp / "gone.json")
        vscode._unlink_legacy(self.src, self.target)
        self.assertFalse(self.target.is_symlink())

    def test_leaves_regular_file_alone(self):
        self.target.write_text("mine\n")
        vscode._unlink_legacy(self.src, self.target)
        self.assertEqual(self.target.read_text(), "mine\n")

    def test_post_replaces_legacy_symlink_without_touching_repo(self):
        repo = self.tmp / "repo"
        (repo / "vscode").mkdir(parents=True)
        for name in vscode._FILES:
            (repo / "vscode" / name).write_text(f"{name} contents\n")
        user = self.tmp / ".config/Code/User"
        user.mkdir(parents=True)
        for name in vscode._FILES:
            (user / name).symlink_to(repo / "vscode" / name)
        with mock.patch.object(vscode.core, "REPO_ROOT", repo), \
                mock.patch.object(Path, "home",
                                  classmethod(lambda cls: self.tmp)), \
                mock.patch.object(vscode, "_install_extensions"), \
                mock.patch.object(vscode.core, "detect_os",
                                  return_value="linux"):
            vscode._post()
            # A later repo edit must not reach the installed copy by itself.
            (repo / "vscode" / "settings.json").write_text("edited\n")
        for name in vscode._FILES:
            self.assertFalse((user / name).is_symlink(), name)
        self.assertEqual((user / "settings.json").read_text(),
                         "settings.json contents\n")


if __name__ == "__main__":
    unittest.main()
