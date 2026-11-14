"""Actions exposed by the tcc launcher."""

from __future__ import annotations

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


def battery() -> None:
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
