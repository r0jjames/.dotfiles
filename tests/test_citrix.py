# tests/test_citrix.py
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from lib.tools import citrix_vdi


def write(path: Path, data) -> None:
    path.write_text(json.dumps(data))


class RemoveEnabledRulesTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.rules = root / "karabiner-citrix.json"
        self.config = root / "karabiner.json"
        write(self.rules, {"rules": [{"description": "Citrix VDI rule A"},
                                     {"description": "NuPhy rule B"}]})

    def test_removes_only_our_rules(self):
        write(self.config, {"profiles": [{"complex_modifications": {"rules": [
            {"description": "Citrix VDI rule A"},
            {"description": "user's own rule"},
            {"description": "NuPhy rule B"},
        ]}}]})
        removed = citrix_vdi.remove_enabled_rules(self.rules, self.config)
        self.assertEqual(removed, 2)
        config = json.loads(self.config.read_text())
        kept = config["profiles"][0]["complex_modifications"]["rules"]
        self.assertEqual(kept, [{"description": "user's own rule"}])

    def test_no_rules_enabled_leaves_file_untouched(self):
        write(self.config, {"profiles": [{"complex_modifications": {"rules": [
            {"description": "user's own rule"}]}}]})
        before = self.config.read_text()
        self.assertEqual(citrix_vdi.remove_enabled_rules(self.rules, self.config), 0)
        self.assertEqual(self.config.read_text(), before)

    def test_profile_without_complex_modifications(self):
        write(self.config, {"profiles": [{"name": "bare"}]})
        self.assertEqual(citrix_vdi.remove_enabled_rules(self.rules, self.config), 0)


class RuleFilesTest(unittest.TestCase):
    def test_two_rule_files_with_expected_descriptions(self):
        files = citrix_vdi._rules_srcs()
        self.assertEqual(
            [f.name for f in files],
            ["karabiner-citrix.json", "karabiner-nuphy-windows-mode.json"])
        for f in files:
            self.assertTrue(f.is_file(), f"{f} does not exist")

        base = json.loads(files[0].read_text())
        self.assertEqual(
            [r["description"] for r in base["rules"]],
            ["Citrix VDI: F1-F12 as function keys (with any modifiers)",
             "Citrix VDI: Left Command as Alt (all keyboards)"])

        extra = json.loads(files[1].read_text())
        self.assertEqual(
            [r["description"] for r in extra["rules"]],
            ["NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl/Cmd swap outside Citrix",
             "NuPhy (2.4G dongle + Bluetooth, Windows mode): Ctrl+Left/Right switches desktop outside Citrix"])


if __name__ == "__main__":
    unittest.main()
