# tests/test_theme.py
from __future__ import annotations

import tempfile
import textwrap
import unittest
from pathlib import Path
from unittest import mock

from lib import core, theme

GHOSTTY = textwrap.dedent("""\
    # a comment = not a setting
    background = 300a24
    foreground = eeeeec
    cursor-color = bbbbbb
    cursor-text = 300a24
    selection-background = b5d5ff
    selection-foreground = 300a24
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


def with_config(test):
    """Point core.REPO_ROOT at a temp repo holding `text` as ghostty/config."""
    def wrapper(self, *a, **kw):
        return test(self, *a, **kw)
    return wrapper


class ThemeTestCase(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        (root / "ghostty").mkdir()
        self.config = root / "ghostty" / "config"
        self.config.write_text(GHOSTTY)
        p = mock.patch.object(core, "REPO_ROOT", root)
        p.start()
        self.addCleanup(p.stop)


class ParsingTest(ThemeTestCase):
    def test_colors_normalised_to_uppercase_hex(self):
        t = theme.load()
        self.assertEqual(t.background, "#300A24")
        self.assertEqual(t.foreground, "#EEEEEC")
        self.assertEqual(t.cursor_bg, "#BBBBBB")
        self.assertEqual(t.cursor_fg, "#300A24")
        self.assertEqual(t.selection_bg, "#B5D5FF")

    def test_palette_is_16_slots_in_index_order(self):
        palette = theme.load().palette
        self.assertEqual(len(palette), 16)
        self.assertEqual(palette[0], "#2E3436")
        # Slot 10 proves indices are numeric, not sorted as strings.
        self.assertEqual(palette[10], "#8AE234")
        self.assertEqual(palette[15], "#EEEEEC")

    def test_font_family_and_size(self):
        t = theme.load()
        self.assertEqual(t.font_family, "MesloLGS Nerd Font Mono")
        self.assertEqual(t.font_size, 13)
        self.assertIsInstance(t.font_size, int)

    def test_comment_lines_are_ignored(self):
        self.assertNotIn("a comment", str(theme.load()))

    def test_ansi_maps_slots_to_windows_terminal_names(self):
        ansi = theme.load().ansi()
        self.assertEqual(ansi["black"], "#2E3436")
        self.assertEqual(ansi["red"], "#CC0000")
        self.assertEqual(ansi["brightBlack"], "#555753")
        self.assertEqual(ansi["brightWhite"], "#EEEEEC")
        self.assertEqual(len(ansi), 16)

    def test_defaults_when_optional_keys_absent(self):
        self.config.write_text(
            "background = 000000\nforeground = ffffff\n"
            + "\n".join(f"palette = {i}=#0000{i:02x}" for i in range(16)))
        t = theme.load()
        self.assertEqual(t.cursor_bg, "#FFFFFF")   # falls back to foreground
        self.assertEqual(t.cursor_fg, "#000000")   # falls back to background
        self.assertTrue(t.bold_is_bright)


class FailureTest(ThemeTestCase):
    def test_incomplete_palette_is_an_error(self):
        self.config.write_text(GHOSTTY.replace("palette = 7=#d3d7cf\n", ""))
        with self.assertRaises(core.DotfilesError) as caught:
            theme.load()
        self.assertIn("7", str(caught.exception))

    def test_missing_background_is_an_error(self):
        self.config.write_text(GHOSTTY.replace("background = 300a24\n", ""))
        with self.assertRaises(core.DotfilesError) as caught:
            theme.load()
        self.assertIn("background", str(caught.exception))


if __name__ == "__main__":
    unittest.main()
