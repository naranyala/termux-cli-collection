# TCC Action Roadmap

This file tracks useful, safe, and small-screen-friendly actions for the Termux CLI Collection. Completed items are kept at the bottom for reference.

## Action design rules

Every action should:

- have one narrow purpose and a predictable command name;
- work without root whenever possible;
- support direct invocation and the interactive launcher;
- keep output readable on narrow terminals;
- avoid destructive behavior by default;
- return a non-zero status when it cannot complete;
- use only the standard Python library or existing Termux commands when practical;
- document optional packages and Android-specific limitations.

## Remaining work

### Release and packaging

Document version updates and eventually provide a repeatable package/release process for Termux users.

- Keep one version source of truth: `tcc/__init__.py` for Python, injected into the C build (removing the hardcoded `VERSION` in `csrc/main.c`).
- Add `pyproject.toml` with `[project.scripts] tcc = "tcc.cli:main"` so `pip install .` works without replacing `install.sh`, which remains the Termux-native path (it owns `libexec` placement and C compilation).
- Document a release checklist in `docs/development.md` (bump version, update README action table, tag `vX.Y.Z`).

### Extension ideas (unscheduled)

- More machine-readable `--json` coverage: `storage`, `ports`, `processes`.
- Focused file and text utilities (for example, duplicate-name or large-file finders).
- Action filtering by category in the launcher (`!system`, `!files`).
- Document Android-version and Termux:API limitations per action.

## Completed

### `tcc battery --json`

Machine-readable battery output via `--json`; compact human-readable default; handles a missing Termux:API with a hint and a non-zero status.

### `tcc environment`

Displays `PREFIX`, `HOME`, `SHELL`, `PWD`, and `PATH` entry count, one key/value per line, no secrets.

### `tcc path-check [PATH ...]`

Reports each path as missing, file, directory, or symlink (with target); returns non-zero when anything is missing.

### `tcc file-info PATH`

Type, size, permissions, modification time, and absolute path via `pathlib`/`stat`, plus `--json`.

### `tcc checksum FILE`

Streaming checksums with `--algorithm`; SHA-256 default; chunked reads for large files.

### `tcc ports`

Listening sockets via `ss`/`netstat`; clear hints when tools are missing; never requires root.

### `tcc processes`

Compact read-only process list with a `ps -o` fast path and a plain `ps` fallback.

### `tcc clipboard`

`get` and `set` operations through Termux:API; `set` requires explicit content; missing support exits `1`, usage errors exit `2`.

### `tcc line-count FILE`

Native streaming count of lines and bytes with clear errors for unreadable files.

### `tcc mem-info`

Memory statistics from `/proc/meminfo` with a clear unavailable fallback for non-Linux systems.

### `tcc tree PATH`

Native depth-limited directory tree: sorted entries, symlink-safe via `lstat`, permission warnings, `--depth` validated 1-16.

### Action categories

Launcher groups actions under `System`, `Device`, `Files`, and `Native` headers; number selection still refers to the filtered action list.

### Search actions

`/` opens search mode matching name, category, and description; all printable characters are typable; `ESC` clears; number selection keeps working.

### Terminal capability detection

`TERM=dumb`, empty `TERM`, missing `termios`, or non-TTY streams fall back to the numbered menu; short terminals hide the detail panel.

### Output formats

Diagnostics go to stderr, data to stdout; `--json` is supported by `battery`, `system-info`, and `file-info` with JSON-only stdout.

### Automated tests

`tests/` with stdlib `unittest`: formatting helpers, registry invariants, README consistency, action exit codes, non-TTY menu, and native build-and-run tests.

### CI checks

GitHub Actions runs Python compilation, the full test suite, and strict C compilation with `-Werror` on every push.
