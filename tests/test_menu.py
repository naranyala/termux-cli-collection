"""Tests for the non-TTY menu fallback and launcher helpers."""

import contextlib
import io
import unittest
from unittest import mock

from tcc.menu import display_rows, numbered_menu, Action


def make_actions() -> list[Action]:
    return [
        ("alpha", "First test action", "System", lambda: 0),
        ("beta", "Second test action", "Files", lambda: 3),
        ("exit", "Close the launcher", "Other", lambda: None),
    ]


class NumberedMenuTest(unittest.TestCase):
    def run_menu(self, answer: str) -> tuple[int, str]:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            with contextlib.redirect_stderr(io.StringIO()):
                with mock.patch("sys.stdin", io.StringIO(answer)):
                    code = numbered_menu(make_actions(), "tcc test")
        return code, buffer.getvalue()

    def test_valid_choice_runs_action(self) -> None:
        code, output = self.run_menu("1\n")
        self.assertEqual(code, 0)
        self.assertIn("alpha", output)

    def test_exit_choice_returns_zero(self) -> None:
        code, _ = self.run_menu("3\n")
        self.assertEqual(code, 0)

    def test_quit_returns_zero(self) -> None:
        code, _ = self.run_menu("q\n")
        self.assertEqual(code, 0)

    def test_invalid_choice_returns_two(self) -> None:
        code, _ = self.run_menu("99\n")
        self.assertEqual(code, 2)

    def test_action_return_code_is_propagated(self) -> None:
        code, _ = self.run_menu("2\n")
        self.assertEqual(code, 3)


class DisplayRowsTest(unittest.TestCase):
    def test_headers_are_inserted_per_category(self) -> None:
        rows = display_rows(make_actions())
        headers = [label for index, label in rows if index is None]
        self.assertEqual(headers, ["SYSTEM", "FILES", "OTHER"])

    def test_action_indexes_refer_to_filtered_list(self) -> None:
        rows = display_rows(make_actions())
        indexes = [index for index, _ in rows if index is not None]
        self.assertEqual(indexes, [0, 1, 2])


if __name__ == "__main__":
    unittest.main()
