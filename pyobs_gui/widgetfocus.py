import threading
import logging
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import IFocuser
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetfocus import Ui_WidgetFocus


log = logging.getLogger(__name__)


class WidgetFocus(BaseWidget, Ui_WidgetFocus):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update)
        self.setupUi(self)
        self.module = module    # type: IFocuser
        self.comm = comm        # type: Comm

        # variables
        self._focus = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butSetFocus.clicked.connect(lambda: self.run_async(self.module.set_focus,
                                                                self.spinFocus.value()))

    def _init(self):
        # get current filter
        self._focus = self.module.get_focus().wait()
        self.signal_update_gui.emit()

    def _update(self):
        # get focus
        self._focus = self.module.get_focus().wait()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self):
        # enable myself and set filter
        self.setEnabled(True)
        self.labelCurFocus.setText('%.3f' % self._focus)
