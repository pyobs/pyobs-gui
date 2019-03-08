from PyQt5 import QtWidgets

from pyobs.modules import PyObsModule
from .mainwindow import MainWindow


class GUI(PyObsModule):
    def __init__(self, *args, **kwargs):
        PyObsModule.__init__(self, thread_funcs=self._run, restart_threads=False, *args, **kwargs)

    def _run(self):
        # create app
        app = QtWidgets.QApplication([])

        # create and show window
        window = MainWindow(self.comm, self.vfs)
        window.show()

        # run
        app.exec()
