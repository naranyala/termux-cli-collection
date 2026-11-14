# Termux CLI Collection (`tcc`)

A small collection of practical, shell-friendly command-line utilities for [Termux](https://termux.dev/). It combines Python for fast, portable actions with C for native POSIX/system actions.

The project is designed for everyday Android terminal workflows, experimentation, and learning. It does not require root access.

## Documentation

Detailed documentation is maintained in [`docs/`](docs/README.md):

- [Scope and design](docs/scope.md)
- [Installation and usage](docs/installation.md)
- [Action reference](docs/actions.md)
- [Interactive interface](docs/interface.md)
- [Architecture](docs/architecture.md)
- [Development and testing](docs/development.md)
- [Roadmap/TODOs](docs/TODOS.md)

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

## Current actions

| Command | Implementation | Description | Requirements |
|---|---|---|---|
| `tcc system-info` | Python | Shows OS, architecture, Python, Termux prefix, and current directory | Python 3 |
| `tcc environment` | Python | Shows useful Termux environment values | Python 3 |
| `tcc storage` | Python | Shows total, used, free, and percentage storage for the current directory | Python 3 |
| `tcc battery [--json]` | Python | Shows battery data from `termux-battery-status` | Termux:API app and `pkg install termux-api` |
| `tcc path-check [PATH ...]` | Python | Reports missing paths, files, directories, and symlinks | Python 3 |
| `tcc file-info [PATH]` | Python | Shows type, size, permissions, and modification time | Python 3 |
| `tcc checksum FILE` | Python | Calculates a streaming checksum, SHA-256 by default | Python 3 |
| `tcc ports` | Python | Shows listening network sockets when `ss` or `netstat` is available | Optional `iproute2` package |
| `tcc processes` | Python | Shows a compact process list | Termux `ps` |
| `tcc disk-free` | C | Shows native filesystem totals for the current directory | C compiler at install time |
| `tcc mem-info` | C | Shows available Linux memory statistics | C compiler at install time |
| `tcc line-count FILE` | C | Counts lines and bytes without loading the whole file | C compiler at install time |

Running `tcc` without a command opens the interactive launcher. `tcc --help` and `tcc --version` are also available.

## Installation

### Termux

From the project directory:

```sh
chmod +x install.sh
./install.sh
```

The installer:

1. copies the Python launcher and package to `$PREFIX/share/tcc`;
2. compiles the native C action when `cc` is available;
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
```

Install the optional battery integration with:

```sh
pkg install termux-api
```

The Termux:API Android application must also be installed for `tcc battery` to return data. Without it, the action prints an installation hint and exits safely.

### Updating

Pull or copy the latest source, then run the installer again:

```sh
git pull
./install.sh
```

The installer replaces the installed Python package and native binary.

## Interactive launcher navigation

Run:

```sh
tcc
```

Navigation supports:

- Termux Extra Keys `UP` and `DOWN` buttons;
- keyboard arrow keys;
- `w` / `s` and `k` / `j`;
- number keys for direct selection;
- `ENTER` to run an action;
- `/` to search actions;
- `?` to open keyboard help;
- `ESC` to clear search;
- `q` to quit.

The launcher uses a header, action list, selected-action detail panel, search mode, help overlay, and scrolling selection on larger screens. It adapts to small screens: it detects terminal width, uses a compact single-column layout below 72 columns, clips long titles, and shows the detail panel only when there is room.

To add native navigation buttons, edit `~/.termux/termux.properties`:

```text
extra-keys = [['ESC','UP','DOWN','ENTER','TAB','CTRL']]
```

Reload the Termux configuration or restart the session afterward.

When standard input or output is not a terminal, `tcc` uses a numbered prompt instead of raw keyboard mode, making it usable in simple scripts and tests.

## Repository layout

```text
.
├── main.py              # Small compatibility entry point
├── install.sh           # Installs tcc globally in Termux
├── docs/                # Project, action, interface, and development docs
├── tcc/
│   ├── __init__.py      # Project name and version
│   ├── cli.py           # Argument parsing and action registry
│   ├── menu.py          # Interactive and non-interactive picker
│   └── actions.py       # Python action implementations
├── main.c               # Compatibility C build entry point
└── csrc/
    ├── main.c           # Native C command dispatch
    ├── disk.c           # Filesystem statistics action
    ├── disk.h           # Disk action interface
    ├── system.c         # Memory and line-count actions
    └── system.h         # System action interface
```

See [`docs/architecture.md`](docs/architecture.md) for the detailed module responsibilities.

## Architecture

The launcher keeps the user interface separate from action implementations:

- `tcc.cli` defines the available action registry and direct command handling.
- `tcc.menu` owns terminal input, Termux button navigation, rendering, and fallback prompts.
- `tcc.actions` contains Python implementations and invokes installed native actions when needed.
- `csrc` contains independently compilable C code. The Python launcher calls the installed C binary through a narrow command interface.

To add a new action, implement it in the appropriate action module, register it in `tcc/cli.py`, and document it in the action table above.

## Development and testing

Run Python actions directly from the repository:

```sh
python main.py --help
python main.py system-info
python main.py storage
python main.py battery
python main.py disk-free
```

Check Python syntax:

```sh
python -m py_compile main.py tcc/*.py
```

Build and test the C action without installing it globally:

```sh
cc -Wall -Wextra -O2 csrc/main.c csrc/disk.c csrc/system.c -o tcc-c
./tcc-c --help
./tcc-c disk-free
rm tcc-c
```

The compatibility source can also be built with:

```sh
cc -Wall -Wextra -O2 main.c csrc/disk.c csrc/system.c -o tcc-c
```

## Contribution guidelines

New actions should:

1. have a narrow, clearly named purpose;
2. support direct invocation and launcher invocation;
3. provide useful output without destructive side effects;
4. return a meaningful non-zero status for invalid input or failures;
5. work without root whenever feasible;
6. document optional Termux packages and Android limitations;
7. keep modules small and avoid duplicating terminal or dispatch logic;
8. include a README entry and a simple manual test command.

## Roadmap

- add focused file and text utilities;
- add automated Python and C tests;
- improve machine-readable output options such as `--json`;
- document Android-version and Termux:API limitations;
- add packaging metadata as the collection grows.
