# Development and Testing

## Python checks

Compile all Python modules:

```sh
python -m py_compile main.py tcc/*.py
```

Run representative actions:

```sh
python main.py system-info
python main.py environment
python main.py storage
python main.py path-check README.md
python main.py file-info README.md
python main.py checksum README.md
```

Test the non-TTY menu fallback:

```sh
printf '1\n' | python main.py
```

Test narrow output using a simulated width:

```sh
printf '1\n' | COLUMNS=32 python main.py
```

## C checks

Build with warnings enabled:

```sh
cc -Wall -Wextra -O2 csrc/main.c csrc/disk.c -o tcc-c
./tcc-c --help
./tcc-c disk-free
rm tcc-c
```

The compatibility wrapper can also be built with:

```sh
cc -Wall -Wextra -O2 main.c csrc/disk.c -o tcc-c
```

## Full local installation check

```sh
./install.sh
tcc --version
tcc system-info
tcc disk-free
```

## Style expectations

Keep modules focused, avoid duplicated terminal logic, use standard-library functionality where possible, and document optional Termux packages. New actions must not silently modify user data.
