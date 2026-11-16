# Action Reference

All commands are available through the launcher and as direct commands. Run `tcc --help` for the current parser output.

Actions are read-only unless stated otherwise. They never prompt for input, which makes them safe for scripts and pipes.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | The action could not complete (missing path, missing package, missing tool, native failure) |
| `2` | Usage error (bad algorithm, missing required argument, invalid native arguments) |

## `system-info`

```sh
tcc system-info
tcc system-info --json
```

Shows TCC version, operating system, Android architecture, Python version, Termux prefix, and current directory. `--json` prints the same fields as a JSON object.

## `environment`

```sh
tcc environment
```

Shows useful non-secret environment values: `PREFIX`, `HOME`, `SHELL`, `PWD`, and the number of `PATH` entries.

## `storage`

```sh
tcc storage
```

Reports total, used, free, and percentage storage for the filesystem containing the current directory, in human-readable units.

## `battery`

```sh
tcc battery
tcc battery --json
```

Calls `termux-battery-status`. The default output is compact and human-readable; `--json` preserves the structured data for scripts.

Requires the Termux:API app and `pkg install termux-api`. Without them it prints an installation hint and exits `1`.

## `clipboard`

```sh
tcc clipboard get
tcc clipboard set "text to copy"
```

Reads or writes the Android clipboard through Termux:API.

- `get` prints the current clipboard content.
- `set` requires explicit content; it never reads the clipboard as a side effect and always replaces the whole content.
- Use `--` before content that starts with a dash.

Requires the Termux:API app and `pkg install termux-api`. Missing support exits `1`; an unknown operation or missing content exits `2`.

## `path-check`

```sh
tcc path-check README.md main.py "$HOME"
```

Reports whether each path is missing, a file, a directory, or a symlink (with its target). It returns `1` if any requested path is missing.

## `file-info`

```sh
tcc file-info README.md
tcc file-info "$HOME"
tcc file-info README.md --json
```

Shows absolute path, type, size, permissions, and modification time. The default target is the current directory. `--json` prints the same fields as a JSON object. Inspecting an unreadable or missing path exits `1`.

## `checksum`

```sh
tcc checksum README.md
tcc checksum --algorithm md5 README.md
```

Streams a file through a checksum algorithm in chunks, so large files never load fully into memory. SHA-256 is the default; any algorithm available through Python's `hashlib` can be selected with `--algorithm`. Output is `<digest>  <path>` for easy piping. An unsupported algorithm exits `2`; an unreadable file exits `1`.

## `ports`

```sh
tcc ports
```

Lists listening sockets using `ss` or `netstat`. Output is capped at 20 lines with a summary line for the rest. Install `iproute2` if neither command is available:

```sh
pkg install iproute2
```

Without any socket tool it prints a hint to stderr and exits `1`.

## `processes`

```sh
tcc processes
```

Shows a compact, read-only process listing using Termux `ps`, capped at 20 entries. It never signals or terminates processes. When `ps` is unavailable it exits `1`.

## `disk-free`

```sh
tcc disk-free
```

Runs the installed native C action and reports total, used, and available bytes for the filesystem of the current directory, using `statvfs`.

## `mem-info`

```sh
tcc mem-info
```

Reads selected memory statistics (total, available, free, swap) from `/proc/meminfo` through the native C action. It reports a clear error on systems without that interface.

## `line-count`

```sh
tcc line-count README.md
```

Streams a file through the native C action and reports newline count and byte count without loading the whole file into memory. Missing or unreadable files exit `1`.

## `tree`

```sh
tcc tree
tcc tree docs --depth 2
tcc tree --depth 1 "$HOME"
```

Renders a compact, sorted directory tree using native POSIX directory APIs.

- Depth defaults to `3` and accepts `1`-`16`; out-of-range values exit `2`.
- Symlinks are shown but never followed, so cycles are impossible.
- Directories are suffixed with `/`.
- Entries are sorted alphabetically per directory.
- Permission errors print a warning to stderr and continue; the tree still succeeds.
- Connectors use Unicode box drawing on a TTY and ASCII (`|--`, `` `-- ``) when piped.
