"""Actions exposed by the tcc launcher."""

from __future__ import annotations

import datetime
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

from . import __version__


def format_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or unit == "TiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def system_info() -> None:
    print("System information")
    print(f"  Version:   {__version__}")
    print(f"  OS:        {platform.system()} {platform.release()}")
    print(f"  Machine:   {platform.machine()}")
    print(f"  Python:    {platform.python_version()}")
    print(f"  Termux:    {os.environ.get('PREFIX', 'not detected')}")
    print(f"  Directory: {Path.cwd()}")


def storage() -> None:
    usage = shutil.disk_usage(Path.cwd())
    used = usage.total - usage.free
    print(f"Storage: {Path.cwd()}")
    print(f"  Total: {format_bytes(usage.total)}")
    print(f"  Used:  {format_bytes(used)}")
    print(f"  Free:  {format_bytes(usage.free)}")
    print(f"  Usage: {used / usage.total * 100:.1f}%")


def environment() -> None:
    print("Termux environment")
    for key in ("PREFIX", "HOME", "SHELL", "PWD"):
        print(f"  {key}: {os.environ.get(key, 'not set')}")
    print(f"  PATH entries: {len(os.environ.get('PATH', '').split(os.pathsep))}")


def path_check(targets: list[str] | None = None) -> int:
    paths = [Path(value).expanduser() for value in (targets or ["."])]
    missing = 0
    for path in paths:
        resolved = path.resolve(strict=False)
        if not path.exists() and not path.is_symlink():
            kind = "missing"
            missing += 1
        elif path.is_symlink():
            kind = f"symlink -> {path.readlink()}"
        elif path.is_dir():
            kind = "directory"
        else:
            kind = "file"
        print(f"{path}: {kind} ({resolved})")
    return 1 if missing else 0


def file_info(target: str = ".") -> int:
    path = Path(target).expanduser()
    try:
        info = path.stat()
    except OSError as error:
        print(f"Cannot inspect {path}: {error}", file=sys.stderr)
        return 1
    kind = "directory" if path.is_dir() else "file" if path.is_file() else "other"
    print(f"Path: {path.resolve()}")
    print(f"  Type:  {kind}")
    print(f"  Size:  {format_bytes(info.st_size)}")
    print(f"  Mode:  {oct(info.st_mode & 0o777)}")
    print(f"  Mtime: {datetime.datetime.fromtimestamp(info.st_mtime).isoformat(timespec="seconds")}")
    return 0


def checksum(target: str, algorithm: str = "sha256") -> int:
    path = Path(target).expanduser()
    try:
        digest = hashlib.new(algorithm)
    except ValueError:
        print(f"Unsupported algorithm: {algorithm}", file=sys.stderr)
        return 2
    try:
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
    except OSError as error:
        print(f"Cannot read {path}: {error}", file=sys.stderr)
        return 1
    print(f"{digest.hexdigest()}  {path}")
    return 0


def battery(as_json: bool = False) -> None:
    command = shutil.which("termux-battery-status")
    if command is None:
        print("Battery status is unavailable.")
        print("Install Termux:API and run: pkg install termux-api")
        return
    try:
        result = subprocess.run([command], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"Could not read battery status: {error}", file=sys.stderr)
        return
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return
    print("Battery status")
    for key in ("percentage", "status", "plugged", "temperature", "current"):
        if key in data:
            print(f"  {key.capitalize()}: {data[key]}")


def native_disk_free() -> None:
    binary = os.environ.get("TCC_C_BINARY")
    if not binary:
        # Installed layout: $PREFIX/share/tcc/tcc/actions.py.
        prefix = Path(__file__).resolve().parents[3]
        binary = str(prefix / "libexec" / "tcc" / "tcc-c")
    if not Path(binary).is_file():
        print("The native action is unavailable. Rerun ./install.sh.", file=sys.stderr)
        return
    subprocess.run([binary, "disk-free"], check=False)
