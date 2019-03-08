import threading
import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox


log = logging.getLogger(__name__)


class BaseWidget(QtWidgets.QWidget):
    show_error = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        self.show_error.connect(self.error_box)

    def run_async(self, method, *args, **kwargs):
        threading.Thread(target=self._async_thread, args=(method, *args), kwargs=kwargs).start()

    def _async_thread(self, method, *args, **kwargs):
        try:
            method(*args, **kwargs)
        except Exception as e:
            log.exception("error")
            self.show_error.emit(str(e))

    def error_box(self, message):
        QMessageBox.warning(self, 'Error', message)
