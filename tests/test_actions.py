"""Tests for Python actions using temporary files."""

import contextlib
import hashlib
import io
import tempfile
import unittest
from pathlib import Path

from tcc import actions


class PathCheckTest(unittest.TestCase):
    def test_existing_path_returns_zero(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(actions.path_check([str(Path(__file__))]), 0)

    def test_missing_path_returns_one(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(actions.path_check(["/definitely/not/here"]), 1)


class FileInfoTest(unittest.TestCase):
    def test_missing_target_returns_one(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(actions.file_info("/definitely/not/here"), 1)

    def test_json_output_is_parseable(self) -> None:
        import json

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(actions.file_info(__file__, as_json=True), 0)
        payload = json.loads(buffer.getvalue())
        self.assertEqual(payload["type"], "file")
        self.assertIn("size", payload)


class ChecksumTest(unittest.TestCase):
    def test_sha256_known_value(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as handle:
            handle.write("hello")
            path = handle.name
        try:
            buffer = io.StringIO()
            with contextlib.redirect_stdout(buffer):
                self.assertEqual(actions.checksum(path), 0)
            expected = hashlib.sha256(b"hello").hexdigest()
            self.assertIn(expected, buffer.getvalue())
        finally:
            Path(path).unlink()

    def test_unsupported_algorithm_returns_two(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(actions.checksum(__file__, "no-such-algo"), 2)


class SystemInfoTest(unittest.TestCase):
    def test_json_output_is_parseable(self) -> None:
        import json

        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            self.assertEqual(actions.system_info(as_json=True), 0)
        payload = json.loads(buffer.getvalue())
        self.assertIn("version", payload)
        self.assertIn("directory", payload)


class ClipboardTest(unittest.TestCase):
    def test_unknown_operation_returns_two(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(actions.clipboard("delete"), 2)

    def test_set_without_content_returns_two(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(actions.clipboard("set", []), 2)


if __name__ == "__main__":
    unittest.main()
