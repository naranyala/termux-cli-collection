# Interactive Interface

Run `tcc` without a command to open the launcher:

```sh
tcc
```

## Layout

The launcher renders:

- a header with the project title and active key hints;
- actions grouped into categories (`System`, `Device`, `Files`, `Native`);
- a detail panel describing the selected action on wider screens;
- a footer with key hints.

Number keys always refer to the position in the visible (possibly filtered) action list, so they keep working while grouped headers are displayed or a search is active.

## Navigation

| Key | Effect |
|---|---|
| `UP` / `DOWN` arrows | Move the selection |
| Termux Extra Keys `UP` / `DOWN` | Move the selection |
| `w` / `k` | Move up |
| `s` / `j` | Move down |
| `1`-`9` | Run the numbered action directly |
| `ENTER` | Run the selected action |
| `/` | Enter search mode |
| `?` | Open the keyboard help overlay |
| `ESC` | Clear the search, or close help |
| `q` or `Ctrl-C` | Quit (`Ctrl-C` exits with status `130`) |

## Search mode

Press `/` and type to filter actions by name, category, or description. All printable characters can be typed while searching, including letters that are navigation keys outside search mode (`q`, `w`, `s`, `k`, `j`, `?`, `/`). `BACKSPACE` edits the query, arrows still move the selection, `ENTER` leaves search mode with the filter applied, and `ESC` clears it.

## Small-screen behavior

The launcher detects terminal width and height:

- below 72 columns it uses a compact, aligned single-column list and hides descriptions;
- on terminals shorter than 14 lines it hides the detail panel to keep the list usable;
- long titles are clipped, and the action list scrolls to keep the selection visible.

After an action runs, its output stays on screen until you press `ENTER` to return. Actions that exit with a non-zero status print a short status line before the pause.

## Fallbacks

- When stdin or stdout is not a TTY, raw keyboard mode is not used. TCC displays a numbered, categorized prompt instead, which makes simple pipes and scripted checks safe:

  ```sh
  printf '1\n' | tcc
  ```

- Terminals without ANSI support (`TERM=dumb` or empty) use the same numbered prompt.
- Environments without `termios` (some proot setups) also fall back to the numbered prompt.

## Terminal safety

The launcher restores terminal settings when an action finishes, when the user presses `Ctrl-C`, and when the process exits. Actions run outside raw mode, so their output and any paging behave normally.

Configure native Termux buttons in `~/.termux/termux.properties`:

```text
extra-keys = [['ESC','UP','DOWN','ENTER','TAB','CTRL']]
```

Reload the configuration or restart the session afterward.
