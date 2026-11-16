# Scope and Design

## Purpose

TCC is a collection of practical, safe, shell-friendly utilities for Termux on Android. It combines Python actions for fast development with C actions for native POSIX/system functionality.

The project is intended for everyday terminal workflows, experimentation, and learning. It is not a replacement for Termux, package management, or standard Unix utilities.

## In scope

- System, environment, storage, battery, clipboard, file, and text utilities.
- Unprivileged operation whenever possible.
- Direct commands that work in scripts, with predictable exit codes.
- An interactive launcher for phone-sized screens with search and categories.
- Optional Termux integrations with clear package requirements.
- Machine-readable output (`--json`) where it helps scripting.
- Small modules with predictable output and exit codes.

## Out of scope

- Root-only requirements or graphical interfaces.
- Destructive behavior without explicit confirmation.
- Malware, credential theft, or offensive-security automation.
- Unnecessary third-party dependencies (Python side: standard library only; C side: plain POSIX).
- A large framework that hides individual utility behavior.

## Action requirements

Every action should:

- have one clear purpose and a predictable command name;
- be safe by default and never modify data without explicit instruction;
- support both launcher and direct invocation;
- document optional Termux packages and Android limitations;
- remain readable on narrow terminals;
- exit `0` on success, `1` when the task cannot complete, and `2` on usage errors;
- use only the standard Python library or existing Termux/POSIX commands.

## Layering rules

- The launcher (`tcc/menu.py`) never implements actions; it only selects and runs registry entries.
- Actions never touch terminal state; the launcher owns raw mode and restores it around every action.
- Python actions call native C functionality only through the installed `tcc-c` binary, never by re-implementing terminal or dispatch logic.
