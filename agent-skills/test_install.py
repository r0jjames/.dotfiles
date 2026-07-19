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


class TestPickTargets(unittest.TestCase):
    def test_explicit_targets(self):
        self.assertEqual(install.pick_targets("copilot"), ["copilot"])
        self.assertEqual(install.pick_targets("claude"), ["claude"])
        self.assertEqual(install.pick_targets("both"), ["copilot", "claude"])

    def test_interactive_menu(self):
        with mock.patch("builtins.input", return_value="2"):
            self.assertEqual(install.pick_targets(None), ["claude"])

    def test_interactive_invalid_exits(self):
        with mock.patch("builtins.input", return_value="9"):
            with self.assertRaises(SystemExit):
                install.pick_targets(None)


class TestVscodePromptsDir(TempDirTest):
    def test_appdata_windows_layout(self):
        user = self.tmp / "AppData" / "Code" / "User"
        user.mkdir(parents=True)
        with mock.patch.dict(os.environ, {"APPDATA": str(self.tmp / "AppData")}):
            self.assertEqual(install.vscode_prompts_dir(), user / "prompts")

    def test_none_when_no_vscode(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch("install.Path.home", return_value=self.tmp):
            self.assertIsNone(install.vscode_prompts_dir())


class TestInstallPrompts(TempDirTest):
    def test_installs_and_reports(self):
        prompts_src = self.tmp / "prompts"
        prompts_src.mkdir()
        (prompts_src / "explain-code.prompt.md").write_text("prompt body")
        user_dir = self.tmp / "Code" / "User"
        user_dir.mkdir(parents=True)
        with mock.patch("install.PROMPTS_SRC", prompts_src), \
             mock.patch("install.vscode_prompts_dir",
                        return_value=user_dir / "prompts"):
            results = install.install_prompts(dry_run=False)
        self.assertEqual(results, [("copilot", "prompt:explain-code.prompt", "installed")])
        self.assertEqual((user_dir / "prompts" / "explain-code.prompt.md").read_text(),
                         "prompt body")

    def test_up_to_date_second_run(self):
        prompts_src = self.tmp / "prompts"
        prompts_src.mkdir()
        (prompts_src / "explain-code.prompt.md").write_text("prompt body")
        user_dir = self.tmp / "Code" / "User"
        user_dir.mkdir(parents=True)
        with mock.patch("install.PROMPTS_SRC", prompts_src), \
             mock.patch("install.vscode_prompts_dir",
                        return_value=user_dir / "prompts"):
            install.install_prompts(dry_run=False)
            results = install.install_prompts(dry_run=False)
        self.assertEqual(results[0][2], "up to date")

    def test_no_vscode_dir_warns_and_returns_empty(self):
        with mock.patch("install.vscode_prompts_dir", return_value=None):
            self.assertEqual(install.install_prompts(dry_run=False), [])


class TestCommunityCache(TempDirTest):
    def test_clone_failure_warns_and_returns_none(self):
        cache = self.tmp / "cache" / "awesome-copilot"
        boom = subprocess.CalledProcessError(128, ["git", "clone"])
        with mock.patch("install.cache_dir", return_value=cache), \
             mock.patch("install.run_git", side_effect=boom):
            self.assertIsNone(install.update_community_cache(dry_run=False))

    def test_clone_failure_uses_existing_cache(self):
        cache = self.tmp / "cache" / "awesome-copilot"
        (cache / ".git").mkdir(parents=True)
        (cache / "skills" / "code-tour").mkdir(parents=True)
        boom = subprocess.CalledProcessError(128, ["git", "fetch"])
        with mock.patch("install.cache_dir", return_value=cache), \
             mock.patch("install.run_git", side_effect=boom):
            self.assertEqual(install.update_community_cache(dry_run=False), cache)

    def test_fresh_clone_invokes_git(self):
        cache = self.tmp / "cache" / "awesome-copilot"
        calls = []
        with mock.patch("install.cache_dir", return_value=cache), \
             mock.patch("install.run_git", side_effect=lambda a: calls.append(a)):
            result = install.update_community_cache(dry_run=False)
        self.assertEqual(result, cache)
        self.assertEqual(calls[0][0], "clone")
        self.assertIn("sparse-checkout", calls[1])

    def test_caveman_clone_uses_caveman_repo(self):
        cache = self.tmp / "cache" / "caveman"
        calls = []
        with mock.patch("install.caveman_cache_dir", return_value=cache), \
             mock.patch("install.run_git", side_effect=lambda a: calls.append(a)):
            result = install.update_caveman_cache(dry_run=False)
        self.assertEqual(result, cache)
        self.assertIn(install.CAVEMAN_REPO_URL, calls[0])
        self.assertIn("skills/caveman", calls[1])

    def test_caveman_existing_cache_updates(self):
        cache = self.tmp / "cache" / "caveman"
        (cache / ".git").mkdir(parents=True)
        calls = []
        with mock.patch("install.caveman_cache_dir", return_value=cache), \
             mock.patch("install.run_git", side_effect=lambda a: calls.append(a)):
            result = install.update_caveman_cache(dry_run=False)
        self.assertEqual(result, cache)
        self.assertIn("fetch", calls[1])
        self.assertIn("reset", calls[2])

    def test_addy_clone_uses_addy_repo(self):
        cache = self.tmp / "cache" / "addy-agent-skills"
        calls = []
        with mock.patch("install.addy_cache_dir", return_value=cache), \
             mock.patch("install.run_git", side_effect=lambda a: calls.append(a)):
            result = install.update_addy_cache(dry_run=False)
        self.assertEqual(result, cache)
        self.assertIn(install.ADDY_REPO_URL, calls[0])
        self.assertIn("skills/debugging-and-error-recovery", calls[1])


class TestBuildItems(unittest.TestCase):
    def test_orders_skills_prompts_community(self):
        items = install.build_items(
            custom_skills=["explain-logic", "soundboarding"],
            prompt_files=["create-sb.prompt.md", "explain-code.prompt.md"])
        kinds = [k for k, _ in items]
        self.assertEqual(kinds[:2], ["skill", "skill"])
        self.assertEqual(kinds[2:4], ["prompt", "prompt"])
        self.assertTrue(all(k == "community" for k in kinds[4:]))
        names = [n for _, n in items]
        for s in (install.COMMUNITY_SKILLS + install.CAVEMAN_SKILLS
                  + install.ADDY_SKILLS):
            self.assertIn(s, names)


class TestPickItems(unittest.TestCase):
    ITEMS = [("skill", "explain-logic"), ("skill", "soundboarding"),
             ("prompt", "create-sb.prompt.md"), ("community", "caveman")]

    def pick(self, inputs):
        it = iter(inputs)
        with mock.patch("builtins.input", side_effect=lambda *_: next(it)):
            return install.pick_items(list(self.ITEMS))

    def test_enter_confirms_all_preselected(self):
        self.assertEqual(self.pick([""]), self.ITEMS)

    def test_number_toggles_off(self):
        result = self.pick(["2", ""])
        self.assertNotIn(("skill", "soundboarding"), result)
        self.assertEqual(len(result), 3)

    def test_toggle_twice_back_on(self):
        self.assertEqual(self.pick(["2", "2", ""]), self.ITEMS)

    def test_a_toggles_all_then_one_on(self):
        result = self.pick(["a", "3", ""])
        self.assertEqual(result, [("prompt", "create-sb.prompt.md")])

    def test_zero_selected_exits(self):
        with self.assertRaises(SystemExit):
            self.pick(["a", ""])

    def test_invalid_input_reprompts(self):
        self.assertEqual(self.pick(["zzz", "99", ""]), self.ITEMS)


class TestInstallPromptsFilter(TempDirTest):
    def test_names_filter_limits_install(self):
        prompts_src = self.tmp / "prompts"
        prompts_src.mkdir()
        (prompts_src / "a.prompt.md").write_text("a")
        (prompts_src / "b.prompt.md").write_text("b")
        user_dir = self.tmp / "Code" / "User"
        user_dir.mkdir(parents=True)
        with mock.patch("install.PROMPTS_SRC", prompts_src), \
             mock.patch("install.vscode_prompts_dir",
                        return_value=user_dir / "prompts"):
            results = install.install_prompts(dry_run=False,
                                              names={"b.prompt.md"})
        self.assertEqual([r[1] for r in results], ["prompt:b.prompt"])
        self.assertFalse((user_dir / "prompts" / "a.prompt.md").exists())


class TestRegistry(unittest.TestCase):
    def test_caveman_is_copilot_only(self):
        source, meta = install.registry()["caveman"]
        self.assertEqual(meta["targets"], ("copilot",))
        self.assertEqual(source["label"], "caveman")

    def test_debugging_is_copilot_only_default(self):
        _, meta = install.registry()["debugging-and-error-recovery"]
        self.assertEqual(meta["targets"], ("copilot",))
        self.assertTrue(meta["default"])

    def test_cherry_picks_not_default(self):
        reg = install.registry()
        for name in ("observability-and-instrumentation", "ci-cd-and-automation",
                     "security-and-hardening", "deprecation-and-migration",
                     "pdf", "docx", "pptx", "xlsx"):
            self.assertFalse(reg[name][1]["default"], name)

    def test_default_names_match_legacy_constants(self):
        self.assertEqual(
            install.default_community_names(),
            set(install.COMMUNITY_SKILLS + install.CAVEMAN_SKILLS
                + ["debugging-and-error-recovery"]))

    def test_legacy_cache_dir_used_for_awesome(self):
        source = install.source_by_label("awesome-copilot")
        with mock.patch("install.cache_dir",
                        return_value=Path("/tmp/xyz")) as m:
            self.assertEqual(install.source_cache_dir(source), Path("/tmp/xyz"))
            m.assert_called_once()

    def test_new_source_gets_registry_cache_path(self):
        source = install.source_by_label("anthropics-skills")
        self.assertEqual(install.source_cache_dir(source),
                         Path.home() / ".agent-skills-cache" / "anthropics-skills")

    def test_update_source_cache_sparse_names(self):
        source = install.source_by_label("addy-agent-skills")
        with mock.patch("install.update_repo_cache") as m:
            install.update_source_cache(source, dry_run=False,
                                        names=["security-and-hardening"])
        sparse = m.call_args[0][3]
        self.assertEqual(sparse, ["skills/security-and-hardening"])


class TestInstallCommunityForTarget(TempDirTest):
    def fake_sources(self, with_cache=True):
        cache = self.tmp / "cache"
        (cache / "skills" / "tool-x").mkdir(parents=True)
        (cache / "skills" / "tool-x" / "SKILL.md").write_text("x")
        return [{
            "label": "fake", "url": "u", "branch": "main", "cache": "fake",
            "fallback": "f",
            "_cache": cache if with_cache else None,
            "skills": {
                "tool-x": {"targets": ("copilot", "claude"), "default": True},
                "cop-only": {"targets": ("copilot",), "default": True,
                             "note": "claude uses plugin"},
            },
        }]

    def test_installs_allowed_skill(self):
        dest = self.tmp / "dest"
        with mock.patch("install.SOURCES", self.fake_sources()):
            results = install.install_community_for_target(
                "claude", dest, {"tool-x"}, dry_run=False)
        self.assertEqual(results, [("claude", "tool-x", "installed")])
        self.assertTrue((dest / "tool-x" / "SKILL.md").is_file())

    def test_skips_wrong_target_with_note(self):
        dest = self.tmp / "dest"
        with mock.patch("install.SOURCES", self.fake_sources()):
            results = install.install_community_for_target(
                "claude", dest, {"cop-only"}, dry_run=False)
        self.assertEqual(results,
                         [("claude", "cop-only",
                           "skipped (claude uses plugin)")])
        self.assertFalse((dest / "cop-only").exists())

    def test_missing_in_cache_reported(self):
        sources = self.fake_sources()
        sources[0]["skills"]["ghost"] = {"targets": ("claude",),
                                         "default": True}
        dest = self.tmp / "dest"
        with mock.patch("install.SOURCES", sources):
            results = install.install_community_for_target(
                "claude", dest, {"ghost"}, dry_run=False)
        self.assertEqual(results,
                         [("claude", "ghost", "missing in cache — skipped")])

    def test_no_cache_skips_silently(self):
        dest = self.tmp / "dest"
        with mock.patch("install.SOURCES", self.fake_sources(with_cache=False)):
            results = install.install_community_for_target(
                "claude", dest, {"tool-x"}, dry_run=False)
        self.assertEqual(results, [])


class TestStatus(TempDirTest):
    def make_dest(self):
        dest = self.tmp / "claude-skills"
        dest.mkdir(parents=True)
        return dest

    def test_classifies_custom_community_unknown(self):
        dest = self.make_dest()
        src = self.make_skill("repo", name="explain-logic")
        (dest / "explain-logic").symlink_to(src)
        (dest / "code-tour").mkdir()
        (dest / "mystery").mkdir()
        rows, warnings = install.gather_status(
            "claude", dest, {"explain-logic"}, {})
        by_name = {r[0]: r for r in rows}
        self.assertEqual(by_name["explain-logic"][1:],
                         ("custom", "symlink"))
        self.assertEqual(by_name["code-tour"][1:],
                         ("community (awesome-copilot)", "copy"))
        self.assertEqual(by_name["mystery"][1:], ("unknown", "copy"))
        self.assertEqual(warnings, [])

    def test_broken_symlink_warns(self):
        dest = self.make_dest()
        (dest / "explain-logic").symlink_to(self.tmp / "gone")
        _, warnings = install.gather_status(
            "claude", dest, {"explain-logic"}, {})
        self.assertIn("claude: explain-logic is a broken symlink", warnings)

    def test_wrong_target_warns(self):
        dest = self.make_dest()
        (dest / "caveman").mkdir()
        _, warnings = install.gather_status("claude", dest, set(), {})
        self.assertTrue(any("caveman" in w and "claude" in w
                            for w in warnings))

    def test_plugin_duplicate_warns(self):
        dest = self.make_dest()
        (dest / "brainstorming").mkdir()
        _, warnings = install.gather_status(
            "claude", dest, set(),
            {"brainstorming": "superpowers@claude-plugins-official"})
        self.assertTrue(any("superpowers@claude-plugins-official" in w
                            for w in warnings))

    def test_plugin_duplicate_ignored_on_copilot(self):
        dest = self.make_dest()
        (dest / "brainstorming").mkdir()
        _, warnings = install.gather_status(
            "copilot", dest, set(),
            {"brainstorming": "superpowers@claude-plugins-official"})
        self.assertEqual(warnings, [])

    def test_plugin_skills_reads_enabled_only(self):
        settings = self.tmp / "settings.json"
        settings.write_text(
            '{"enabledPlugins": {"good@mp": true, "off@mp": false}}')
        cache = self.tmp / "plugcache"
        for plug, skill in (("good", "alpha"), ("off", "beta")):
            (cache / "mp" / plug / "1.0.0" / "skills" / skill).mkdir(
                parents=True)
        result = install.plugin_skills(cache_root=cache,
                                       settings_path=settings)
        self.assertEqual(result, {"alpha": "good@mp"})

    def test_plugin_skills_missing_config_empty(self):
        result = install.plugin_skills(
            cache_root=self.tmp / "nope",
            settings_path=self.tmp / "nope.json")
        self.assertEqual(result, {})


class TestPickerTags(TempDirTest):
    def test_installed_tag(self):
        root = self.tmp / "claude" / "skills"
        (root / "code-tour").mkdir(parents=True)
        with mock.patch("install.target_root", return_value=root):
            tag = install.item_tag("community", "code-tour", ["claude"], {})
        self.assertEqual(tag, "[installed]")

    def test_conflict_tag_from_plugin(self):
        root = self.tmp / "claude" / "skills"
        root.mkdir(parents=True)
        with mock.patch("install.target_root", return_value=root):
            tag = install.item_tag("community", "caveman", ["claude"],
                                   {"caveman": "caveman@caveman"})
        self.assertEqual(tag, "[conflict]")

    def test_update_tag_for_stale_custom_copy(self):
        src = self.make_skill("repo", name="explain-logic",
                              content="new")
        root = self.tmp / "copilot" / "skills"
        (root / "explain-logic").mkdir(parents=True)
        (root / "explain-logic" / "SKILL.md").write_text("old")
        with mock.patch("install.target_root", return_value=root), \
             mock.patch("install.SKILLS_SRC", src.parent):
            tag = install.item_tag("skill", "explain-logic",
                                   ["copilot"], {})
        self.assertEqual(tag, "[installed] [update]")

    def test_no_tag_when_absent(self):
        root = self.tmp / "claude" / "skills"
        root.mkdir(parents=True)
        with mock.patch("install.target_root", return_value=root):
            self.assertEqual(
                install.item_tag("community", "pdf", ["claude"], {}), "")

    def test_pick_items_preselected_and_tags_render(self):
        items = [("community", "pdf"), ("community", "code-tour")]
        with mock.patch("builtins.input", side_effect=["1", ""]):
            chosen = install.pick_items(
                items, preselected=[False, True],
                tags={("community", "code-tour"): "[installed]"})
        self.assertEqual(chosen, items)  # 'pdf' toggled on by input "1"


class TestUninstall(TempDirTest):
    def test_removes_copy_and_symlink(self):
        dest = self.tmp / "skills"
        src = self.make_skill("repo", name="explain-logic")
        dest.mkdir()
        (dest / "explain-logic").symlink_to(src)
        (dest / "code-tour").mkdir()
        results = install.uninstall_skills(
            ["explain-logic", "code-tour"], "claude", dest,
            {"explain-logic", "code-tour"}, force=False, dry_run=False)
        self.assertEqual(results,
                         [("claude", "explain-logic", "removed (symlink)"),
                          ("claude", "code-tour", "removed")])
        self.assertFalse((dest / "explain-logic").is_symlink())
        self.assertFalse((dest / "code-tour").exists())
        self.assertTrue(src.exists())  # repo source untouched

    def test_unknown_refused_without_force(self):
        dest = self.tmp / "skills"
        (dest / "mystery").mkdir(parents=True)
        results = install.uninstall_skills(
            ["mystery"], "claude", dest, set(), force=False, dry_run=False)
        self.assertEqual(results,
                         [("claude", "mystery", "unknown — use --force")])
        self.assertTrue((dest / "mystery").exists())

    def test_unknown_removed_with_force(self):
        dest = self.tmp / "skills"
        (dest / "mystery").mkdir(parents=True)
        results = install.uninstall_skills(
            ["mystery"], "claude", dest, set(), force=True, dry_run=False)
        self.assertEqual(results, [("claude", "mystery", "removed")])
        self.assertFalse((dest / "mystery").exists())

    def test_not_installed(self):
        dest = self.tmp / "skills"
        dest.mkdir()
        results = install.uninstall_skills(
            ["ghost"], "claude", dest, {"ghost"}, force=False,
            dry_run=False)
        self.assertEqual(results, [("claude", "ghost", "not installed")])

    def test_dry_run_removes_nothing(self):
        dest = self.tmp / "skills"
        (dest / "code-tour").mkdir(parents=True)
        results = install.uninstall_skills(
            ["code-tour"], "claude", dest, {"code-tour"}, force=False,
            dry_run=True)
        self.assertEqual(results, [("claude", "code-tour", "removed")])
        self.assertTrue((dest / "code-tour").exists())


if __name__ == "__main__":
    unittest.main()
