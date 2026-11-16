#!/data/data/com.termux/files/usr/bin/bash
# Install the collection's global `tcc` command.
set -eu

PREFIX="${PREFIX:-/data/data/com.termux/files/usr}"
ROOT="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
INSTALL_DIR="$PREFIX/share/tcc"
LIBEXEC_DIR="$PREFIX/libexec/tcc"
COMMAND_PATH="$PREFIX/bin/tcc"

mkdir -p "$INSTALL_DIR" "$LIBEXEC_DIR" "$PREFIX/bin"
cp "$ROOT/main.py" "$INSTALL_DIR/main.py"
rm -rf "$INSTALL_DIR/tcc"
cp -R "$ROOT/tcc" "$INSTALL_DIR/tcc"
chmod 755 "$INSTALL_DIR/main.py"

if command -v cc >/dev/null 2>&1; then
    cc -Wall -Wextra -O2 "$ROOT/csrc/main.c" "$ROOT/csrc/disk.c" "$ROOT/csrc/system.c" "$ROOT/csrc/tree.c" -o "$LIBEXEC_DIR/tcc-c"
    chmod 755 "$LIBEXEC_DIR/tcc-c"
    C_STATUS="installed"
else
    rm -f "$LIBEXEC_DIR/tcc-c"
    C_STATUS="skipped (install clang to enable C actions)"
fi

cat > "$COMMAND_PATH" <<LAUNCHER
#!/data/data/com.termux/files/usr/bin/sh
exec python3 "$INSTALL_DIR/main.py" "\$@"
LAUNCHER
chmod 755 "$COMMAND_PATH"

printf 'Installed tcc to %s\n' "$COMMAND_PATH"
printf 'C actions: %s\n' "$C_STATUS"
printf 'Try: tcc\n'
