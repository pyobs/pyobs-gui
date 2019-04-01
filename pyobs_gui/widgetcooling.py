import logging
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import ICooling
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetcooling import Ui_WidgetCooling


log = logging.getLogger(__name__)


class WidgetCooling(BaseWidget, Ui_WidgetCooling):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update)
        self.setupUi(self)
        self.module = module    # type: ICooling
        self.comm = comm        # type: Comm

        # status
        self._status = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    def _update(self):
        # get status
        self._status = self.module.get_cooling_status()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self):
        if self._status is not None:
            # enable myself
            self.setEnabled(True)

            # split values
            enabled, set_point, power, temps = self._status

            # set it
            if enabled:
                self.labelStatus.setText('Set=%.1f°C' % set_point)
                self.labelPower.setText('%d%%' % power)
            else:
                self.labelStatus.setText('OFF')
                self.labelStatus.clear()
