from PyQt5 import QtWidgets

from pyobs.modules import PyObsModule
from .mainwindow import MainWindow


class GUI(PyObsModule):
    def run(self):
        # create app
        app = QtWidgets.QApplication([])

        # create and show window
        window = MainWindow(self.comm, self.vfs, self.observer)
        window.show()

        # run
        app.exec()
