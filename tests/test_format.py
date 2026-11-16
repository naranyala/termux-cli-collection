"""Tests for shared formatting helpers."""

import unittest

from tcc.actions import format_bytes, print_field
from tcc.menu import clip


class FormatBytesTest(unittest.TestCase):
    def test_zero(self) -> None:
        self.assertEqual(format_bytes(0), "0.0 B")

    def test_bytes_below_kib(self) -> None:
        self.assertEqual(format_bytes(1023), "1023.0 B")

    def test_kib(self) -> None:
        self.assertEqual(format_bytes(1024), "1.0 KiB")

    def test_mib(self) -> None:
        self.assertEqual(format_bytes(5 * 1024 * 1024), "5.0 MiB")

    def test_gib(self) -> None:
        self.assertEqual(format_bytes(2 * 1024**3), "2.0 GiB")

    def test_tib_cap(self) -> None:
        self.assertEqual(format_bytes(4 * 1024**4), "4.0 TiB")
        self.assertEqual(format_bytes(10 * 1024**5), "10240.0 TiB")


class ClipTest(unittest.TestCase):
    def test_short_value_unchanged(self) -> None:
        self.assertEqual(clip("abc", 10), "abc")

    def test_long_value_clipped_with_ellipsis(self) -> None:
        self.assertEqual(clip("abcdefghij", 8), "abcde...")

    def test_tiny_width(self) -> None:
        self.assertEqual(clip("abcdef", 3), "abc")

    def test_zero_width(self) -> None:
        self.assertEqual(clip("abcdef", 0), "")


class PrintFieldTest(unittest.TestCase):
    def test_field_label_and_value(self) -> None:
        import contextlib
        import io

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_field("Total", "1.0 KiB")
        self.assertIn("Total: 1.0 KiB", buffer.getvalue())


if __name__ == "__main__":
    unittest.main()
