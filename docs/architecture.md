# Architecture

TCC separates command dispatch, terminal interaction, and action implementations.

```text
main.py
└── tcc/cli.py          action registry + argparse
    ├── tcc/menu.py     launcher (interactive and numbered fallback)
    └── tcc/actions.py  Python actions + native binary bridge

csrc/main.c             native dispatch
├── csrc/disk.c         statvfs filesystem stats
├── csrc/system.c       /proc/meminfo, streaming line count
└── csrc/tree.c         depth-limited directory tree
```

## Python

- `main.py` is a small compatibility entry point.
- `tcc/__init__.py` stores project name and version.
- `tcc/cli.py` registers actions in a categorized registry of `(name, description, category, callable)` tuples, parses direct commands with `argparse`, and starts the launcher. Argument-taking actions (`path-check`, `file-info`, `checksum`, `clipboard`, `line-count`, `tree`, `battery`, `system-info`) are dispatched in dedicated branches so they can receive flags and targets.
- `tcc/menu.py` owns rendering, terminal size handling, key decoding (including Termux Extra Keys escape sequences), raw mode, category grouping, search, and the non-TTY / `TERM=dumb` / no-`termios` fallback to a numbered menu. It restores terminal state in a `finally` block around every action run.
- `tcc/actions.py` implements the Python actions, shared helpers (`print_field`, `format_bytes`), and the native bridge. Action callables return `int` exit codes or `None`.

## Native bridge

`tcc/actions.py:native_action()` locates the native binary in this order:

1. `$TCC_C_BINARY`, when set;
2. `$PREFIX/libexec/tcc/tcc-c` (installed layout);
3. `./tcc-c` next to the repository checkout (development layout).

It runs the binary with `subprocess.run(check=False)` and returns its exit code, which `tcc/cli.py` propagates to the shell.

## C

- `csrc/main.c` handles native command dispatch and help/version output. `tree [PATH] [--depth N]` parses its own options and validates depth (1-16).
- `csrc/disk.c` implements filesystem statistics using `statvfs`.
- `csrc/system.c` implements `/proc/meminfo` filtering and streaming line counting.
- `csrc/tree.c` implements the depth-limited directory tree: per-directory sorting, `lstat` (symlinks are shown but never followed, preventing cycles), permission warnings to stderr, Unicode connectors on TTYs and ASCII when piped, and a 1024-entry cap per directory.
- `csrc/disk.h`, `csrc/system.h`, and `csrc/tree.h` expose the action interfaces.
- Root `main.c` is a compatibility build wrapper that includes `csrc/main.c`.

Build the native actions with:

```sh
cc -Wall -Wextra -O2 csrc/main.c csrc/disk.c csrc/system.c csrc/tree.c -o tcc-c
```

## Tests and CI

`tests/` holds a standard-library `unittest` suite covering formatting helpers, registry invariants (unique names, contiguous categories, README consistency), action exit codes, the non-TTY menu, and a build-and-run pass over the native binary (skipped when no `cc` is available). GitHub Actions runs the same checks on every push via `.github/workflows/ci.yml`.

## Adding an action

1. Implement the action in `tcc/actions.py` (return an `int` exit code) or the appropriate C module under `csrc/`.
2. Add a `(name, description, category, callable)` entry in `tcc/cli.py` in the right category block, keeping categories contiguous.
3. Add direct argument handling in `tcc/cli.py:main()` if the action needs paths or options, and a generic flag in `build_parser()` if needed.
4. Keep output narrow-screen-friendly, send diagnostics to stderr, and return `1`/`2` for failure/usage errors.
5. Add the command to the README action table and `docs/actions.md`; the `tests/test_registry.py` consistency test fails if the README table is out of sync.
6. Add or extend tests in `tests/`, covering exit codes.
7. Test both direct invocation and launcher selection.
