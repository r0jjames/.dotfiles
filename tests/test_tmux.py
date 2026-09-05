# tests/test_tmux.py
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib.tools import tmux


class TmuxToolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        (self.repo / "tmux" / "scripts").mkdir(parents=True)
        (self.repo / "tmux" / "tmux.conf").write_text("set -g mouse on\n")
        (self.repo / "tmux" / "scripts" / "status.sh").write_text("#!/bin/sh\n")
        patches = [
            mock.patch.object(tmux.core, "REPO_ROOT", self.repo),
            mock.patch.object(Path, "home", classmethod(lambda cls: self.tmp)),
            mock.patch.dict(os.environ, {}, clear=False),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)
        os.environ.pop("XDG_CONFIG_HOME", None)

    @property
    def src(self) -> Path:
        return self.repo / "tmux"

    # ---- registration ----
    def test_macos_and_linux_only(self):
        self.assertEqual(tmux.TOOL.platforms, frozenset({"macos", "linux"}))

    def test_installs_brew_package(self):
        self.assertEqual(tmux.TOOL.brew, ("tmux",))

    # ---- link targets ----
    def test_default_target_is_dot_config(self):
        self.assertEqual(tmux._targets(), [self.tmp / ".config" / "tmux"])

    def test_xdg_adds_a_second_target(self):
        """tmux.conf hard-codes ~/.config/tmux, so that link must exist even
        when XDG_CONFIG_HOME points elsewhere."""
        xdg = self.tmp / "xdg"
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}):
            self.assertEqual(
                tmux._targets(),
                [self.tmp / ".config" / "tmux", xdg / "tmux"])

    def test_xdg_pointing_at_dot_config_does_not_duplicate(self):
        with mock.patch.dict(os.environ,
                             {"XDG_CONFIG_HOME": str(self.tmp / ".config")}):
            self.assertEqual(tmux._targets(),
                             [self.tmp / ".config" / "tmux"])

    # ---- install / status / uninstall ----
    def test_post_symlinks_the_whole_directory(self):
        tmux._post()
        target = tmux._targets()[0]
        self.assertTrue(target.is_symlink())
        self.assertEqual(target.resolve(), self.src.resolve())
        # the helper scripts have to be reachable through the link
        self.assertTrue((target / "scripts" / "status.sh").exists())
        self.assertTrue(tmux._probe())

    def test_post_links_both_targets_under_xdg(self):
        xdg = self.tmp / "xdg"
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}):
            tmux._post()
            for target in tmux._targets():
                self.assertEqual(target.resolve(), self.src.resolve())
            self.assertTrue(tmux._probe())

    def test_post_is_idempotent(self):
        tmux._post()
        tmux._post()
        self.assertTrue(tmux._probe())

    def test_post_backs_up_an_existing_config_dir(self):
        target = tmux._targets()[0]
        target.mkdir(parents=True)
        (target / "tmux.conf").write_text("mine\n")
        tmux._post()
        backups = list(target.parent.glob("tmux.bak-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual((backups[0] / "tmux.conf").read_text(), "mine\n")

    def test_probe_false_before_install(self):
        self.assertFalse(tmux._probe())

    def test_probe_false_when_only_one_of_two_targets_is_linked(self):
        xdg = self.tmp / "xdg"
        with mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg)}):
            tmux.core.link_file(self.src, tmux._targets()[0])
            self.assertFalse(tmux._probe())

    def test_uninstall_removes_link_and_restores_backup(self):
        target = tmux._targets()[0]
        target.mkdir(parents=True)
        (target / "tmux.conf").write_text("mine\n")
        tmux._post()
        tmux._uninstall()
        self.assertFalse(target.is_symlink())
        self.assertEqual((target / "tmux.conf").read_text(), "mine\n")

    def test_uninstall_leaves_a_foreign_config_alone(self):
        target = tmux._targets()[0]
        target.mkdir(parents=True)
        (target / "tmux.conf").write_text("not ours\n")
        tmux._uninstall()
        self.assertEqual((target / "tmux.conf").read_text(), "not ours\n")


if __name__ == "__main__":
    unittest.main()
