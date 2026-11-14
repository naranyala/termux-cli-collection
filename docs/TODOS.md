# TCC Action Roadmap

This file tracks useful, safe, and small-screen-friendly actions for the Termux CLI Collection.

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

## High priority

### [x] `tcc battery --json`

Add machine-readable output to the existing battery action.

- Reuse `termux-battery-status`.
- Add an optional `--json` mode for shell scripts.
- Keep the default output compact and human-readable.
- Handle missing Termux:API without a traceback.

### [x] `tcc environment`

Show useful Termux environment information.

- Display `PREFIX`, `HOME`, `PATH`, shell, and current directory.
- Redact values that may contain secrets.
- Use one key/value per line for small screens.

### [x] `tcc path-check [PATH ...]`

Inspect paths without changing anything.

- Report whether each path exists.
- Identify file, directory, symlink, or missing path.
- Show readable size for regular files.
- Return non-zero if any requested path is missing.

### [x] `tcc file-info PATH`

Show metadata for one file or directory.

- Type, size, permissions, modified time, and absolute path.
- Use Python's `pathlib` and `stat` modules.
- Never modify the target.

## Medium priority

### [x] `tcc checksum FILE`

Calculate a file checksum.

- Support SHA-256 by default.
- Add `--algorithm` with safe standard algorithms.
- Read files in chunks to support large files.
- Keep output easy to pipe into scripts.

### [x] `tcc ports`

Show listening TCP/UDP sockets when available.

- Prefer existing Termux/POSIX tools instead of parsing privileged data directly.
- Clearly report when Android permissions or `/proc` access limit results.
- Avoid requiring root.

### [x] `tcc processes`

Show a compact process summary.

- Use `ps` when available.
- Support a compact default suitable for phones.
- Add optional name filtering.
- Do not terminate or signal processes.

### [ ] `tcc clipboard`

Read and write clipboard content through Termux:API.

- Separate `get` and `set` operations.
- Require explicit content for writes.
- Never print clipboard content unless requested.
- Document `pkg install termux-api` and the Android app requirement.

## Native C actions

### [ ] `tcc tree PATH`

Create a compact native directory listing.

- Use POSIX directory APIs.
- Limit recursion depth by default.
- Add a safe `--depth` option.
- Gracefully handle permission errors.

### [x] `tcc line-count FILE`

Count lines in a file using a streaming C implementation.

- Avoid loading the entire file into memory.
- Report bytes and lines.
- Return clear errors for binary or unreadable files.

### [x] `tcc mem-info`

Report memory information from available POSIX/Linux interfaces.

- Use `/proc/meminfo` only when available.
- Keep a clear unavailable fallback for non-Linux systems.
- Format values in human-readable units.

## Launcher and interface

### [ ] Action categories

Group actions into compact launcher sections such as `System`, `Files`, `Device`, and `Native` without making navigation difficult on small screens.

### [ ] Search actions

Add a launcher search mode activated by `/`.

- Filter by action name and description.
- Keep number selection available.
- Work without external UI libraries.

### [ ] Terminal capability detection

Improve behavior for terminals without ANSI support.

- Avoid screen-clearing escape sequences when unsupported.
- Fall back to a plain numbered menu.
- Detect narrow height as well as narrow width.

### [ ] Output formats

Standardize optional `--json` output where an action is useful in scripts.

- Keep human-readable output as the default.
- Never mix status text into JSON on stdout.
- Send diagnostics to stderr.

## Quality and maintenance

### [ ] Automated tests

Add tests for:

- byte formatting;
- action registration;
- path and error handling;
- narrow-width menu rendering;
- C action build and exit codes.

### [ ] CI checks

Add a lightweight workflow that runs:

- Python syntax checks;
- Python tests;
- strict C compilation with warnings enabled;
- README and TODO consistency checks where practical.

### [ ] Release and packaging

Document version updates and eventually provide a repeatable package/release process for Termux users.
