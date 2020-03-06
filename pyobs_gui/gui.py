from PyQt5 import QtWidgets

from pyobs.interfaces import IFitsHeaderProvider
from pyobs.modules import PyObsModule
from .mainwindow import MainWindow


class GUI(PyObsModule, IFitsHeaderProvider):
    def __init__(self, *args, **kwargs):
        PyObsModule.__init__(self, *args, **kwargs)
        self._window = None

    def main(self):
        # create app
        app = QtWidgets.QApplication([])

        # create and show window
        self._window = MainWindow(self.comm, self.vfs, self.observer)
        self._window.show()

        # run
        app.exec()

    def get_fits_headers(self, namespaces: list = None, *args, **kwargs) -> dict:
        """Returns FITS header for the current status of this module.

        Args:
            namespaces: If given, only return FITS headers for the given namespaces.

        Returns:
            Dictionary containing FITS headers.
        """
        return self._window.get_fits_headers(namespaces)
