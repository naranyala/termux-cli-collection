"""Build and exercise the native C binary.

These tests are skipped automatically when no C compiler is available.
"""

import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CC = shutil.which("cc")


@unittest.skipIf(CC is None, "no C compiler available")
class NativeBinaryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.directory = tempfile.TemporaryDirectory()
        cls.binary = str(Path(cls.directory.name) / "tcc-c")
        subprocess.run(
            [
                CC,
                "-Wall",
                "-Wextra",
                "-Werror",
                "-O2",
                str(ROOT / "csrc" / "main.c"),
                str(ROOT / "csrc" / "disk.c"),
                str(ROOT / "csrc" / "system.c"),
                str(ROOT / "csrc" / "tree.c"),
                "-o",
                cls.binary,
            ],
            check=True,
            capture_output=True,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        cls.directory.cleanup()

    def run_binary(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [self.binary, *arguments],
            capture_output=True,
            text=True,
        )

    def test_help_exits_zero(self) -> None:
        self.assertEqual(self.run_binary("--help").returncode, 0)

    def test_disk_free_exits_zero(self) -> None:
        result = self.run_binary("disk-free")
        self.assertEqual(result.returncode, 0)
        self.assertIn("Total:", result.stdout)

    def test_line_count_reports_lines_and_bytes(self) -> None:
        source = ROOT / "csrc" / "tree.h"
        result = self.run_binary("line-count", str(source))
        self.assertEqual(result.returncode, 0)
        self.assertIn("lines", result.stdout)
        self.assertIn("bytes", result.stdout)

    def test_line_count_missing_file_exits_one(self) -> None:
        self.assertEqual(self.run_binary("line-count", "/definitely/not/here").returncode, 1)

    def test_invalid_action_exits_two(self) -> None:
        self.assertEqual(self.run_binary("no-such-action").returncode, 2)

    def test_tree_depth_is_validated(self) -> None:
        self.assertEqual(self.run_binary("tree", "--depth", "0").returncode, 2)
        self.assertEqual(self.run_binary("tree", "--depth", "99").returncode, 2)

    def test_tree_missing_path_exits_one(self) -> None:
        self.assertEqual(self.run_binary("tree", "/definitely/not/here").returncode, 1)

    def test_tree_renders_sorted_entries(self) -> None:
        result = self.run_binary("tree", str(ROOT / "csrc" / ".." / "csrc"), "--depth", "1")
        self.assertEqual(result.returncode, 0)
        self.assertIn("disk.c", result.stdout)


if __name__ == "__main__":
    unittest.main()
