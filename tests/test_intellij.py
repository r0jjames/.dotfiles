# tests/test_intellij.py
from __future__ import annotations

import re
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from lib import core
from lib.tools import intellij

_INTELLIJ = core.REPO_ROOT / "intellij"
_MAC = _INTELLIJ / "keymap-macos.xml"
_WIN = _INTELLIJ / "keymap-windows.xml"
_F_KEY = re.compile(r"\bF(?:[1-9]|1[0-2])\b")  # F1..F12 as a whole token


def _shortcuts(path: Path):
    """(action_id, first, second) for every keyboard-shortcut in a keymap."""
    root = ET.fromstring(path.read_text())
    out = []
    for action in root.findall("action"):
        for sc in action.findall("keyboard-shortcut"):
            out.append((action.get("id"),
                        sc.get("first-keystroke"),
                        sc.get("second-keystroke")))
    return out


class KeymapXmlTest(unittest.TestCase):
    def test_both_files_are_well_formed(self):
        for p in (_MAC, _WIN):
            ET.fromstring(p.read_text())  # raises on malformed

    def test_keymap_name_is_roj_ffree(self):
        for p in (_MAC, _WIN):
            self.assertEqual(ET.fromstring(p.read_text()).get("name"), "Roj-Ffree")

    def test_no_function_key_survives_anywhere(self):
        # The whole point: not a single relocated chord may use F1-F12.
        for p in (_MAC, _WIN):
            for action_id, first, second in _shortcuts(p):
                for stroke in (first, second):
                    if stroke:
                        self.assertIsNone(
                            _F_KEY.search(stroke),
                            f"{p.name}: {action_id} still uses an F-key: {stroke}")

    def test_every_action_actually_has_a_chord(self):
        for p in (_MAC, _WIN):
            for action_id, first, second in _shortcuts(p):
                self.assertTrue(first, f"{p.name}: {action_id} has no first-keystroke")

    def test_mac_and_windows_bindings_are_identical(self):
        # Same logical keymap on both OSes - only the parent/header differ.
        self.assertEqual(sorted(_shortcuts(_MAC)), sorted(_shortcuts(_WIN)))

    def test_parents_differ_per_os(self):
        self.assertEqual(ET.fromstring(_WIN.read_text()).get("parent"), "$default")
        self.assertIn("Mac", ET.fromstring(_MAC.read_text()).get("parent"))

    def test_no_duplicate_chord_within_a_file(self):
        for p in (_MAC, _WIN):
            chords = [(f, s) for _, f, s in _shortcuts(p)]
            self.assertEqual(len(chords), len(set(chords)),
                             f"{p.name} has a duplicated chord")


class FindConfigDirsTest(unittest.TestCase):
    def test_matches_community_and_ultimate_ignores_others(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            for name in ("IdeaIC2026.1", "IntelliJIdea2025.3", "PyCharm2026.1",
                         "consentOptions", "somefile.txt"):
                if "." in name and name.endswith(".txt"):
                    (base / name).write_text("x")
                else:
                    (base / name).mkdir()
            found = [d.name for d in intellij.find_config_dirs(base)]
            self.assertEqual(found, ["IdeaIC2026.1", "IntelliJIdea2025.3"])

    def test_missing_base_returns_empty(self):
        self.assertEqual(intellij.find_config_dirs(Path("/no/such/dir")), [])


class PluginsFileTest(unittest.TestCase):
    def test_vscode_keymap_plugin_listed(self):
        text = (_INTELLIJ / "plugins.txt").read_text()
        self.assertIn("com.intellij.plugins.vscodekeymap", text)


if __name__ == "__main__":
    unittest.main()
