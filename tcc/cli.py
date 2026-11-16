"""Command-line entry point for tcc."""

from __future__ import annotations

import argparse

from . import __project_name__, __version__
from . import actions
from .menu import Action, launch


def get_actions() -> list[Action]:
    return [
        ("system-info", "Show system and Termux information", "System", actions.system_info),
        ("environment", "Show useful Termux environment values", "System", actions.environment),
        ("storage", "Show storage usage for the current directory", "System", actions.storage),
        ("ports", "Show listening network sockets", "System", actions.ports),
        ("processes", "Show a compact process list", "System", actions.processes),
        ("battery", "Show battery status from Termux:API", "Device", actions.battery),
        ("clipboard", "Read or write the Android clipboard", "Device", lambda: actions.clipboard()),
        ("path-check", "Check whether the current path exists", "Files", actions.path_check),
        ("file-info", "Show metadata for the current directory", "Files", actions.file_info),
        ("checksum", "Hash the installed launcher", "Files", lambda: actions.checksum(__file__)),
        ("disk-free", "Show disk space using native C", "Native", actions.native_disk_free),
        ("mem-info", "Show native memory information", "Native", actions.native_mem_info),
        ("line-count", "Count lines in the launcher source", "Native", lambda: actions.native_line_count(__file__)),
        ("tree", "Show a compact directory tree", "Native", lambda: actions.native_tree()),
        ("exit", "Close the launcher", "Other", lambda: None),
    ]


def build_parser(action_names: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tcc", description="Termux CLI Collection")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("command", nargs="?", choices=action_names)
    parser.add_argument("target", nargs="*", help="path or file for path-check, file-info, or checksum; get/set for clipboard")
    parser.add_argument("--algorithm", default="sha256", help="checksum algorithm (default: sha256)")
    parser.add_argument("--depth", type=int, default=None, help="tree depth (default: 3)")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON output where supported")
    return parser


def main() -> int:
    action_list = get_actions()
    action_map = {name: action for name, _, _, action in action_list}
    parser = build_parser(list(action_map))
    args = parser.parse_args()

    if args.command is None:
        return launch(action_list, f"{__project_name__} {__version__}")
    if args.command == "battery":
        return actions.battery(args.json)
    elif args.command == "system-info":
        return actions.system_info(args.json)
    elif args.command == "path-check":
        return actions.path_check(args.target or ["."])
    elif args.command == "file-info":
        return actions.file_info(args.target[0] if args.target else ".", args.json)
    elif args.command == "checksum":
        if len(args.target) != 1:
            parser.error("checksum requires exactly one file path")
        return actions.checksum(args.target[0], args.algorithm)
    elif args.command == "clipboard":
        return actions.clipboard(args.target[0] if args.target else "get", args.target[1:])
    elif args.command == "line-count":
        if len(args.target) != 1:
            parser.error("line-count requires exactly one file path")
        return actions.native_line_count(args.target[0])
    elif args.command == "tree":
        return actions.native_tree(args.target[0] if args.target else ".", args.depth)
    else:
        result = action_map[args.command]()
        return result if isinstance(result, int) else 0
