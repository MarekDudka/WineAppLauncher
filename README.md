# WineAppLauncher

A small GTK window that lists the applications installed in Wine. Pick one and it runs.

It reads the menu entries Wine creates in `~/.local/share/applications/wine` (one per installed program, across all your prefixes), shows them with their icons, and starts the selected one with the right `WINEPREFIX` and working directory. Entries whose prefix no longer exists are skipped.

## Requirements

- Linux with Wine (`wine` on your PATH)
- Python 3 with GTK 4 (`sudo apt install python3-gi gir1.2-gtk-4.0` on Debian/Ubuntu)
- GNOME (or any desktop reading `~/.local/share/applications`) for the menu entry

## Files

| File | Purpose |
|------|---------|
| `WineAppLauncher.py` | The launcher |
| `WineAppLauncher.svg` | Menu icon |
| `install.sh` | Adds "Wine Applications" and its icon to the GNOME menu |
| `uninstall.sh` | Removes it from the menu |

## Usage

Install into the GNOME menu, then search for **Wine Applications** in Activities:

```bash
./install.sh
```

Or run directly:

```bash
./WineAppLauncher.py
```

In the window: type to search, Up/Down to move, Enter or double-click to run, Escape to close. The window closes after an application starts.

`./WineAppLauncher.py --list` prints the found applications as text.

## Uninstall

```bash
./uninstall.sh
```

(`./install.sh --uninstall` does the same.)

This removes only the menu entry and icon; Wine and your prefixes are not touched. The menu entry holds the absolute path to this folder, so run `./install.sh` again if you move it.

## Notes

- Programs run through your `wine` command (so any wrapper you have, such as a USB patch, applies), not the distro's `wine-stable`.
- A program installed after you opened the window shows up the next time you open it, once Wine has created its menu entry.
