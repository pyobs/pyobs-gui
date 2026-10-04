"""App-wide Qt signals for things that aren't tied to one widget.

Widgets are created per connected module and don't know about the window or the GUI module that
owns the settings, so settings changes are announced here instead of passing a reference around.
"""

from PySide6 import QtCore  # type: ignore


class GuiSignals(QtCore.QObject):
    # emitted by whoever applied new settings (e.g. new VFS roots), after they are in effect;
    # widgets re-read what they derived from them
    settings_changed = QtCore.Signal()


gui_signals = GuiSignals()
