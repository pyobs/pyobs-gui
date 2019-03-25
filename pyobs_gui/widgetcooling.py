import threading
import logging
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import ICooling
from .qt.widgetcooling import Ui_WidgetCooling


log = logging.getLogger(__name__)


class WidgetCooling(QtWidgets.QWidget, Ui_WidgetCooling):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: ICooling
        self.comm = comm        # type: Comm

    def enter(self):
        pass

    def leave(self):
        pass
