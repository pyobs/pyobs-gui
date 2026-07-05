import logging
from typing import Any

import qasync  # type: ignore
from PySide6 import QtCore  # type: ignore

from pyobs.interfaces import GuidingState, IAutoGuiding, IExposureTime, IRunning
from pyobs.interfaces.IExposureTime import ExposureTimeState
from pyobs.interfaces.IRunning import RunningState
from .base import BaseWidget
from .qt.autoguidingwidget_ui import Ui_AutoGuidingWidget

log = logging.getLogger(__name__)


class AutoGuidingWidget(BaseWidget, Ui_AutoGuidingWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._running = False
        self._loop_closed = False
        self._exposure_time = 0.0
        self._offset: tuple[float, float] | None = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonStart.clicked.connect(self._start)
        self.buttonStop.clicked.connect(self._stop)
        self.spinExposureTime.init_modified(self.labelExposureTime).committed.connect(self._set_exposure_time)

        # button colors
        self.colorize_button(self.buttonStart, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonStop, QtCore.Qt.GlobalColor.red)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IRunning, self._on_running_state)
        await self.comm.subscribe_state(self.module, IExposureTime, self._on_exptime_state)
        await self.comm.subscribe_state(self.module, IAutoGuiding, self._on_guiding_state)

        # permitted methods (ACLs)
        await self._fetch_permitted_methods()

    def _on_running_state(self, state: RunningState) -> None:
        self._running = state.running
        self.signal_update_gui.emit()

    def _on_exptime_state(self, state: ExposureTimeState) -> None:
        # only follow live updates while the spin box isn't mid-edit, so a user's in-progress
        # value isn't clobbered by a state update from elsewhere
        was_synced = self.spinExposureTime.value() == self._exposure_time
        self._exposure_time = state.exposure_time
        self.labelExposureTime.setText(f"{state.exposure_time:.1f}")
        if was_synced:
            self.spinExposureTime.setValue(state.exposure_time)
        self.signal_update_gui.emit()

    def _on_guiding_state(self, state: GuidingState) -> None:
        self._loop_closed = state.loop_closed
        if state.last_offset_x is not None and state.last_offset_y is not None:
            self._offset = (state.last_offset_x, state.last_offset_y)
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.buttonStart.setEnabled(not self._running and self.permitted("start"))
        self.buttonStop.setEnabled(self._running and self.permitted("stop"))
        self.spinExposureTime.setEnabled(self.permitted("set_exposure_time"))
        self.labelLoopState.setText(
            "Closed loop" if self._running and self._loop_closed else "Open loop" if self._running else "Stopped"
        )
        self.labelOffset.setText(f"({self._offset[0]:+.2f}, {self._offset[1]:+.2f}) px" if self._offset else "")

    @qasync.asyncSlot()  # type: ignore
    async def _start(self) -> None:
        async with self.comm.proxy(self.module, IAutoGuiding) as proxy:
            await proxy.start()

    @qasync.asyncSlot()  # type: ignore
    async def _stop(self) -> None:
        async with self.comm.proxy(self.module, IAutoGuiding) as proxy:
            await proxy.stop()

    @qasync.asyncSlot()  # type: ignore
    async def _set_exposure_time(self) -> None:
        value = self.spinExposureTime.value()
        async with self.comm.proxy(self.module, IExposureTime) as proxy:
            await proxy.set_exposure_time(value)


__all__ = ["AutoGuidingWidget"]
