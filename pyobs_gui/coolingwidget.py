import qasync
import logging
from typing import Any
from PySide6 import QtCore  # type: ignore

from pyobs.interfaces import ICooling
from pyobs.interfaces.ICooling import CoolingState
from .base import BaseWidget
from .qt.coolingwidget_ui import Ui_CoolingWidget

log = logging.getLogger(__name__)


class CoolingWidget(BaseWidget, Ui_CoolingWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # status
        self._status: tuple[bool, float, float] | None = None
        self.state: CoolingState | None = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.checkEnabled.toggled.connect(self.checkEnabled_toggled)
        self.buttonApply.clicked.connect(self.buttonApply_clicked)

    async def _init(self) -> None:
        print(self.module)
        await self.comm.subscribe_state(self.module, ICooling, self._update_state)

    def _update_state(self, state: CoolingState) -> None:
        print("_update_state")
        self.state = state
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        if self._status is not None:
            # enable myself
            self.setEnabled(True)

            # set it
            if self.state and self.state.enabled:
                self.labelStatus.setText("N/A" if self.state.setpoint is None else f"{self.state.setpoint:.1}f°C")
                self.labelPower.setText("N/A" if self.state.power is None else f"{self.state.power:d}%%")
            else:
                self.labelStatus.setText("N/A" if self.state is None or self.state.power is None else "OFF")
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
