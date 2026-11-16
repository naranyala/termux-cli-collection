"""Tests for the action registry and documentation consistency."""

import re
import unittest
from pathlib import Path

from tcc.cli import get_actions

ROOT = Path(__file__).resolve().parents[1]
KNOWN_CATEGORIES = {"System", "Device", "Files", "Native", "Other"}


class RegistryTest(unittest.TestCase):
    def setUp(self) -> None:
        self.actions = get_actions()

    def test_names_are_unique(self) -> None:
        names = [name for name, _, _, _ in self.actions]
        self.assertEqual(len(names), len(set(names)))

    def test_callables_are_callable(self) -> None:
        for name, _, _, action in self.actions:
            self.assertTrue(callable(action), f"{name} is not callable")

    def test_categories_are_known(self) -> None:
        for name, _, category, _ in self.actions:
            self.assertIn(category, KNOWN_CATEGORIES, f"{name} has unknown category {category}")

    def test_groups_are_contiguous(self) -> None:
        categories = [category for _, _, category, _ in self.actions]
        seen: set[str] = set()
        previous = None
        for category in categories:
            if category != previous:
                self.assertNotIn(category, seen, f"category {category} appears in two blocks")
                seen.add(category)
                previous = category


class DocumentationConsistencyTest(unittest.TestCase):
    """Every registered action must have a row in the README action table."""

    def test_readme_lists_all_actions(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        documented = set(re.findall(r"\|\s*`tcc ([a-z-]+)", readme))
        # `exit` is a launcher-only pseudo-action, documented in prose instead.
        registered = {name for name, _, _, _ in get_actions()} - {"exit"}
        self.assertEqual(
            registered - documented,
            set(),
            "actions missing from the README table",
        )
        self.assertEqual(
            documented - registered,
            set(),
            "README lists actions that are not registered",
        )


if __name__ == "__main__":
    unittest.main()
