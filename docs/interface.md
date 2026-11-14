# Interactive Interface

Run `tcc` without a command to open the launcher:

```sh
tcc
```

## Navigation

- Termux Extra Keys `UP` and `DOWN` buttons move the selection.
- Keyboard arrow keys also move the selection.
- `w` / `s` and `k` / `j` provide alternate movement keys.
- Number keys select an action directly.
- `ENTER` runs the selected action.
- `q` or `Ctrl-C` exits.

Configure native Termux buttons in `~/.termux/termux.properties`:

```text
extra-keys = [['ESC','UP','DOWN','ENTER','TAB','CTRL']]
```

Reload the configuration or restart the session afterward.

## Small-screen behavior

The launcher detects terminal width. On screens narrower than 48 columns it uses compact labels and hides long descriptions. Wider screens wrap descriptions rather than allowing horizontal overflow. Titles are clipped when necessary.

When stdin or stdout is not a TTY, raw keyboard mode is not used. TCC displays a numbered prompt instead, which makes simple pipes and scripted checks safe.

## Terminal safety

The launcher restores terminal settings when an action finishes, when the user presses `Ctrl-C`, and when the process exits. Actions pause before returning to the menu so their output can be read.
