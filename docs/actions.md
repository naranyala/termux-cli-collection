# Action Reference

All commands are available through the launcher and as direct commands. Run `tcc --help` for the current parser output.

## `system-info`

```sh
tcc system-info
```

Shows TCC version, operating system, Android architecture, Python version, Termux prefix, and current directory.

## `environment`

```sh
tcc environment
```

Shows useful non-secret environment values: `PREFIX`, `HOME`, `SHELL`, `PWD`, and the number of `PATH` entries.

## `storage`

```sh
tcc storage
```

Reports total, used, free, and percentage storage for the filesystem containing the current directory.

## `battery`

```sh
tcc battery
tcc battery --json
```

Calls `termux-battery-status`. The default output is compact and human-readable; `--json` preserves structured data for scripts.

## `path-check`

```sh
tcc path-check README.md main.py "$HOME"
```

Reports whether each path is missing, a file, a directory, or a symlink. It returns a non-zero status if any path is missing.

## `file-info`

```sh
tcc file-info README.md
tcc file-info "$HOME"
```

Shows absolute path, type, size, permissions, and modification time. The default target is the current directory.

## `checksum`

```sh
tcc checksum README.md
tcc checksum --algorithm md5 README.md
```

Streams a file through a checksum algorithm. SHA-256 is the default; algorithms available through Python's `hashlib` can be selected with `--algorithm`.

## `ports`

```sh
tcc ports
```

Lists listening sockets using `ss` or `netstat`. Install `iproute2` if neither command is available:

```sh
pkg install iproute2
```

## `processes`

```sh
tcc processes
```

Shows a compact, read-only process listing using Termux `ps`.

## `disk-free`

```sh
tcc disk-free
```

Runs the installed native C action and reports total, used, and available bytes for the current filesystem.

## `mem-info`

```sh
tcc mem-info
```

Reads selected memory statistics from `/proc/meminfo` through the native C action. It reports a clear error on systems without that interface.

## `line-count`

```sh
tcc line-count README.md
```

Streams a file through the native C action and reports newline count and byte count.
