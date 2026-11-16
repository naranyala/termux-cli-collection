# Development and Testing

## Requirements

- Python 3 for the launcher and test suite (standard library only).
- A C compiler for the native actions; native tests are skipped automatically when `cc` is missing.

## Python checks

Compile all Python modules:

```sh
python -m py_compile main.py tcc/*.py
```

Run the full test suite from the repository root:

```sh
python -m unittest discover -s tests -t .
```

The suite covers:

- byte and text formatting helpers;
- registry invariants (unique names, callable entries, contiguous categories, README table consistency);
- action behavior and exit codes against temporary files;
- the non-TTY numbered menu and category display;
- building and running the native binary, including error exit codes.

Run representative actions:

```sh
python main.py system-info
python main.py environment
python main.py storage
python main.py path-check README.md
python main.py file-info README.md --json
python main.py checksum README.md
python main.py ports
python main.py processes
python main.py tree docs --depth 2
```

Test the non-TTY menu fallback:

```sh
printf '1\n' | python main.py
```

Test the `TERM=dumb` fallback:

```sh
printf '1\n' | TERM=dumb python main.py
```

Test narrow output using a simulated width:

```sh
printf '1\n' | COLUMNS=32 python main.py
```

## C checks

Build with warnings enabled:

```sh
cc -Wall -Wextra -O2 csrc/main.c csrc/disk.c csrc/system.c csrc/tree.c -o tcc-c
./tcc-c --help
./tcc-c disk-free
rm tcc-c
```

Strict warnings (what CI uses):

```sh
cc -Wall -Wextra -Werror -O2 csrc/main.c csrc/disk.c csrc/system.c csrc/tree.c -o tcc-c
```

The compatibility wrapper can also be built with:

```sh
cc -Wall -Wextra -O2 main.c csrc/disk.c csrc/system.c csrc/tree.c -o tcc-c
```

## CI

`.github/workflows/ci.yml` runs on every push and pull request:

1. `python -m py_compile main.py tcc/*.py`;
2. `python -m unittest discover -s tests -t . -v`;
3. strict C compilation with `-Wall -Wextra -Werror` followed by `./tcc-c --help`.

## Full local installation check

```sh
./install.sh
tcc --version
tcc system-info
tcc disk-free
tcc tree docs --depth 2
```

## Style expectations

Keep modules focused, avoid duplicated terminal logic, use standard-library functionality where possible, and document optional Termux packages. New actions must not silently modify user data. Actions return integer exit codes (`0` success, `1` failure, `2` usage error) and the registry in `tcc/cli.py` stays grouped by category.
