# tests/test_ui.py
from __future__ import annotations

import unittest

from lib import ui


def scripted(*lines):
    it = iter(lines)
    return lambda prompt="": next(it)


ITEMS = [
    ui.MenuItem("zsh", "installed", True),
    ui.MenuItem("nvim", "not installed", True),
    ui.MenuItem("citrix-vdi", "macOS only", False),
]


class ParseNumbersTest(unittest.TestCase):
    def test_spaces_and_commas(self):
        self.assertEqual(ui.parse_numbers("1 3", 3), {1, 3})
        self.assertEqual(ui.parse_numbers("1,2", 3), {1, 2})
        self.assertEqual(ui.parse_numbers("1, 2", 3), {1, 2})

    def test_out_of_range_or_junk_is_none(self):
        self.assertIsNone(ui.parse_numbers("0", 3))
        self.assertIsNone(ui.parse_numbers("4", 3))
        self.assertIsNone(ui.parse_numbers("x", 3))


class InteractiveSelectTest(unittest.TestCase):
    def test_toggle_then_confirm(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("1 2", ""), print_fn=lambda *a: None)
        self.assertEqual(sel, [0, 1])

    def test_toggle_twice_removes(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("1", "1", "2", ""), print_fn=lambda *a: None)
        self.assertEqual(sel, [1])

    def test_all_skips_disabled(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("a", ""), print_fn=lambda *a: None)
        self.assertEqual(sel, [0, 1])

    def test_disabled_not_toggleable(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("3", ""), print_fn=lambda *a: None)
        self.assertEqual(sel, [])

    def test_quit(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted("1", "q"), print_fn=lambda *a: None)
        self.assertEqual(sel, [])

    def test_empty_with_no_selection_quits(self):
        sel = ui.interactive_select(
            ITEMS, input_fn=scripted(""), print_fn=lambda *a: None)
        self.assertEqual(sel, [])


class ChooseActionTest(unittest.TestCase):
    def test_actions(self):
        self.assertEqual(ui.choose_action(input_fn=scripted("i")), "install")
        self.assertEqual(ui.choose_action(input_fn=scripted("u")), "uninstall")
        self.assertEqual(ui.choose_action(input_fn=scripted("q")), "quit")

    def test_reprompts_on_junk(self):
        self.assertEqual(ui.choose_action(input_fn=scripted("z", "i")), "install")


class ConfirmTest(unittest.TestCase):
    def test_yes_no_default_no(self):
        self.assertTrue(ui.confirm("?", input_fn=scripted("y")))
        self.assertFalse(ui.confirm("?", input_fn=scripted("n")))
        self.assertFalse(ui.confirm("?", input_fn=scripted("")))


if __name__ == "__main__":
    unittest.main()
