# Architecture

TCC separates command dispatch, terminal interaction, and action implementations.

```text
main.py
└── tcc/cli.py
    ├── tcc/menu.py
    └── tcc/actions.py

csrc/main.c
└── csrc/disk.c
    └── csrc/disk.h
```

## Python

- `main.py` is a small compatibility entry point.
- `tcc/__init__.py` stores project metadata.
- `tcc/cli.py` registers actions, parses direct commands, and starts the launcher.
- `tcc/menu.py` owns rendering, terminal width handling, key decoding, raw mode, and non-TTY fallback behavior.
- `tcc/actions.py` implements Python actions and invokes the installed native binary.

## C

- `csrc/main.c` handles native command dispatch and help/version output.
- `csrc/disk.c` implements filesystem statistics using `statvfs`.
- `csrc/system.c` implements `/proc/meminfo` and streaming line counting.
- `csrc/disk.h` and `csrc/system.h` expose native action interfaces.
- Root `main.c` is a compatibility build wrapper.

Build the native action with:

```sh
cc -Wall -Wextra -O2 csrc/main.c csrc/disk.c csrc/system.c -o tcc-c
```

## Adding an action

1. Implement the action in `tcc/actions.py` or the appropriate C module.
2. Add a `(name, description, callable)` entry in `tcc/cli.py`.
3. Add direct argument handling if the action needs paths or options.
4. Keep output narrow-screen-friendly and return useful error statuses.
5. Add the command to `docs/actions.md` and update the roadmap if needed.
6. Test both direct invocation and launcher selection.
