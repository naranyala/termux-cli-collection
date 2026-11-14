"""Small, dependency-free TUI for the Termux action launcher."""

from __future__ import annotations

import os
import select
import shutil
import sys
import textwrap
import time
from collections.abc import Callable

Action = tuple[str, str, Callable[[], None]]


def terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size((64, 20))
    return max(30, size.columns), max(10, size.lines)


def clip(value: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(value) <= width:
        return value
    return value[: max(0, width - 3)] + "..." if width >= 4 else value[:width]


def read_key() -> str:
    """Read one logical key, including Termux Extra Keys sequences."""
    fd = sys.stdin.fileno()
    first = os.read(fd, 1).decode("utf-8", errors="ignore")
    if first in ("\r", "\n"):
        return "ENTER"
    if first in ("\x7f", "\x08"):
        return "BACKSPACE"
    if first in ("q", "Q", "\x03"):
        return "QUIT"
    if first == "?":
        return "HELP"
    if first == "/":
        return "SEARCH"
    if first in ("w", "k", "\x10"):
        return "UP"
    if first in ("s", "j", "\x0e"):
        return "DOWN"
    if first == "\x1b":
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
        return "ESC"
    if first.isdigit():
        return f"NUMBER:{first}"
    if first.isprintable():
        return f"CHAR:{first}"
    return "OTHER"


def wait_for_return() -> None:
    print("\nPress Enter to return to the launcher...")
    sys.stdin.readline()


def draw_header(title: str, query: str, width: int, search_mode: bool) -> None:
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.write("=" * width + "\n")
    sys.stdout.write(clip(f"  {title}", width) + "\n")
    if search_mode:
        sys.stdout.write(clip(f"  Search: {query}_", width) + "\n")
    else:
        sys.stdout.write(clip("  Actions  |  / search  ? help  q quit", width) + "\n")
    sys.stdout.write("-" * width + "\n")


def draw_help(title: str, width: int) -> None:
    draw_header(title, "", width, False)
    lines = (
        "Keyboard help",
        "",
        "  UP/DOWN or w/s   Move selection",
        "  ENTER            Run selected action",
        "  1-9              Run action by number",
        "  /                Search actions",
        "  ESC              Clear search / close help",
        "  ?                Show this help",
        "  q                Quit",
        "",
        "Termux Extra Keys UP and DOWN buttons are supported.",
    )
    for line in lines:
        for wrapped in textwrap.wrap(line, width=max(12, width - 4)) or [""]:
            sys.stdout.write(clip(f"  {wrapped}", width) + "\n")
    sys.stdout.write("\nPress any key to return...\n")
    sys.stdout.flush()


def draw_actions(actions: list[Action], selected: int, query: str, width: int, height: int, search_mode: bool, title: str) -> None:
    draw_header(title, query, width, search_mode)
    if not actions:
        sys.stdout.write("  No actions match the search. Press ESC to clear it.\n")
        sys.stdout.flush()
        return

    compact = width < 52
    visible_rows = max(3, height - 7)
    start = max(0, min(selected - visible_rows + 1, len(actions) - visible_rows))
    end = min(len(actions), start + visible_rows)

    for index in range(start, end):
        name, description, _ = actions[index]
        marker = ">" if index == selected else " "
        if compact:
            line = f" {marker} {index + 1}. {name}"
            sys.stdout.write(clip(line, width) + "\n")
        else:
            label = f" {marker} {index + 1}. {name:<14}"
            sys.stdout.write(clip(label + description, width) + "\n")

    if not compact:
        name, description, _ = actions[selected]
        sys.stdout.write("\n" + "-" * width + "\n")
        sys.stdout.write(clip(f" Selected: {name}", width) + "\n")
        for line in textwrap.wrap(description, width=max(12, width - 4)):
            sys.stdout.write(clip(f"   {line}", width) + "\n")
    sys.stdout.write("\n" + clip("  UP/DOWN move  ENTER run  / search  ? help  q quit", width) + "\n")
    sys.stdout.flush()


def numbered_menu(actions: list[Action], title: str) -> int:
    width, _ = terminal_size()
    print(clip(f"{title} - choose an action", width))
    for number, (name, description, _) in enumerate(actions, 1):
        print(clip(f"  {number}. {name} - {description}", width))
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
    query = ""
    search_mode = False
    showing_help = False
    original = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        while True:
            filtered = [
                action for action in actions
                if not query or query.lower() in f"{action[0]} {action[1]}".lower()
            ]
            selected = min(selected, max(0, len(filtered) - 1))
            width, height = terminal_size()
            if showing_help:
                draw_help(title, width)
            else:
                draw_actions(filtered, selected, query, width, height, search_mode, title)

            key = read_key()
            if showing_help:
                if key in {"ESC", "HELP", "QUIT"}:
                    showing_help = False
                else:
                    showing_help = False
                continue
            if search_mode:
                if key == "ESC":
                    query = ""
                    search_mode = False
                elif key == "ENTER":
                    search_mode = False
                elif key == "BACKSPACE":
                    query = query[:-1]
                elif key.startswith("CHAR:"):
                    query += key[5:]
                elif key == "QUIT":
                    return 0
                elif key == "UP" and filtered:
                    selected = (selected - 1) % len(filtered)
                elif key == "DOWN" and filtered:
                    selected = (selected + 1) % len(filtered)
                continue
            if key == "UP" and filtered:
                selected = (selected - 1) % len(filtered)
            elif key == "DOWN" and filtered:
                selected = (selected + 1) % len(filtered)
            elif key == "SEARCH":
                search_mode = True
            elif key == "HELP":
                showing_help = True
            elif key == "QUIT":
                return 0
            elif key == "ESC":
                query = ""
            elif key == "ENTER" or key.startswith("NUMBER:"):
                if not filtered:
                    continue
                index = selected
                if key.startswith("NUMBER:"):
                    number = int(key[7:]) - 1
                    if number >= len(filtered):
                        continue
                    index = number
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original)
                filtered[index][2]()
                if filtered[index][0] == "exit":
                    return 0
                wait_for_return()
                tty.setraw(sys.stdin.fileno())
    except KeyboardInterrupt:
        return 130
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original)
