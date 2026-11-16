# Termux CLI Collection (`tcc`)

[![CI](https://github.com/naranyala/termux-cli-collection/actions/workflows/ci.yml/badge.svg)](https://github.com/naranyala/termux-cli-collection/actions/workflows/ci.yml)

A small collection of practical, shell-friendly command-line utilities for [Termux](https://termux.dev/). It combines Python for fast, portable actions with C for native POSIX/system actions, and bundles everything behind a single global `tcc` command with an interactive launcher.

The project is designed for everyday Android terminal workflows, experimentation, and learning. It does not require root access.

- **14 actions** across system, device, file, and native categories;
- **interactive launcher** with search, categories, and small-screen support;
- **standard library only** on the Python side, plain POSIX on the C side;
- **script-friendly**: predictable exit codes, streaming output, optional JSON.

## Documentation

Detailed documentation is maintained in [`docs/`](docs/README.md):

- [Scope and design](docs/scope.md)
- [Installation and usage](docs/installation.md)
- [Action reference](docs/actions.md) — every action with examples and exit codes
- [Interactive interface](docs/interface.md) — launcher keys, layouts, fallbacks
- [Architecture](docs/architecture.md)
- [Development and testing](docs/development.md)
- [Roadmap/TODOs](docs/TODOS.md)

## Quick start

```sh
git clone <repository-url>
cd termux-cli-collection
./install.sh
tcc                 # interactive launcher
tcc system-info     # or run any action directly
```

## Scope

This project provides:

- focused utilities for system, storage, battery, file, text, and workflow tasks;
- an interactive launcher accessible globally as `tcc`;
- Python actions for rapid development and standard-library functionality;
- C actions where native system APIs or low overhead are useful;
- predictable command names, help output, and shell-friendly behavior;
- optional Termux integrations when their packages are installed.

### Out of scope

- replacing Termux or standard Unix commands;
- requiring root or a graphical desktop;
- destructive actions without explicit confirmation;
- malware, credential theft, or offensive-security automation;
- unnecessary dependencies or one large application framework.

## Actions

| Command | Implementation | Category | Description | Requirements |
|---|---|---|---|---|
| `tcc system-info [--json]` | Python | System | Shows OS, architecture, Python, Termux prefix, and current directory | Python 3 |
| `tcc environment` | Python | System | Shows useful Termux environment values | Python 3 |
| `tcc storage` | Python | System | Shows total, used, free, and percentage storage for the current directory | Python 3 |
| `tcc ports` | Python | System | Shows listening network sockets when `ss` or `netstat` is available | Optional `iproute2` package |
| `tcc processes` | Python | System | Shows a compact process list | Termux `ps` |
| `tcc battery [--json]` | Python | Device | Shows battery data from `termux-battery-status` | Termux:API app and `pkg install termux-api` |
| `tcc clipboard get` | Python | Device | Prints the Android clipboard content | Termux:API app and `pkg install termux-api` |
| `tcc clipboard set TEXT` | Python | Device | Replaces the Android clipboard content | Termux:API app and `pkg install termux-api` |
| `tcc path-check [PATH ...]` | Python | Files | Reports missing paths, files, directories, and symlinks | Python 3 |
| `tcc file-info [PATH] [--json]` | Python | Files | Shows type, size, permissions, and modification time | Python 3 |
| `tcc checksum FILE` | Python | Files | Calculates a streaming checksum, SHA-256 by default | Python 3 |
| `tcc disk-free` | C | Native | Shows native filesystem totals for the current directory | C compiler at install time |
| `tcc mem-info` | C | Native | Shows available Linux memory statistics | C compiler at install time |
| `tcc line-count FILE` | C | Native | Counts lines and bytes without loading the whole file | C compiler at install time |
| `tcc tree [PATH] [--depth N]` | C | Native | Shows a compact, depth-limited directory tree | C compiler at install time |

The launcher additionally exposes an `exit` entry that closes it.

## Command-line usage

```sh
tcc [--version] [--json] [--algorithm NAME] [--depth N] [COMMAND [TARGET ...]]
```

| Flag | Applies to | Description |
|---|---|---|
| `--version` | global | Print the `tcc` version |
| `--help` | global | Show the parser help |
| `--json` | `battery`, `system-info`, `file-info` | Print machine-readable JSON on stdout |
| `--algorithm NAME` | `checksum` | Any `hashlib` algorithm; default `sha256` |
| `--depth N` | `tree` | Tree depth, 1-16; default 3 |

Running `tcc` without a command opens the interactive launcher. Every action also works when piped: `tcc battery --json | python -m json.tool`.

### Exit codes

Actions are script-safe: they never prompt for input and always return a meaningful status.

| Code | Meaning |
|---|---|
| `0` | Success |
| `1` | The action could not complete (missing file, missing Termux:API, missing `ss`/`netstat`, native binary failure) |
| `2` | Usage error (unsupported checksum algorithm, `clipboard` without content, invalid native arguments, invalid menu choice) |
| `130` | Interrupted by `Ctrl-C` in the launcher |

### Environment variables

| Variable | Description |
|---|---|
| `TCC_C_BINARY` | Overrides the path to the native binary; otherwise `$PREFIX/libexec/tcc/tcc-c` is used, falling back to a locally built `./tcc-c` next to the repository |
| `PREFIX` | Termux prefix, used to locate installed files |
| `TERM` | `dumb` or empty forces the plain numbered menu instead of the full-screen launcher |

## Installation

### Termux

From the project directory:

```sh
chmod +x install.sh
./install.sh
```

The installer:

1. copies the Python launcher and package to `$PREFIX/share/tcc`;
2. compiles the native C actions when `cc` is available;
3. installs the global command at `$PREFIX/bin/tcc`;
4. installs the native binary at `$PREFIX/libexec/tcc/tcc-c`.

Termux's `$PREFIX/bin` is normally already on `PATH`, so verify the installation with:

```sh
command -v tcc
tcc --version
tcc --help
tcc system-info
tcc environment
tcc storage
tcc battery --json
tcc path-check "$HOME"
tcc file-info README.md
tcc checksum README.md
tcc ports
tcc processes
tcc disk-free
tcc mem-info
tcc line-count README.md
tcc tree docs --depth 2
```

Install the optional Termux:API integrations (battery, clipboard) with:

```sh
pkg install termux-api
```

The Termux:API Android application must also be installed for `tcc battery` and `tcc clipboard` to return data. Without it, those actions print an installation hint and exit with status 1.

### Updating

Pull or copy the latest source, then run the installer again:

```sh
git pull
./install.sh
```

The installer replaces the installed Python package and native binary.

### Uninstalling

```sh
rm -f "$PREFIX/bin/tcc"
rm -rf "$PREFIX/share/tcc" "$PREFIX/libexec/tcc"
```

## Interactive launcher

Run:

```sh
tcc
```

Actions are grouped into categories (`System`, `Device`, `Files`, `Native`), and the launcher supports:

- Termux Extra Keys `UP` and `DOWN` buttons;
- keyboard arrow keys, or `w` / `s` and `k` / `j`;
- number keys for direct selection;
- `ENTER` to run an action;
- `/` to search actions by name, category, or description;
- `?` to open keyboard help;
- `ESC` to clear search or close help;
- `q` (or `Ctrl-C`) to quit.

The launcher uses a header, a selected-action detail panel, search mode, a help overlay, and scrolling selection on larger screens. It adapts to small screens: it detects terminal width and height, uses a compact single-column layout below 72 columns, clips long titles, and shows the detail panel only when there is room. Terminals without ANSI support (such as `TERM=dumb`) fall back to a plain numbered menu.

To add native navigation buttons, edit `~/.termux/termux.properties`:

```text
extra-keys = [['ESC','UP','DOWN','ENTER','TAB','CTRL']]
```

Reload the Termux configuration or restart the session afterward.

When standard input or output is not a terminal, `tcc` uses a numbered prompt instead of raw keyboard mode, making it usable in simple scripts and tests:

```sh
printf '1\n' | tcc
```

## Repository layout

```text
.
├── main.py              # Small compatibility entry point
├── install.sh           # Installs tcc globally in Termux
├── docs/                # Project, action, interface, and development docs
├── tests/               # Python and native C test suite
├── .github/workflows/   # CI workflow
├── tcc/
│   ├── __init__.py      # Project name and version
│   ├── cli.py           # Argument parsing and categorized action registry
│   ├── menu.py          # Interactive and non-interactive picker
│   └── actions.py       # Python action implementations
├── main.c               # Compatibility C build entry point
└── csrc/
    ├── main.c           # Native C command dispatch
    ├── disk.c           # Filesystem statistics action
    ├── disk.h           # Disk action interface
    ├── system.c         # Memory and line-count actions
    ├── system.h         # System action interface
    ├── tree.c           # Depth-limited directory tree action
    └── tree.h           # Tree action interface
```

See [`docs/architecture.md`](docs/architecture.md) for the detailed module responsibilities.

## Architecture

The launcher keeps the user interface separate from action implementations:

- `tcc.cli` defines the categorized action registry and direct command handling.
- `tcc.menu` owns terminal input, key decoding (including Termux Extra Keys sequences), rendering, and fallback prompts.
- `tcc.actions` contains Python implementations and invokes the native binary through a narrow command interface.
- `csrc` contains independently compilable C code with no shared state.

To add a new action, implement it in the appropriate action module, register it in `tcc/cli.py`, and document it in the action table above. The full checklist is in [`docs/architecture.md`](docs/architecture.md).

## Development and testing

Run Python actions directly from the repository without installing:

```sh
python main.py --help
python main.py system-info
python main.py storage
python main.py battery
python main.py disk-free     # uses ./tcc-c when built locally
```

Check Python syntax:

```sh
python -m py_compile main.py tcc/*.py
```

Build and test the C actions without installing them globally:

```sh
cc -Wall -Wextra -O2 csrc/main.c csrc/disk.c csrc/system.c csrc/tree.c -o tcc-c
./tcc-c --help
./tcc-c disk-free
rm tcc-c
```

The compatibility source can also be built with:

```sh
cc -Wall -Wextra -O2 main.c csrc/disk.c csrc/system.c csrc/tree.c -o tcc-c
```

Run the full test suite (40 tests; builds the native binary when `cc` is available):

```sh
python -m unittest discover -s tests -t .
```

Continuous integration runs the same checks on every push; see [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

## Contribution guidelines

New actions should:

1. have a narrow, clearly named purpose;
2. support direct invocation and launcher invocation;
3. provide useful output without destructive side effects;
4. return a meaningful non-zero status for invalid input or failures;
5. work without root whenever feasible;
6. document optional Termux packages and Android limitations;
7. keep modules small and avoid duplicating terminal or dispatch logic;
8. include a README table entry, a `docs/actions.md` section, and tests.

## Roadmap

Completed and planned work is tracked in [`docs/TODOS.md`](docs/TODOS.md). Remaining highlights:

- packaging metadata and a repeatable release process;
- more machine-readable `--json` coverage (`storage`, `ports`);
- focused file and text utilities.
