"""Small, dependency-free TUI for the Termux action launcher."""

from __future__ import annotations

import os
import select
import shutil
import sys
import textwrap
import time
from collections.abc import Callable

try:
    import termios
    import tty

    HAS_RAW_MODE = True
except ImportError:  # pragma: no cover - POSIX-only build environments
    HAS_RAW_MODE = False

Action = tuple[str, str, str, Callable[[], int | None]]


def terminal_size() -> tuple[int, int]:
    size = shutil.get_terminal_size((64, 20))
    return max(30, size.columns), max(10, size.lines)


def clip(value: str, width: int) -> str:
    if width <= 0:
        return ""
    if len(value) <= width:
        return value
    return value[: max(0, width - 3)] + "..." if width >= 4 else value[:width]


def read_key(search_mode: bool = False) -> str:
    """Read one logical key, including Termux Extra Keys sequences.

    In search mode, printable characters (including q, w, s, k, j, ?, and /)
    are returned as CHAR: keys so they can be typed into the query.
    """
    fd = sys.stdin.fileno()
    first = os.read(fd, 1).decode("utf-8", errors="ignore")
    if first in ("\r", "\n"):
        return "ENTER"
    if first in ("\x7f", "\x08"):
        return "BACKSPACE"
    if first == "\x03":
        return "QUIT"
    if not search_mode:
        if first in ("q", "Q"):
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
    if not search_mode and first.isdigit():
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
    elif width < 72:
        sys.stdout.write("  UP/DOWN  ENTER  / search  ? help  q\n")
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
        "  !category        Filter by category, e.g. !files",
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


def display_rows(filtered: list[Action]) -> list[tuple[int | None, str]]:
    """Group actions by category.

    Returns display rows as ``(action index, label)`` pairs. Header rows use
    ``None`` as the index so selection and number keys keep referring to the
    underlying filtered action list.
    """
    rows: list[tuple[int | None, str]] = []
    category = None
    for index, (name, _description, group, _action) in enumerate(filtered):
        if group != category:
            rows.append((None, group.upper()))
            category = group
        rows.append((index, name))
    return rows


def draw_actions(
    actions: list[Action],
    selected: int,
    query: str,
    width: int,
    height: int,
    search_mode: bool,
    title: str,
) -> None:
    draw_header(title, query, width, search_mode)
    if not actions:
        sys.stdout.write("  No actions match the search. Press ESC to clear it.\n")
        sys.stdout.flush()
        return

    # Keep the compact layout on phone-sized terminals even when the
    # terminal reports a moderately wide column count. It is more readable
    # than squeezing descriptions into a narrow action row.
    compact = width < 72
    # Very short terminals lose the detail panel and description column.
    tall = height >= 14
    visible_rows = max(3, height - 7)
    rows = display_rows(actions)
    selected_row = 0
    for row, (action_index, _label) in enumerate(rows):
        if action_index == selected:
            selected_row = row
            break
    start = max(0, min(selected_row - visible_rows + 1, len(rows) - visible_rows))
    end = min(len(rows), start + visible_rows)

    for row in range(start, end):
        action_index, label = rows[row]
        if action_index is None:
            sys.stdout.write(clip(f"  [{label}]", width) + "\n")
            continue
        name, description, _group, _action = actions[action_index]
        marker = ">" if action_index == selected else " "
        number = action_index + 1
        if compact:
            line = f" {marker} {number}. {name}"
            sys.stdout.write(clip(line, width) + "\n")
        else:
            line = f" {marker} {number}. {name:<14}"
            sys.stdout.write(clip(line + description, width) + "\n")

    if not compact and tall:
        name, description, _group, _action = actions[selected]
        sys.stdout.write("\n" + "-" * width + "\n")
        sys.stdout.write(clip(f" Selected: {name}", width) + "\n")
        for line in textwrap.wrap(description, width=max(12, width - 4)):
            sys.stdout.write(clip(f"   {line}", width) + "\n")
    footer = "  UP/DOWN  ENTER  /  ?  q" if compact else "  UP/DOWN move  ENTER run  / search  ? help  q quit"
    sys.stdout.write("\n" + clip(footer, width) + "\n")
    sys.stdout.flush()


def numbered_menu(actions: list[Action], title: str) -> int:
    width, _ = terminal_size()
    print(clip(f"{title} - choose an action", width))
    category = None
    for number, (name, description, group, _action) in enumerate(actions, 1):
        if group != category:
            print(clip(f"[{group}]", width))
            category = group
        print(clip(f"  {number}. {name} - {description}", width))
    choice = input("Choice: ").strip().lower()
    if choice in {"q", str(len(actions)), "exit"}:
        return 0
    if choice.isdigit() and 1 <= int(choice) < len(actions):
        result = actions[int(choice) - 1][3]()
        return result if isinstance(result, int) else 0
    print("Invalid choice.", file=sys.stderr)
    return 2


def filter_actions(actions: list[Action], query: str) -> list[Action]:
    """Filter actions by a search query.

    A query starting with ``!`` matches category names only (for example
    ``!files``); anything else matches name, category, and description.
    """
    if not query:
        return list(actions)
    if query.startswith("!"):
        category = query[1:].lower()
        return [action for action in actions if category in action[2].lower()]
    needle = query.lower()
    return [
        action for action in actions
        if needle in f"{action[0]} {action[2]} {action[1]}".lower()
    ]


def launch(actions: list[Action], title: str) -> int:
    if not sys.stdin.isatty() or not sys.stdout.isatty():
        return numbered_menu(actions, title)
    if os.environ.get("TERM", "") in ("", "dumb") or not HAS_RAW_MODE:
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
            filtered = filter_actions(actions, query)
            selected = min(selected, max(0, len(filtered) - 1))
            width, height = terminal_size()
            if showing_help:
                draw_help(title, width)
            else:
                draw_actions(filtered, selected, query, width, height, search_mode, title)

            key = read_key(search_mode=search_mode)
            if showing_help:
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
                    if number < 0 or number >= len(filtered):
                        continue
                    index = number
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original)
                result = filtered[index][3]()
                if filtered[index][0] == "exit":
                    return 0
                if isinstance(result, int) and result != 0:
                    print(f"Action exited with status {result}.")
                wait_for_return()
                tty.setraw(sys.stdin.fileno())
    except KeyboardInterrupt:
        return 130
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, original)
