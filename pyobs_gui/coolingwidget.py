import qasync
import logging
from typing import Any
from PySide6 import QtCore  # type: ignore

from pyobs.interfaces import ICooling
from .base import BaseWidget
from .qt.coolingwidget_ui import Ui_CoolingWidget


log = logging.getLogger(__name__)


class CoolingWidget(BaseWidget, Ui_CoolingWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)  # type: ignore

        # status
        self._status: tuple[bool, float, float] | None = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.checkEnabled.toggled.connect(self.checkEnabled_toggled)
        self.buttonApply.clicked.connect(self.buttonApply_clicked)

    async def _init(self) -> None:
        module = self.module
        if isinstance(module, ICooling):
            enabled, setpoint, _ = await module.get_cooling()
            self.checkEnabled.setChecked(enabled)
            self.spinSetPoint.setValue(setpoint)

    async def _update(self) -> None:
        # get status
        module = self.module
        if isinstance(module, ICooling):
            self._status = await module.get_cooling()

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

    @QtCore.Slot(bool)  # type: ignore
    def checkEnabled_toggled(self, enabled: bool) -> None:
        self.spinSetPoint.setEnabled(enabled)

    @qasync.asyncSlot()  # type: ignore
    async def buttonApply_clicked(self) -> None:
        # get enabled and setpoint temperature
        enabled = self.checkEnabled.isChecked()
        temp = self.spinSetPoint.value()

        # send it
        module = self.module
        if isinstance(module, ICooling):
            await module.set_cooling(enabled, temp)
