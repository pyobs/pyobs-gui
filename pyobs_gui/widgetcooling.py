import asyncio
import logging
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import ICooling
from .basewidget import BaseWidget
from .qt.widgetcooling import Ui_WidgetCooling


log = logging.getLogger(__name__)


class WidgetCooling(BaseWidget, Ui_WidgetCooling):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs):
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)

        # status
        self._status = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def _update(self) -> None:
        # get status
        if isinstance(self.module, ICooling):
            self._status = await self.module.get_cooling_status()

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
                self.labelStatus.setText("N/A" if set_point is None else "Set=%.1f°C" % set_point)
                self.labelPower.setText("N/A" if power is None else "%d%%" % power)
            else:
                self.labelStatus.setText("N/A" if power is None else "OFF")
                self.labelPower.clear()

    def on_buttonApply_clicked(self) -> None:
        asyncio.create_task(self.set_cooling())

    async def set_cooling(self) -> None:
        # get enabled and setpoint temperature
        enabled = self.checkEnabled.isChecked()
        temp = self.spinSetPoint.value()

        # send it
        if isinstance(self.module, ICooling):
            await self.module.set_cooling(enabled, temp)
