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
    """(action_id, first, second) for our own relocated bindings - only
    <action> elements that carry a <keyboard-shortcut> child."""
    root = ET.fromstring(path.read_text())
    out = []
    for action in root.findall("action"):
        for sc in action.findall("keyboard-shortcut"):
            out.append((action.get("id"),
                        sc.get("first-keystroke"),
                        sc.get("second-keystroke")))
    return out


def _unbound_ids(path: Path):
    """Action ids fully unbound via an empty <action id="X"/> element.

    keymaps/*.xml has no remove="true" attribute (that only exists in a
    different XML dialect - plugin.xml action registration - and is
    silently ignored by the scheme-file reader). Each <action> element
    REPLACES that id's whole shortcut list for this keymap; zero
    <keyboard-shortcut> children means the list is empty, which
    KeymapImpl.getShortcutList returns as-is without falling back to the
    parent keymap - i.e. a real, working unbind. Verified against
    KeymapImpl.readExternal/getShortcutList bytecode (IntelliJ CE 2025.2)
    and the empty <action id="X"/> tags already used this way in bundled
    keymaps (e.g. Mac OS X 10.5+.xml has 17 of them).
    """
    root = ET.fromstring(path.read_text())
    return {a.get("id") for a in root.findall("action")
            if not list(a)}


# Conflicts discovered 2026-07-24 by diffing our keymaps against the actual
# bundled Mac OS X 10.5+.xml / $default.xml (IntelliJ CE 2025.2): these
# actions already own the same chord we relocated onto, so our XML must
# unbind them (empty <action id="X"/>) or the two actions tie (symptom:
# Rename silently did nothing - it was contending with ChooseRunConfiguration).
KNOWN_CONFLICTS = [
    # (chord, action_id_to_unbind, "mac" | "windows" | "both")
    ("control alt R", "Diff.ApplyLeftSide", "both"),
    ("control alt R", "ChooseRunConfiguration", "mac"),
    ("control alt D", "UsageGrouping.DirectoryStructure", "both"),
    ("control alt D", "ChooseDebugConfiguration", "mac"),
    ("control alt Q", "ToggleRenderedDocPresentation", "both"),
    ("control alt E", "ToggleFindInSelection", "both"),
    ("control alt E", "Console.History.Browse", "both"),
]


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
        # Same logical keymap on both OSes - only the parent/header (and the
        # OS-specific unbind entries) differ. Case-insensitive: IntelliJ
        # itself resaves keymap files in whatever case it likes (e.g. it
        # lowercased keymap-macos.xml on import) and key-letter case is not
        # semantically meaningful to the keymap parser.
        def lower(shortcuts):
            return sorted((i, (f or "").lower(), (s or "").lower())
                          for i, f, s in shortcuts)
        self.assertEqual(lower(_shortcuts(_MAC)), lower(_shortcuts(_WIN)))

    def test_parents_differ_per_os(self):
        self.assertEqual(ET.fromstring(_WIN.read_text()).get("parent"), "$default")
        self.assertIn("Mac", ET.fromstring(_MAC.read_text()).get("parent"))

    def test_no_duplicate_chord_within_a_file(self):
        # Only our own relocated bindings must be chord-unique.
        for p in (_MAC, _WIN):
            chords = [(f, s) for _, f, s in _shortcuts(p)]
            self.assertEqual(len(chords), len(set(chords)),
                             f"{p.name} has a duplicated chord")

    def test_unbound_actions_carry_no_shortcut(self):
        # An unbind entry must be a genuinely empty <action id="X"/> - if it
        # somehow gained a <keyboard-shortcut> child it would stop unbinding
        # and start re-adding, silently resurrecting the collision.
        for p in (_MAC, _WIN):
            assigned_ids = {i for i, _, _ in _shortcuts(p)}
            self.assertEqual(assigned_ids & _unbound_ids(p), set(),
                             f"{p.name}: an action is both unbound and assigned")

    def test_known_inherited_conflicts_are_unbound(self):
        mac_unbound = _unbound_ids(_MAC)
        win_unbound = _unbound_ids(_WIN)
        for _, action_id, applies_to in KNOWN_CONFLICTS:
            if applies_to in ("both", "mac"):
                self.assertIn(action_id, mac_unbound,
                             f"keymap-macos.xml doesn't unbind {action_id}")
            if applies_to in ("both", "windows"):
                self.assertIn(action_id, win_unbound,
                             f"keymap-windows.xml doesn't unbind {action_id}")

    def test_documented_conflicts_are_real_hot_set_chords(self):
        # Every documented conflict must target a chord we actually use on a
        # bare Ctrl+Alt+<letter> (no leader) hot-set action - guards against
        # the conflict list drifting from the real keymap.
        hot_set_chords = {f for _, f, s in _shortcuts(_MAC) if s is None}
        def norm(tok):
            parts = tok.lower().replace("ctrl", "control").split()
            return " ".join(sorted(parts))
        normalized_hot_set = {norm(c) for c in hot_set_chords}
        for chord, action_id, _ in KNOWN_CONFLICTS:
            self.assertIn(norm(chord), normalized_hot_set,
                         f"{action_id} conflict ({chord}) isn't a real hot-set chord")


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
