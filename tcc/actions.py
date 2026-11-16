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
import textwrap
from pathlib import Path

from . import __version__


def print_field(label: str, value: object) -> None:
    width = max(24, shutil.get_terminal_size((64, 24)).columns)
    label = str(label)
    max_label = max(6, width // 3)
    if len(label) > max_label:
        label = label[: max_label - 3] + "..."
    prefix = f"  {label}: "
    lines = textwrap.wrap(str(value), width=max(8, width - len(prefix))) or [""]
    print(prefix + lines[0])
    continuation = " " * len(prefix)
    for line in lines[1:]:
        print(continuation + line)


def format_bytes(value: int) -> str:
    amount = float(value)
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if amount < 1024 or unit == "TiB":
            return f"{amount:.1f} {unit}"
        amount /= 1024
    return f"{value} B"


def system_info(as_json: bool = False) -> int:
    payload = {
        "version": __version__,
        "os": f"{platform.system()} {platform.release()}",
        "machine": platform.machine(),
        "python": platform.python_version(),
        "termux": os.environ.get("PREFIX", "not detected"),
        "directory": str(Path.cwd()),
    }
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print("System information")
    print_field("Version", payload["version"])
    print_field("OS", payload["os"])
    print_field("Machine", payload["machine"])
    print_field("Python", payload["python"])
    print_field("Termux", payload["termux"])
    print_field("Directory", payload["directory"])
    return 0


def storage() -> None:
    usage = shutil.disk_usage(Path.cwd())
    used = usage.total - usage.free
    print_field("Storage", Path.cwd())
    print_field("Total", format_bytes(usage.total))
    print_field("Used", format_bytes(used))
    print_field("Free", format_bytes(usage.free))
    print_field("Usage", f"{used / usage.total * 100:.1f}%")


def environment() -> None:
    print("Termux environment")
    for key in ("PREFIX", "HOME", "SHELL", "PWD"):
        print_field(key, os.environ.get(key, "not set"))
    print_field("PATH entries", len(os.environ.get("PATH", "").split(os.pathsep)))


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
        print_field(str(path), f"{kind} ({resolved})")
    return 1 if missing else 0


def file_info(target: str = ".", as_json: bool = False) -> int:
    path = Path(target).expanduser()
    try:
        info = path.stat()
    except OSError as error:
        print(f"Cannot inspect {path}: {error}", file=sys.stderr)
        return 1
    kind = "directory" if path.is_dir() else "file" if path.is_file() else "other"
    payload = {
        "path": str(path.resolve()),
        "type": kind,
        "size": info.st_size,
        "mode": oct(info.st_mode & 0o777),
        "mtime": datetime.datetime.fromtimestamp(info.st_mtime).isoformat(timespec="seconds"),
    }
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 0
    print_field("Path", payload["path"])
    print_field("Type", payload["type"])
    print_field("Size", format_bytes(info.st_size))
    print_field("Mode", payload["mode"])
    print_field("Mtime", payload["mtime"])
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


def battery(as_json: bool = False) -> int:
    command = shutil.which("termux-battery-status")
    if command is None:
        print("Battery status is unavailable.")
        print("Install Termux:API and run: pkg install termux-api")
        return 1
    try:
        result = subprocess.run([command], capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
    except (OSError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"Could not read battery status: {error}", file=sys.stderr)
        return 1
    if as_json:
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0
    print("Battery status")
    for key in ("percentage", "status", "plugged", "temperature", "current"):
        if key in data:
            print(f"  {key.capitalize()}: {data[key]}")
    return 0


def clipboard(operation: str = "get", content: list[str] | None = None) -> int:
    if operation not in ("get", "set"):
        print(f"Unknown clipboard operation: {operation} (use get or set)", file=sys.stderr)
        return 2
    if operation == "set" and not content:
        print("clipboard set requires content: tcc clipboard set TEXT", file=sys.stderr)
        return 2
    command = shutil.which(f"termux-clipboard-{operation}")
    if command is None:
        print("Clipboard support is unavailable.")
        print("Install Termux:API and run: pkg install termux-api", file=sys.stderr)
        return 1
    if operation == "set":
        text = " ".join(content) if content else ""
        try:
            subprocess.run([command, text], capture_output=True, text=True, check=True)
        except (OSError, subprocess.CalledProcessError) as error:
            print(f"Could not write the clipboard: {error}", file=sys.stderr)
            return 1
        print("Clipboard updated.")
        return 0
    try:
        result = subprocess.run([command], capture_output=True, text=True, check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        print(f"Could not read the clipboard: {error}", file=sys.stderr)
        return 1
    print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    return 0


def command_output(commands: list[list[str]]) -> list[str]:
    for command in commands:
        executable = shutil.which(command[0])
        if executable is None:
            continue
        try:
            result = subprocess.run([executable, *command[1:]], capture_output=True, text=True, check=True)
        except (OSError, subprocess.CalledProcessError):
            continue
        return [line for line in result.stdout.splitlines() if line.strip()]
    return []


def ports() -> int:
    lines = command_output([["ss", "-lntu"], ["netstat", "-lntu"]])
    if not lines:
        print("No socket listing tool is available (try: pkg install iproute2).", file=sys.stderr)
        return 1
    print("Listening sockets")
    for line in lines[:20]:
        print(f"  {line}")
    if len(lines) > 20:
        print(f"  ... {len(lines) - 20} more")
    return 0


def processes() -> int:
    lines = command_output([["ps", "-A", "-o", "PID,USER,NAME"]],)
    if not lines:
        lines = command_output([["ps", "-A"]])
    if not lines:
        print("Process listing is unavailable.", file=sys.stderr)
        return 1
    print("Processes (first 20)")
    for line in lines[:21]:
        print(f"  {line}")
    if len(lines) > 21:
        print(f"  ... {len(lines) - 21} more")
    return 0


def native_action(command: str, *arguments: str) -> int:
    binary = os.environ.get("TCC_C_BINARY")
    if not binary:
        # Installed layout: $PREFIX/share/tcc/tcc/actions.py.
        prefix = Path(__file__).resolve().parents[3]
        binary = str(prefix / "libexec" / "tcc" / "tcc-c")
        if not Path(binary).is_file():
            # Development layout: a locally built binary next to the checkout.
            local = Path(__file__).resolve().parents[1] / "tcc-c"
            if local.is_file():
                binary = str(local)
    if not Path(binary).is_file():
        print("The native action is unavailable. Rerun ./install.sh.", file=sys.stderr)
        return 1
    result = subprocess.run([binary, command, *arguments], check=False)
    return result.returncode


def native_disk_free() -> int:
    return native_action("disk-free")


def native_mem_info() -> int:
    return native_action("mem-info")


def native_line_count(target: str) -> int:
    return native_action("line-count", target)


def native_tree(target: str = ".", depth: int | None = None) -> int:
    arguments = [target]
    if depth is not None:
        arguments += ["--depth", str(depth)]
    return native_action("tree", *arguments)
