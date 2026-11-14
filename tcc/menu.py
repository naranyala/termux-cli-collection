"""Termux-friendly interactive action picker."""

from __future__ import annotations

import os
import select
import shutil
import sys
import textwrap
import time
from collections.abc import Callable

Action = tuple[str, str, Callable[[], None]]


def screen_width() -> int:
    return max(24, shutil.get_terminal_size((64, 24)).columns)


def clipped(value: str, width: int) -> str:
    if len(value) <= width:
        return value
    if width < 4:
        return value[:width]
    return value[: width - 3] + "..."


def draw(actions: list[Action], selected: int, title: str) -> None:
    width = screen_width()
    name_width = min(14, max(len(name) for name, _, _ in actions))
    description_width = width - name_width - 9
    compact = width < 48

    sys.stdout.write("\033[2J\033[H")
    sys.stdout.write(clipped(title, width) + "\n")
    if compact:
        sys.stdout.write("UP/DOWN  ENTER  q\n\n")
    else:
        sys.stdout.write("UP/DOWN, w/s, numbers, ENTER, or q\n\n")

    for number, (name, description, _) in enumerate(actions):
        pointer = ">" if number == selected else " "
        label = f" {pointer} {number + 1}. {name:<{name_width}}"
        if compact:
            sys.stdout.write(clipped(label, width) + "\n")
            continue
        lines = textwrap.wrap(description, width=max(12, description_width)) or [""]
        sys.stdout.write(label + clipped(lines[0], max(1, description_width)) + "\n")
        for continuation in lines[1:]:
            sys.stdout.write(" " * (name_width + 7) + clipped(continuation, max(1, description_width)) + "\n")
    sys.stdout.flush()


def read_key() -> str:
    fd = sys.stdin.fileno()
    first = os.read(fd, 1).decode("utf-8", errors="ignore")
    if first in ("\r", "\n"):
        return "ENTER"
    if first in ("q", "Q", "\x03"):
        return "QUIT"
    if first in ("w", "k", "\x10"):
        return "UP"
    if first in ("s", "j", "\x0e"):
        return "DOWN"
    if first.isdigit():
        return first
    if first != "\x1b":
        return "OTHER"

    sequence = first
    deadline = time.monotonic() + 0.15
    while len(sequence) < 3 and time.monotonic() < deadline:
        ready, _, _ = select.select([fd], [], [], 0.03)
        if ready:
            sequence += os.read(fd, 1).decode("utf-8", errors="ignore")
        else:
            break
    if sequence in ("\x1b[A", "\x1bOA"):
        return "UP"
    if sequence in ("\x1b[B", "\x1bOB"):
        return "DOWN"
    return "OTHER"


def wait_for_return() -> None:
    print("\nPress Enter to return to the menu...")
    sys.stdin.readline()


def numbered_menu(actions: list[Action], title: str) -> int:
    width = screen_width()
    print(clipped(f"{title} - choose an action", width))
    for number, (name, description, _) in enumerate(actions, 1):
        print(clipped(f"  {number}. {name} - {description}", width))
    choice = input("Choice: ").strip().lower()
    if choice in {"q", str(len(actions)), "exit"}:
        return 0
    if choice.isdigit() and 1 <= int(choice) < len(actions):
        actions[int(choice) - 1][2]()
        return 0
    print("Invalid choice.", file=sys.stderr)
    return 2


def launch(actions: list[Action], title: str) -> int:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return numbered_menu(actions, title)

    import termios
    import tty

    selected = 0
    original = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            draw(actions, selected, title)
            key = read_key()
            if key == "UP":
                selected = (selected - 1) % len(actions)
            elif key == "DOWN":
                selected = (selected + 1) % len(actions)
            elif key == "QUIT":
                return 0
            elif key == "ENTER" or (key.isdigit() and 1 <= int(key) <= len(actions)):
                index = selected if key == "ENTER" else int(key) - 1
                actions[index][2]()
                if index == len(actions) - 1:
                    return 0
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original)
                wait_for_return()
                tty.setraw(sys.stdin.fileno())
    except KeyboardInterrupt:
        return 130
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original)
