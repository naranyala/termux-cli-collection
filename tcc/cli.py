"""Command-line entry point for tcc."""

from __future__ import annotations

import argparse

from . import __project_name__, __version__
from . import actions
from .menu import Action, launch


def get_actions() -> list[Action]:
    return [
        ("system-info", "Show system and Termux information", actions.system_info),
        ("storage", "Show storage usage for the current directory", actions.storage),
        ("battery", "Show battery status from Termux:API", actions.battery),
        ("disk-free", "Show disk space using native C", actions.native_disk_free),
        ("exit", "Close the launcher", lambda: None),
    ]


def build_parser(action_names: list[str]) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="tcc", description="Termux CLI Collection")
    parser.add_argument("--version", action="version", version=__version__)
    parser.add_argument("command", nargs="?", choices=action_names)
    return parser


def main() -> int:
    action_list = get_actions()
    action_map = {name: action for name, _, action in action_list}
    parser = build_parser(list(action_map))
    args = parser.parse_args()

    if args.command is None:
        return launch(action_list, f"{__project_name__} {__version__}")
    action_map[args.command]()
    return 0
