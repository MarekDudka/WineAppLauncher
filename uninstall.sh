#!/bin/bash
# Removes the "Wine Applications" launcher from the GNOME application menu.
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
rm -f "$APPS/WineAppLauncher.desktop"
rm -f "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps/WineAppLauncher.svg"
update-desktop-database "$APPS" 2>/dev/null
echo "Removed the Wine Applications launcher from the menu."
