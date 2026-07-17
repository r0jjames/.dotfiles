# tests/test_registry.py
from __future__ import annotations

import unittest

from lib import core
from lib import tools


class RegistrySanityTest(unittest.TestCase):
    def test_names_unique_and_match_keys(self):
        names = [t.name for t in tools.REGISTRY.values()]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(names, list(tools.REGISTRY.keys()))

    def test_platforms_valid(self):
        for tool in tools.REGISTRY.values():
            self.assertTrue(tool.platforms, f"{tool.name}: empty platforms")
            self.assertTrue(
                tool.platforms <= {"macos", "linux", "gitbash"},
                f"{tool.name}: bad platforms {tool.platforms}")

    def test_link_sources_exist_in_repo(self):
        for tool in tools.REGISTRY.values():
            for link in tool.links:
                self.assertFalse(
                    link.src.startswith("/"),
                    f"{tool.name}: absolute link src {link.src}")
                self.assertTrue(
                    link.src_path().exists(),
                    f"{tool.name}: missing link source {link.src_path()}")

    def test_status_never_crashes(self):
        for tool in tools.REGISTRY.values():
            self.assertIn(core.tool_status(tool),
                          (core.INSTALLED, core.PARTIAL, core.NOT_INSTALLED))

    def test_docs_present(self):
        for tool in tools.REGISTRY.values():
            self.assertTrue(tool.doc, f"{tool.name}: empty doc")


if __name__ == "__main__":
    unittest.main()
