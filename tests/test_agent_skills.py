# tests/test_agent_skills.py
from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import agent_skills


class AgentSkillsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.src = self.tmp / "repo" / "agent-skills" / "skills"
        (self.src / "explain-logic").mkdir(parents=True)
        patches = [
            mock.patch.object(agent_skills, "SKILLS_SRC", self.src),
            mock.patch.object(agent_skills, "INSTALLER",
                              self.tmp / "repo" / "agent-skills" / "install.py"),
            mock.patch.object(core, "REPO_ROOT", self.tmp / "repo"),
            mock.patch.object(Path, "home", classmethod(lambda cls: self.tmp)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def os_is(self, name):
        return mock.patch.object(agent_skills.core, "detect_os",
                                 return_value=name)

    def install_as(self, target, kind):
        d = self.tmp / (".copilot" if target == "copilot" else ".claude") / "skills"
        d.mkdir(parents=True, exist_ok=True)
        dest = d / "explain-logic"
        if kind == "symlink":
            dest.symlink_to(self.src / "explain-logic")
        else:
            (dest / "SKILL.md").parent.mkdir(parents=True)
            (dest / "SKILL.md").write_text("x")
        return dest

    # ---- platform gating ----
    def test_runs_on_gitbash(self):
        self.assertEqual(agent_skills.TOOL.platforms,
                         frozenset({"macos", "linux", "gitbash"}))

    def test_targets_per_os(self):
        with self.os_is("macos"):
            self.assertEqual(agent_skills._targets(), ["claude"])
        with self.os_is("gitbash"):
            self.assertEqual(agent_skills._targets(), ["copilot", "claude"])

    # ---- post_install ----
    def test_post_install_claude_only_on_macos(self):
        with self.os_is("macos"), mock.patch.object(core, "run") as run:
            agent_skills._post()
        self.assertEqual(run.call_args[0][0][-2:], ["--target", "claude"])

    def test_post_install_both_on_gitbash(self):
        with self.os_is("gitbash"), mock.patch.object(core, "run") as run:
            agent_skills._post()
        self.assertEqual(run.call_args[0][0][-2:], ["--target", "both"])

    # ---- status probe ----
    def test_probe_finds_symlink(self):
        self.install_as("claude", "symlink")
        with self.os_is("macos"):
            self.assertTrue(agent_skills._probe())

    def test_probe_finds_windows_copy(self):
        self.install_as("copilot", "copy")
        with self.os_is("gitbash"):
            self.assertTrue(agent_skills._probe())

    def test_probe_ignores_copilot_dir_on_macos(self):
        self.install_as("copilot", "copy")
        with self.os_is("macos"):
            self.assertFalse(agent_skills._probe())

    def test_probe_ignores_foreign_skills(self):
        d = self.tmp / ".claude" / "skills" / "code-tour"
        d.mkdir(parents=True)
        with self.os_is("macos"):
            self.assertFalse(agent_skills._probe())

    def test_probe_ignores_symlink_outside_repo(self):
        other = self.tmp / "elsewhere" / "explain-logic"
        other.mkdir(parents=True)
        d = self.tmp / ".claude" / "skills"
        d.mkdir(parents=True)
        (d / "explain-logic").symlink_to(other)
        with self.os_is("macos"):
            self.assertFalse(agent_skills._probe())

    # ---- uninstall ----
    def test_uninstall_delegates_with_custom_names(self):
        with self.os_is("gitbash"), mock.patch.object(core, "run") as run:
            agent_skills._uninstall()
        cmd = run.call_args[0][0]
        self.assertIn("--uninstall", cmd)
        self.assertEqual(cmd[cmd.index("--uninstall") + 1], "explain-logic")
        self.assertEqual(cmd[-1], "both")

    def test_uninstall_noop_without_skills(self):
        shutil.rmtree(self.src / "explain-logic")
        with self.os_is("macos"), mock.patch.object(core, "run") as run:
            agent_skills._uninstall()
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
