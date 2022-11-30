import asyncio
import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import ICooling
from .base import BaseWidget
from .qt.coolingwidget_ui import Ui_CoolingWidget


log = logging.getLogger(__name__)


class CoolingWidget(QtWidgets.QWidget, BaseWidget, Ui_CoolingWidget):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)

        # status
        self._status = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def _init(self) -> None:
        if isinstance(self.module, ICooling):
            enabled, setpoint, _ = await self.module.get_cooling()
            self.checkEnabled.setChecked(enabled)
            self.spinSetPoint.setValue(setpoint)

    async def _update(self) -> None:
        # get status
        if isinstance(self.module, ICooling):
            self._status = await self.module.get_cooling()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        if self._status is not None:
            # enable myself
            self.setEnabled(True)

            # split values
            enabled, set_point, power = self._status

            # set it
            if enabled:
                self.labelStatus.setText("N/A" if set_point is None else "%.1f°C" % set_point)
                self.labelPower.setText("N/A" if power is None else "%d%%" % power)
            else:
                self.labelStatus.setText("N/A" if power is None else "OFF")
                self.labelPower.clear()

    def on_checkEnabled_toggled(self, enabled: bool) -> None:
        self.spinSetPoint.setEnabled(enabled)

    def on_buttonApply_clicked(self) -> None:
        asyncio.create_task(self.set_cooling())

    async def set_cooling(self) -> None:
        # get enabled and setpoint temperature
        enabled = self.checkEnabled.isChecked()
        temp = self.spinSetPoint.value()

        # send it
        if isinstance(self.module, ICooling):
            await self.module.set_cooling(enabled, temp)
