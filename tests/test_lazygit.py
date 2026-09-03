# tests/test_lazygit.py
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import lazygit


class LazygitToolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        (self.repo / "lazygit").mkdir(parents=True)
        (self.repo / "lazygit" / "config.yml").write_text("gui:\n")
        patches = [
            mock.patch.object(core, "REPO_ROOT", self.repo),
            mock.patch.object(Path, "home", classmethod(lambda cls: self.tmp)),
            mock.patch.dict(os.environ, {}, clear=False),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        os.environ.pop("XDG_CONFIG_HOME", None)

    def os_is(self, name):
        return mock.patch.object(lazygit.core, "detect_os", return_value=name)

    @property
    def src(self) -> Path:
        return self.repo / "lazygit" / "config.yml"

    # ---- platform gating ----
    def test_macos_and_linux_only(self):
        self.assertEqual(lazygit.TOOL.platforms, frozenset({"macos", "linux"}))

    def test_installs_brew_package(self):
        self.assertEqual(lazygit.TOOL.brew, ("lazygit",))

    # ---- config location ----
    def test_macos_uses_application_support(self):
        with self.os_is("macos"):
            self.assertEqual(
                lazygit._target(),
                self.tmp / "Library" / "Application Support" / "lazygit"
                / "config.yml")

    def test_linux_uses_xdg_default(self):
        with self.os_is("linux"):
            self.assertEqual(lazygit._target(),
                             self.tmp / ".config" / "lazygit" / "config.yml")

    def test_xdg_config_home_wins_on_every_os(self):
        xdg = self.tmp / "xdg"
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}):
            for name in ("macos", "linux"):
                with self.os_is(name):
                    self.assertEqual(lazygit._target(),
                                     xdg / "lazygit" / "config.yml")

    # ---- install / status / uninstall ----
    def test_post_symlinks_config(self):
        with self.os_is("macos"):
            lazygit._post()
            target = lazygit._target()
            self.assertTrue(target.is_symlink())
            self.assertEqual(target.resolve(), self.src.resolve())
            self.assertTrue(lazygit._probe())

    def test_post_is_idempotent(self):
        with self.os_is("linux"):
            lazygit._post()
            lazygit._post()
            self.assertTrue(lazygit._probe())

    def test_post_backs_up_existing_config(self):
        with self.os_is("linux"):
            target = lazygit._target()
            target.parent.mkdir(parents=True)
            target.write_text("mine\n")
            lazygit._post()
            backups = list(target.parent.glob("config.yml.bak-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), "mine\n")

    def test_probe_false_before_install(self):
        with self.os_is("macos"):
            self.assertFalse(lazygit._probe())

    def test_uninstall_removes_link_and_restores_backup(self):
        with self.os_is("linux"):
            target = lazygit._target()
            target.parent.mkdir(parents=True)
            target.write_text("mine\n")
            lazygit._post()
            lazygit._uninstall()
            self.assertFalse(target.is_symlink())
            self.assertEqual(target.read_text(), "mine\n")

    def test_uninstall_leaves_foreign_file_alone(self):
        with self.os_is("macos"):
            target = lazygit._target()
            target.parent.mkdir(parents=True)
            target.write_text("not ours\n")
            lazygit._uninstall()
            self.assertEqual(target.read_text(), "not ours\n")


if __name__ == "__main__":
    unittest.main()
