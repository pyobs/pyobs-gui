from typing import List, Dict, Tuple, Any

from PyQt5 import QtWidgets

from pyobs.interfaces import IFitsHeaderProvider
from pyobs.modules import Module
from .mainwindow import MainWindow


class GUI(Module, IFitsHeaderProvider):
    __module__ = 'pyobs_gui'

    def __init__(self, show_shell: bool = True, show_events: bool = True, *args, **kwargs):
        """Inits a new GUI.

        Args:
            show_shell: Whether to show the shell page.
            show_events: Whether to show the events page.
        """

        Module.__init__(self, *args, **kwargs)
        self._window = None
        self._show_shell = show_shell
        self._show_events = show_events

    def main(self):
        # create app
        app = QtWidgets.QApplication([])

        # create and show window
        self._window = MainWindow(self.comm, self.vfs, self.observer,
                                  show_shell=self._show_shell, show_events=self._show_events)
        self._window.show()

        # run
        app.exec()

    def get_fits_headers(self, namespaces: List[str] = None, *args, **kwargs) -> Dict[str, Tuple[Any, str]]:
        """Returns FITS header for the current status of this module.

        Args:
            namespaces: If given, only return FITS headers for the given namespaces.

        Returns:
            Dictionary containing FITS headers.
        """
        return self._window.get_fits_headers(namespaces)
