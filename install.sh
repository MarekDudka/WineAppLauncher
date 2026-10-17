#!/bin/bash
# Installs the "Wine Applications" launcher into the GNOME application menu.
if [ "$1" = "--uninstall" ]; then
    exec "$(dirname "${BASH_SOURCE[0]}")/uninstall.sh"
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
TARGET="$APPS/WineAppLauncher.desktop"
ICONS="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"

PY=/usr/bin/python3  # system Python, which has the GTK bindings (not conda/venv)
[ -x "$PY" ] || { echo "$PY is required" >&2; exit 1; }
"$PY" -c 'import gi; gi.require_version("Gtk","4.0")' 2>/dev/null ||
    { echo "GTK 4 for Python is required (Debian/Ubuntu: sudo apt install python3-gi gir1.2-gtk-4.0)" >&2; exit 1; }

chmod +x "$DIR/WineAppLauncher.py"
mkdir -p "$APPS" "$ICONS"
cp "$DIR/WineAppLauncher.svg" "$ICONS/WineAppLauncher.svg"
cat > "$TARGET" <<DESKTOP
[Desktop Entry]
Type=Application
Name=Wine Applications
Comment=List and run applications installed in Wine
Exec=$DIR/WineAppLauncher.py
Icon=WineAppLauncher
Terminal=false
Categories=System;
Keywords=wine;windows;applications;
StartupWMClass=WineAppLauncher.py
DESKTOP
chmod +x "$TARGET"
update-desktop-database "$APPS" 2>/dev/null
gtk-update-icon-cache -q -t "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor" 2>/dev/null
echo "Installed $TARGET - search for 'Wine Applications' in GNOME Activities."
