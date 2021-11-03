from typing import List, Dict, Tuple, Any

from PyQt5 import QtWidgets

from pyobs.interfaces import IFitsHeaderBefore
from pyobs.modules import Module
from .mainwindow import MainWindow


class GUI(Module, IFitsHeaderBefore):
    __module__ = 'pyobs_gui'

    def __init__(self, show_shell: bool = True, show_events: bool = True, show_modules: list = None,
                 widgets: list = None, *args, **kwargs):
        """Inits a new GUI.

        Args:
            show_shell: Whether to show the shell page.
            show_events: Whether to show the events page.
            show_modules: If not empty, show only listed modules.
            widgets: List of custom widgets.
        """

        Module.__init__(self, *args, **kwargs)
        self._window = None
        self._show_shell = show_shell
        self._show_events = show_events
        self._show_modules = show_modules
        self._widgets = widgets

    def main(self):
        # create app
        app = QtWidgets.QApplication([])

        # create and show window
        self._window = MainWindow(self.comm, self.vfs, self.observer,
                                  show_shell=self._show_shell, show_events=self._show_events,
                                  show_modules=self._show_modules, widgets=self._widgets)
        self._window.show()

        # run
        app.exec()

    def get_fits_header_before(self, namespaces: List[str] = None, *args, **kwargs) -> Dict[str, Tuple[Any, str]]:
        """Returns FITS header for the current status of this module.

        Args:
            namespaces: If given, only return FITS headers for the given namespaces.

        Returns:
            Dictionary containing FITS headers.
        """
        return self._window.get_fits_headers(namespaces)
