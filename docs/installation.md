# Installation and Usage

## Requirements

- Termux with Python 3.
- A C compiler (`cc`, normally provided by the Termux `clang` package) for the native actions. Without it, the Python actions still work and native actions report that they are unavailable.
- Termux:API and the `termux-api` package only for battery and clipboard access:

  ```sh
  pkg install termux-api
  ```

  The Termux:API Android application must also be installed.

## Install globally

From the repository directory:

```sh
chmod +x install.sh
./install.sh
```

The installer copies the Python launcher and `tcc/` package to `$PREFIX/share/tcc`, builds the native C binary when `cc` is available, and installs:

```text
$PREFIX/bin/tcc
$PREFIX/libexec/tcc/tcc-c
$PREFIX/share/tcc/main.py
$PREFIX/share/tcc/tcc/
```

`$PREFIX/bin` is normally already on Termux's `PATH`.

## Verify

```sh
command -v tcc
tcc --version
tcc --help
tcc system-info
tcc disk-free
tcc tree docs --depth 2
```

## Use without installing

Every Python action runs straight from the repository:

```sh
python main.py system-info
python main.py tree docs        # uses ./tcc-c when built locally
```

Build the native binary next to the checkout to enable native actions in this mode:

```sh
cc -Wall -Wextra -O2 csrc/main.c csrc/disk.c csrc/system.c csrc/tree.c -o tcc-c
```

The launcher also works uninstalled, including the non-interactive fallback:

```sh
printf '1\n' | python main.py
```

## Update

Pull or copy new source and rerun the installer:

```sh
git pull
./install.sh
```

The installer replaces the installed Python package and native binary.

## Optional Termux:API support

`pkg install termux-api` plus the Termux:API app enables:

- `tcc battery` and `tcc battery --json`;
- `tcc clipboard get` and `tcc clipboard set TEXT`.

Without them, these actions print a helpful message and exit with status `1` (usage mistakes such as `clipboard set` without content exit `2`).

## Uninstall

Remove the installed files manually:

```sh
rm -f "$PREFIX/bin/tcc"
rm -rf "$PREFIX/share/tcc" "$PREFIX/libexec/tcc"
```
