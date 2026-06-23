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
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # state
        self.state: ICooling.State | None = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.checkEnabled.toggled.connect(self.checkEnabled_toggled)
        self.buttonApply.clicked.connect(self.buttonApply_clicked)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, ICooling, self._update_state)

    def _update_state(self, state: ICooling.State) -> None:
        self.state = state
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        if self.state is not None:
            self.setEnabled(True)

            if self.state.enabled:
                self.labelStatus.setText("N/A" if self.state.setpoint is None else f"{self.state.setpoint:.1f}°C")
                self.labelPower.setText("N/A" if self.state.power is None else f"{self.state.power:d}%")
            else:
                self.labelStatus.setText("OFF")
                self.labelPower.clear()

    @QtCore.Slot(bool)  # type: ignore
    def checkEnabled_toggled(self, enabled: bool) -> None:
        self.spinSetPoint.setEnabled(enabled)

    @qasync.asyncSlot()  # type: ignore
    async def buttonApply_clicked(self) -> None:
        enabled = self.checkEnabled.isChecked()
        temp = self.spinSetPoint.value()
        async with self.comm.proxy(self.module, ICooling) as proxy:
            await proxy.set_cooling(enabled, temp)
