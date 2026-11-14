"""Command-line entry point for tcc."""

from __future__ import annotations

import argparse
from pathlib import Path

from . import __project_name__, __version__
from . import actions
from .menu import Action, launch


def get_actions() -> list[Action]:
    return [
        ("system-info", "Show system and Termux information", actions.system_info),
        ("environment", "Show useful Termux environment values", actions.environment),
        ("storage", "Show storage usage for the current directory", actions.storage),
        ("battery", "Show battery status from Termux:API", actions.battery),
        ("path-check", "Check whether the current path exists", actions.path_check),
        ("file-info", "Show metadata for the current directory", actions.file_info),
        ("checksum", "Hash the installed launcher", lambda: actions.checksum(__file__)),
        ("disk-free", "Show disk space using native C", actions.native_disk_free),
        ("exit", "Close the launcher", lambda: None),
    ]


def build_parser(action_names: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tcc", description="Termux CLI Collection")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("command", nargs="?", choices=action_names)
    parser.add_argument("target", nargs="*", help="path or file for path-check, file-info, or checksum")
    parser.add_argument("--algorithm", default="sha256", help="checksum algorithm (default: sha256)")
    parser.add_argument("--json", action="store_true", help="print battery data as JSON")
    return parser


def main() -> int:
    action_list = get_actions()
    action_map = {name: action for name, _, action in action_list}
    parser = build_parser(list(action_map))
    args = parser.parse_args()

    if args.command is None:
        return launch(action_list, f"{__project_name__} {__version__}")
    if args.command == "battery":
        actions.battery(args.json)
    elif args.command == "path-check":
        return actions.path_check(args.target or ["."])
    elif args.command == "file-info":
        return actions.file_info(args.target[0] if args.target else ".")
    elif args.command == "checksum":
        if len(args.target) != 1:
            parser.error("checksum requires exactly one file path")
        return actions.checksum(args.target[0], args.algorithm)
    else:
        action_map[args.command]()
    return 0
