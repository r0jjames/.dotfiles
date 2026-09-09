# tests/test_terminal_ubuntu.py
from __future__ import annotations

import textwrap
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from lib import core
from lib.tools import terminal_ubuntu as tu

_GHOSTTY = textwrap.dedent("""\
    # a comment = not a setting
    background = 300a24
    foreground = eeeeec
    cursor-color = bbbbbb
    cursor-text = 300a24
    palette = 0=#2e3436
    palette = 1=#cc0000
    palette = 2=#4e9a06
    palette = 3=#c4a000
    palette = 4=#3465a4
    palette = 5=#75507b
    palette = 6=#06989a
    palette = 7=#d3d7cf
    palette = 8=#555753
    palette = 9=#ef2929
    palette = 10=#8ae234
    palette = 11=#fce94f
    palette = 12=#729fcf
    palette = 13=#ad7fa8
    palette = 14=#34e2e2
    palette = 15=#eeeeec
    bold-is-bright = true
    font-family = MesloLGS Nerd Font Mono
    font-size = 13
    macos-option-as-alt = true
    """)


class GsettingsValueTest(unittest.TestCase):
    """Colour parsing itself lives in tests/test_theme.py; what matters here
    is the GVariant text gsettings will accept."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "ghostty").mkdir()
        self.config = root / "ghostty" / "config"
        self.config.write_text(_GHOSTTY)
        p = mock.patch.object(core, "REPO_ROOT", root)
        p.start()
        self.addCleanup(p.stop)

    def test_font_joins_family_and_size(self):
        self.assertEqual(tu._desired()["font"],
                         "'MesloLGS Nerd Font Mono 13'")

    def test_theme_colours_reach_the_profile_keys(self):
        desired = tu._desired()
        self.assertEqual(desired["cursor-background-color"], "'#BBBBBB'")
        self.assertEqual(desired["foreground-color"], "'#EEEEEC'")

    def test_booleans_are_unquoted(self):
        desired = tu._desired()
        self.assertEqual(desired["use-theme-colors"], "false")
        self.assertEqual(desired["bold-is-bright"], "true")

    def test_desired_quotes_scalars_and_lists_for_gsettings(self):
        desired = tu._desired()
        self.assertEqual(desired["background-color"], "'#300A24'")
        self.assertEqual(desired["use-theme-colors"], "false")
        self.assertTrue(desired["palette"].startswith("['#2E3436', "))
        self.assertTrue(desired["palette"].endswith("'#EEEEEC']"))


class AvailabilityTest(unittest.TestCase):
    def _gsettings(self, fixed: str, reloc: str):
        def fake(cmd, *a, **kw):
            if cmd[:2] == ["gsettings", "list-schemas"]:
                return mock.Mock(returncode=0, stdout=fixed)
            if cmd[:2] == ["gsettings", "list-relocatable-schemas"]:
                return mock.Mock(returncode=0, stdout=reloc)
            return mock.Mock(returncode=0, stdout="")
        return fake

    def test_profile_schema_is_only_in_the_relocatable_list(self):
        """The regression this guards: list-schemas never shows the profile
        schema, so checking only there reports GNOME Terminal as absent."""
        with mock.patch.object(core, "have", return_value=True), \
             mock.patch.object(core, "run", side_effect=self._gsettings(
                 tu._PROFILE_LIST, tu._PROFILE_SCHEMA)):
            self.assertTrue(tu.available())

    def test_absent_when_gnome_terminal_not_installed(self):
        with mock.patch.object(core, "have", return_value=True), \
             mock.patch.object(core, "run",
                               side_effect=self._gsettings("", "")):
            self.assertFalse(tu.available())

    def test_absent_without_gsettings(self):
        with mock.patch.object(core, "have", return_value=False):
            self.assertFalse(tu.available())


class ToolShapeTest(unittest.TestCase):
    def test_linux_only(self):
        self.assertEqual(tu.TOOL.platforms, frozenset({"linux"}))

    def test_no_packages_to_install(self):
        self.assertEqual(tu.TOOL.apt, ())
        self.assertEqual(tu.TOOL.brew, ())

    def test_skips_on_wsl(self):
        with mock.patch.object(core, "is_wsl", return_value=True), \
             mock.patch.object(tu, "available") as avail:
            tu._post()
        avail.assert_not_called()

    def test_probe_false_on_wsl(self):
        with mock.patch.object(core, "is_wsl", return_value=True):
            self.assertFalse(tu._probe())


if __name__ == "__main__":
    unittest.main()
