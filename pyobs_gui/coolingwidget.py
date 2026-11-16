import logging
from typing import Any
from PySide6 import QtCore  # type: ignore

from pyobs.interfaces import ICooling, CoolingState
from .base import BaseWidget
from .qt.coolingwidget_ui import Ui_CoolingWidget

log = logging.getLogger(__name__)


class CoolingWidget(BaseWidget, Ui_CoolingWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # state
        self.state: CoolingState | None = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.checkEnabled.toggled.connect(self.checkEnabled_toggled)
        self.buttonApply.clicked.connect(self.buttonApply_clicked)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, ICooling, self._update_state)

    def _update_state(self, state: CoolingState) -> None:
        self.state = state
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        if self.state is not None:
            self.setEnabled(True)

            self.labelStatus.setText(self._status_text(self.state))
            if self.state.enabled:
                self.labelPower.setText("N/A" if self.state.power is None else f"{self.state.power:d}%")
            else:
                self.labelPower.clear()

    @staticmethod
    def _status_text(state: CoolingState) -> str:
        """Setpoint text; while a ramp runs, also the target it is heading for."""
        setpoint = "N/A" if state.setpoint is None else f"{state.setpoint:.1f}°C"
        if state.ramping and state.target is not None:
            prefix = "" if state.enabled else "warming "
            return f"{prefix}{setpoint} → {state.target:.1f}°C"
        return setpoint if state.enabled else "OFF"

    @QtCore.Slot(bool)  # type: ignore
    def checkEnabled_toggled(self, enabled: bool) -> None:
        self.spinSetPoint.setEnabled(enabled)

    def buttonApply_clicked(self) -> None:
        enabled = self.checkEnabled.isChecked()
        temp = self.spinSetPoint.value()
        self.run_background(self._apply_cooling, enabled, temp)

    async def _apply_cooling(self, enabled: bool, temp: float) -> None:
        async with self.comm.proxy(self.module, ICooling) as proxy:
            await proxy.set_cooling(enabled, temp)
