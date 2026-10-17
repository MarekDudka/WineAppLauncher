#!/usr/bin/python3
"""GTK launcher listing the applications installed in Wine; pick one to run it.

Reads the menu entries Wine creates in ~/.local/share/applications/wine.
Type to search, double-click or press Enter to run, Escape to close.

Usage: WineAppLauncher.py [--list]   (--list prints the entries instead of the GUI)
"""
import configparser
import os
import shlex
import subprocess
import sys
from pathlib import Path

APPS = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "applications/wine"


def load_entries():
    entries = []
    for path in sorted(APPS.rglob("*.desktop")):
        cp = configparser.RawConfigParser(strict=False, interpolation=None)
        cp.optionxform = str
        try:
            cp.read(path, encoding="utf-8")
            sec = cp["Desktop Entry"]
        except (configparser.Error, KeyError, UnicodeDecodeError):
            continue
        if sec.get("NoDisplay", "").lower() == "true" or "Exec" not in sec:
            continue
        # Desktop-file unescape (\\ -> \), then shell-style split of the Exec line.
        try:
            argv = shlex.split(sec["Exec"].replace("\\\\", "\\"))
        except ValueError:
            continue
        prefix = next((a.split("=", 1)[1] for a in argv if a.startswith("WINEPREFIX=")), None)
        if prefix and not Path(prefix).is_dir():
            continue  # stale entry from a prefix that no longer exists
        # Use the user's `wine` (with its wrapper) instead of the distro's wine-stable.
        argv = ["wine" if a == "wine-stable" else a for a in argv]
        rel = path.relative_to(APPS).with_suffix("")
        group = str(rel.parent) if str(rel.parent) != "." else ""
        entries.append({
            "name": sec.get("Name", path.stem),
            "group": group.removeprefix("Programs/").removeprefix("Programs"),
            "prefix": Path(prefix).name if prefix else ".wine",
            "icon": sec.get("Icon", ""),
            "argv": argv,
            "cwd": sec.get("Path") if sec.get("Path") and Path(sec["Path"]).is_dir() else None,
        })
    entries.sort(key=lambda e: (e["name"].lower(), e["group"]))
    return entries


def run(entry):
    subprocess.Popen(entry["argv"], cwd=entry["cwd"], start_new_session=True,
                     stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def gui(entries):
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gtk

    def on_activate(app):
        win = Gtk.ApplicationWindow(application=app, title="Wine Applications",
                                    default_width=560, default_height=600)
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6,
                      margin_top=8, margin_bottom=8, margin_start=8, margin_end=8)
        search = Gtk.SearchEntry(placeholder_text="Search applications…")
        lst = Gtk.ListBox(selection_mode=Gtk.SelectionMode.SINGLE, activate_on_single_click=False)
        scroll = Gtk.ScrolledWindow(vexpand=True, child=lst)
        box.append(search)
        box.append(scroll)
        win.set_child(box)

        theme = Gtk.IconTheme.get_for_display(win.get_display())
        for e in entries:
            row = Gtk.ListBoxRow()
            h = Gtk.Box(spacing=10, margin_top=4, margin_bottom=4, margin_start=6, margin_end=6)
            icon = Gtk.Image(pixel_size=32)
            icon.set_from_icon_name(e["icon"] if e["icon"] and theme.has_icon(e["icon"]) else "application-x-executable")
            v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.CENTER)
            title = Gtk.Label(label=e["name"], xalign=0)
            sub = Gtk.Label(label=" · ".join(x for x in (e["group"], e["prefix"]) if x), xalign=0)
            sub.add_css_class("dim-label")
            sub.add_css_class("caption")
            v.append(title)
            v.append(sub)
            h.append(icon)
            h.append(v)
            row.set_child(h)
            row.entry = e
            row.haystack = f'{e["name"]} {e["group"]}'.lower()
            lst.append(row)

        def launch(_lst, row):
            run(row.entry)
            win.close()

        def flt(row):
            return search.get_text().lower() in row.haystack

        lst.set_filter_func(flt)
        lst.connect("row-activated", launch)

        def on_search(_s):
            lst.invalidate_filter()
            first = lst.get_row_at_index(0)
            i = 0
            while first is not None and not flt(first):
                i += 1
                first = lst.get_row_at_index(i)
            if first:
                lst.select_row(first)

        search.connect("search-changed", on_search)
        search.connect("activate", lambda _s: (lst.get_selected_row() and launch(lst, lst.get_selected_row())))
        search.connect("stop-search", lambda _s: win.close())
        first = lst.get_row_at_index(0)
        if first:
            lst.select_row(first)
        win.present()
        search.grab_focus()

    app = Gtk.Application(application_id="local.WineAppLauncher")
    app.connect("activate", on_activate)
    return app.run([sys.argv[0]])


def main():
    entries = load_entries()
    if "--list" in sys.argv:
        for e in entries:
            print(f'{e["name"]}\t{e["group"]}\t{e["prefix"]}\t{e["icon"]}')
        return 0
    return gui(entries)


if __name__ == "__main__":
    sys.exit(main())
