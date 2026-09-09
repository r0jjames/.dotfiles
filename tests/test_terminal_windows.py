# tests/test_terminal_windows.py
"""Windows Terminal theming.

This tool can only run on the Windows box, so the logic that matters -- the
JSONC strip and the settings merge -- is written as pure functions and
exercised here on any OS.
"""
from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import terminal_windows as tw
from tests.test_theme import GHOSTTY


class WindowsTerminalTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "ghostty").mkdir()
        (self.root / "ghostty" / "config").write_text(GHOSTTY)
        p = mock.patch.object(core, "REPO_ROOT", self.root)
        p.start()
        self.addCleanup(p.stop)


class StripJsoncTest(unittest.TestCase):
    def test_removes_line_and_block_comments(self):
        text = '{\n // hi\n "a": 1, /* there */ "b": 2\n}'
        self.assertEqual(json.loads(tw.strip_jsonc(text)), {"a": 1, "b": 2})

    def test_keeps_double_slash_inside_strings(self):
        """A URL in a value must survive; this is why strings are matched."""
        text = '{"url": "https://example.com/x", "n": 1}'
        self.assertEqual(json.loads(tw.strip_jsonc(text))["url"],
                         "https://example.com/x")

    def test_keeps_comment_markers_inside_strings(self):
        text = '{"a": "/* not a comment */", "b": "// nor this"}'
        loaded = json.loads(tw.strip_jsonc(text))
        self.assertEqual(loaded["a"], "/* not a comment */")
        self.assertEqual(loaded["b"], "// nor this")

    def test_keeps_escaped_quotes_in_strings(self):
        text = r'{"a": "he said \"hi\" // ok"}'
        self.assertEqual(json.loads(tw.strip_jsonc(text))["a"],
                         'he said "hi" // ok')

    def test_windows_path_value_survives(self):
        text = r'{"cmd": "C:\\Users\\x", "n": 1}'
        self.assertEqual(json.loads(tw.strip_jsonc(text))["cmd"],
                         r"C:\Users\x")


class SchemeTest(WindowsTerminalTestCase):
    def test_scheme_has_all_sixteen_slots_plus_metadata(self):
        s = tw.scheme()
        self.assertEqual(s["name"], tw.SCHEME_NAME)
        self.assertEqual(s["background"], "#300A24")
        self.assertEqual(s["cursorColor"], "#BBBBBB")
        self.assertEqual(s["selectionBackground"], "#B5D5FF")
        for key in ("black", "red", "brightWhite", "brightPurple"):
            self.assertIn(key, s)


class MergeTest(WindowsTerminalTestCase):
    def test_adds_scheme_and_points_defaults_at_it(self):
        settings = {"profiles": {"defaults": {}, "list": []}}
        self.assertTrue(tw.merge(settings))
        self.assertEqual(settings["schemes"][0]["name"], tw.SCHEME_NAME)
        defaults = settings["profiles"]["defaults"]
        self.assertEqual(defaults["colorScheme"], tw.SCHEME_NAME)
        self.assertEqual(defaults["font"],
                         {"face": "MesloLGS Nerd Font Mono", "size": 13})

    def test_second_merge_is_a_no_op(self):
        settings = {"profiles": {"defaults": {}}}
        self.assertTrue(tw.merge(settings))
        self.assertFalse(tw.merge(settings),
                         "a re-run must not rewrite the user's file")

    def test_preserves_unrelated_settings_and_other_schemes(self):
        settings = {
            "copyOnSelect": True,
            "schemes": [{"name": "Campbell", "background": "#0C0C0C"}],
            "profiles": {"defaults": {"opacity": 80},
                         "list": [{"name": "Ubuntu"}]},
        }
        tw.merge(settings)
        self.assertIs(settings["copyOnSelect"], True)
        self.assertEqual(settings["profiles"]["defaults"]["opacity"], 80)
        self.assertEqual(settings["profiles"]["list"], [{"name": "Ubuntu"}])
        names = [s["name"] for s in settings["schemes"]]
        self.assertIn("Campbell", names)
        self.assertIn(tw.SCHEME_NAME, names)

    def test_refreshes_a_stale_copy_in_place(self):
        settings = {"schemes": [{"name": tw.SCHEME_NAME, "background": "#OLD"}],
                    "profiles": {"defaults": {}}}
        self.assertTrue(tw.merge(settings))
        matching = [s for s in settings["schemes"]
                    if s["name"] == tw.SCHEME_NAME]
        self.assertEqual(len(matching), 1, "must not append a duplicate")
        self.assertEqual(matching[0]["background"], "#300A24")

    def test_rejects_pre_1_0_profiles_list(self):
        with self.assertRaises(core.DotfilesError) as caught:
            tw.merge({"profiles": [{"name": "old"}]})
        self.assertIn("pre-1.0", str(caught.exception))


class ProbeTest(WindowsTerminalTestCase):
    def _settings_file(self, payload: str) -> Path:
        path = self.root / "settings.json"
        path.write_text(payload)
        return path

    def test_probe_true_after_merge(self):
        settings = {"profiles": {"defaults": {}}}
        tw.merge(settings)
        path = self._settings_file(json.dumps(settings))
        with mock.patch.object(tw, "settings_path", return_value=path):
            self.assertTrue(tw._probe())

    def test_probe_false_on_untouched_settings(self):
        path = self._settings_file('{"profiles": {"defaults": {}}}')
        with mock.patch.object(tw, "settings_path", return_value=path):
            self.assertFalse(tw._probe())

    def test_probe_false_when_settings_missing(self):
        with mock.patch.object(tw, "settings_path", return_value=None):
            self.assertFalse(tw._probe())

    def test_probe_false_on_unparseable_file(self):
        path = self._settings_file("{ this is not json")
        with mock.patch.object(tw, "settings_path", return_value=path):
            self.assertFalse(tw._probe())

    def test_probe_reads_a_file_with_comments(self):
        settings = {"profiles": {"defaults": {}}}
        tw.merge(settings)
        body = json.dumps(settings, indent=4)
        path = self._settings_file("// Windows Terminal\n" + body)
        with mock.patch.object(tw, "settings_path", return_value=path):
            self.assertTrue(tw._probe())


class UninstallTest(WindowsTerminalTestCase):
    def test_removes_scheme_and_leaves_the_rest(self):
        settings = {"copyOnSelect": True,
                    "schemes": [{"name": "Campbell"}],
                    "profiles": {"defaults": {"opacity": 80}}}
        tw.merge(settings)
        path = self.root / "settings.json"
        path.write_text(json.dumps(settings))
        with mock.patch.object(tw, "settings_path", return_value=path):
            tw._uninstall()
        after = json.loads(path.read_text())
        self.assertEqual([s["name"] for s in after["schemes"]], ["Campbell"])
        self.assertNotIn("colorScheme", after["profiles"]["defaults"])
        self.assertEqual(after["profiles"]["defaults"]["opacity"], 80)
        self.assertIs(after["copyOnSelect"], True)


class LocationTest(unittest.TestCase):
    def test_no_candidates_without_localappdata(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(tw.settings_candidates(), [])
            self.assertIsNone(tw.settings_path())

    def test_candidates_cover_store_preview_and_unpackaged(self):
        with mock.patch.dict(os.environ, {"LOCALAPPDATA": "/la"}, clear=False):
            found = " ".join(str(p) for p in tw.settings_candidates())
        self.assertIn("Microsoft.WindowsTerminal_8wekyb3d8bbwe", found)
        self.assertIn("Microsoft.WindowsTerminalPreview_8wekyb3d8bbwe", found)
        self.assertIn("Microsoft/Windows Terminal", found)

    def test_post_skips_when_not_on_windows(self):
        with mock.patch.dict(os.environ, {}, clear=True), \
             mock.patch.object(tw, "load_settings") as load:
            tw._post()
        load.assert_not_called()


class ToolShapeTest(unittest.TestCase):
    def test_gitbash_only(self):
        self.assertEqual(tw.TOOL.platforms, frozenset({"gitbash"}))

    def test_no_packages(self):
        self.assertEqual(tw.TOOL.apt, ())
        self.assertEqual(tw.TOOL.brew, ())


if __name__ == "__main__":
    unittest.main()
