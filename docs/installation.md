# Installation and Usage

## Requirements

- Termux with Python 3.
- A C compiler (`cc`, normally provided by the Termux `clang` package) for the native action.
- Termux:API and the `termux-api` package only for battery access.

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
```

## Update

Pull or copy new source and rerun the installer:

```sh
git pull
./install.sh
```

## Optional battery support

Install the Termux:API package and Android application:

```sh
pkg install termux-api
```

Without Termux:API, `tcc battery` prints a helpful message and does not crash.

## Uninstall

Remove the installed files manually:

```sh
rm -f "$PREFIX/bin/tcc"
rm -rf "$PREFIX/share/tcc" "$PREFIX/libexec/tcc"
```
