# tests/test_claude.py
from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import claude


class ClaudeToolTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.repo = self.tmp / "repo"
        (self.repo / "claude").mkdir(parents=True)
        for name in claude._FILES:
            (self.repo / "claude" / name).write_text(f"{name} contents\n")
        patches = [
            mock.patch.object(core, "REPO_ROOT", self.repo),
            mock.patch.object(Path, "home", classmethod(lambda cls: self.tmp)),
        ]
        for p in patches:
            p.start()
            self.addCleanup(p.stop)

    def os_is(self, name):
        return mock.patch.object(claude.core, "detect_os", return_value=name)

    def no_cli(self):
        """Skip the CLI install step — post_install runs it last."""
        return mock.patch.object(claude, "_install_cli")

    # ---- platform gating ----
    def test_runs_on_gitbash(self):
        self.assertEqual(claude.TOOL.platforms,
                         frozenset({"macos", "linux", "gitbash"}))

    def test_target_mode_per_os(self):
        with self.os_is("macos"):
            self.assertEqual(claude._target()[1], "link")
        with self.os_is("linux"):
            self.assertEqual(claude._target()[1], "link")
        with self.os_is("gitbash"):
            self.assertEqual(claude._target()[1], "copy")

    # ---- install ----
    def test_macos_symlinks_into_home(self):
        with self.os_is("macos"), self.no_cli():
            claude._post()
        for name in claude._FILES:
            t = self.tmp / ".claude" / name
            self.assertTrue(t.is_symlink(), name)
            self.assertEqual(t.resolve(), (self.repo / "claude" / name).resolve())

    def test_gitbash_copies_into_home(self):
        with self.os_is("gitbash"), self.no_cli():
            claude._post()
        for name in claude._FILES:
            t = self.tmp / ".claude" / name
            self.assertFalse(t.is_symlink(), name)
            self.assertEqual(t.read_text(), f"{name} contents\n")

    def test_gitbash_rerun_refreshes_edited_file(self):
        with self.os_is("gitbash"), self.no_cli():
            claude._post()
            (self.repo / "claude" / "settings.json").write_text("edited\n")
            claude._post()
        self.assertEqual((self.tmp / ".claude" / "settings.json").read_text(),
                         "edited\n")

    # ---- status probe ----
    def test_probe_false_before_install(self):
        with self.os_is("gitbash"):
            self.assertFalse(claude._probe())

    def test_probe_true_after_install(self):
        for os_name in ("macos", "gitbash"):
            with self.subTest(os_name), self.os_is(os_name), self.no_cli():
                claude._post()
                self.assertTrue(claude._probe())
            shutil.rmtree(self.tmp / ".claude")

    def test_probe_false_when_copy_is_stale(self):
        with self.os_is("gitbash"), self.no_cli():
            claude._post()
            (self.repo / "claude" / "CLAUDE.md").write_text("newer\n")
            self.assertFalse(claude._probe())

    # ---- uninstall ----
    def test_gitbash_uninstall_removes_copies(self):
        with self.os_is("gitbash"), self.no_cli():
            claude._post()
            claude._uninstall()
        for name in claude._FILES:
            self.assertFalse((self.tmp / ".claude" / name).exists(), name)

    def test_uninstall_leaves_user_edited_copy(self):
        with self.os_is("gitbash"), self.no_cli():
            claude._post()
            (self.tmp / ".claude" / "settings.json").write_text("mine\n")
            claude._uninstall()
        self.assertEqual((self.tmp / ".claude" / "settings.json").read_text(),
                         "mine\n")

    # ---- CLI install ----
    def test_gitbash_cli_uses_powershell(self):
        with self.os_is("gitbash"), \
                mock.patch.object(core, "have", return_value=False), \
                mock.patch.object(core, "run") as run:
            run.return_value = mock.Mock(returncode=0)
            claude._install_cli()
        self.assertEqual(run.call_args[0][0][0], "powershell")

    def test_gitbash_cli_failure_warns_without_raising(self):
        with self.os_is("gitbash"), \
                mock.patch.object(core, "have", return_value=False), \
                mock.patch.object(core, "run") as run:
            run.return_value = mock.Mock(returncode=1)
            claude._install_cli()  # must not raise — VDI may block PowerShell

    def test_macos_cli_uses_shell_installer(self):
        with self.os_is("macos"), \
                mock.patch.object(core, "have", return_value=False), \
                mock.patch.object(core, "run") as run:
            run.return_value = mock.Mock(returncode=0)
            claude._install_cli()
        self.assertIn("install.sh", run.call_args[0][0])


class ClaudeSettingsTest(unittest.TestCase):
    """The shipped settings.json has to work on every supported OS."""

    def test_statusline_path_is_not_machine_specific(self):
        settings = json.loads(
            (Path(__file__).resolve().parents[1]
             / "claude" / "settings.json").read_text())
        command = settings["statusLine"]["command"]
        self.assertNotIn("/Users/", command)
        self.assertIn("$HOME", command)

    def settings(self):
        return json.loads(
            (Path(__file__).resolve().parents[1]
             / "claude" / "settings.json").read_text())

    def test_auto_mode_environment_carries_no_single_repo_context(self):
        """This file is user-level, so it loads in every repository. Anything
        specific to one repo belongs in that repo's .claude/settings.json."""
        env = "\n".join(self.settings()["autoMode"]["environment"])
        for needle in ("second-brain", "6-Work", "ai-context"):
            self.assertNotIn(needle, env)

    def test_heavy_plugins_are_per_project_not_global(self):
        """Every globally enabled plugin's skill descriptions load into every
        session. Occasional-use plugins are enabled per project instead."""
        enabled = self.settings()["enabledPlugins"]
        for name in ("vercel", "supabase", "frontend-design", "skill-creator",
                     "claude-md-management", "claude-code-setup"):
            key = f"{name}@claude-plugins-official"
            self.assertIs(enabled.get(key), False, key)

    def test_pr_review_hook_is_installed(self):
        self.assertIn("pr_review_hook.py", claude._FILES)

    def test_pr_review_hook_command_is_not_machine_specific(self):
        entries = self.settings()["hooks"]["PostToolUse"]
        commands = [h["command"] for e in entries if e["matcher"] == "Bash"
                    for h in e["hooks"]]
        hook = [c for c in commands if "pr_review_hook.py" in c]
        self.assertEqual(len(hook), 1, commands)
        self.assertIn("$HOME/.claude/pr_review_hook.py", hook[0])
        self.assertNotIn("/Users/", hook[0])
        self.assertNotIn("/home/", hook[0])

    def test_pr_review_hook_never_blocks_when_missing(self):
        """settings.json goes live the moment it is saved (symlink), before
        install links the script — and a machine may lack python3. Exit 2
        from python would block every Bash call, so the command swallows it."""
        entries = self.settings()["hooks"]["PostToolUse"]
        command = [h["command"] for e in entries for h in e["hooks"]
                   if "pr_review_hook.py" in h["command"]][0]
        self.assertTrue(command.rstrip().endswith("|| true"), command)

    def test_pr_review_defaults(self):
        env = self.settings()["env"]
        self.assertEqual(env["PR_REVIEW_OWNERS"], "r0jjames")
        self.assertEqual(env["PR_REVIEW_COPILOT"], "0")

    def test_review_skill_stays_out_of_the_listing(self):
        overrides = self.settings()["skillOverrides"]
        self.assertEqual(overrides["review-pr-comment"], "user-invocable-only")


if __name__ == "__main__":
    unittest.main()
