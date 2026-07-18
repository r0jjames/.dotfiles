# tests/test_vscode.py
from __future__ import annotations

import unittest

from lib.tools import vscode

SAMPLE = """\
# ---- AI ----
anthropic.claude-code @macos
github.copilot @windows  # work machine
ms-python.python
ms-vscode-remote.remote-wsl @windows

# comment-only line
golang.go  # untagged with comment
"""


class ParseExtensionsTest(unittest.TestCase):
    def test_macos_gets_untagged_and_macos_only(self):
        self.assertEqual(
            vscode.parse_extensions(SAMPLE, "macos"),
            ["anthropic.claude-code", "ms-python.python", "golang.go"])

    def test_gitbash_gets_untagged_and_windows_only(self):
        self.assertEqual(
            vscode.parse_extensions(SAMPLE, "gitbash"),
            ["github.copilot", "ms-python.python",
             "ms-vscode-remote.remote-wsl", "golang.go"])

    def test_unknown_tag_never_matches(self):
        self.assertEqual(
            vscode.parse_extensions("some.ext @linux\n", "macos"), [])

    def test_multiple_tags_match_any(self):
        text = "some.ext @macos @windows\n"
        self.assertEqual(vscode.parse_extensions(text, "macos"), ["some.ext"])
        self.assertEqual(vscode.parse_extensions(text, "gitbash"), ["some.ext"])

    def test_repo_extensions_file_parses_on_both_platforms(self):
        from lib import core
        text = (core.REPO_ROOT / "vscode" / "extensions.txt").read_text()
        mac = vscode.parse_extensions(text, "macos")
        win = vscode.parse_extensions(text, "gitbash")
        self.assertIn("anthropic.claude-code", mac)
        self.assertNotIn("github.copilot", mac)
        self.assertIn("github.copilot", win)
        self.assertNotIn("anthropic.claude-code", win)
        self.assertIn("ms-python.python", mac)
        self.assertIn("ms-python.python", win)


if __name__ == "__main__":
    unittest.main()
