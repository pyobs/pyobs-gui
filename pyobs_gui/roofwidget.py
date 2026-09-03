from __future__ import annotations

from typing import Any, TYPE_CHECKING
from PySide6 import QtCore  # type: ignore

from pyobs.interfaces import IMotion, MotionState, IPointingAltAz, AltAzState
from .base import BaseWidget
from .qt.roofwidget_ui import Ui_RoofWidget

if TYPE_CHECKING:
    from pyobs.utils.enums import MotionStatus


class RoofWidget(BaseWidget, Ui_RoofWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._motion_status: MotionStatus | None = None
        self._azimuth: float | None = None

        # connect signals
        self.buttonOpen.clicked.connect(self.open_roof)
        self.buttonClose.clicked.connect(self.close_roof)
        self.buttonStop.clicked.connect(self.stop_roof)
        self.signal_update_gui.connect(self.update_gui)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IMotion, self._on_motion_state)
        if await self.comm.has_proxy(self.module, IPointingAltAz):
            await self.comm.subscribe_state(self.module, IPointingAltAz, self._on_pointing_state)

    def _on_motion_state(self, state: MotionState) -> None:
        self._motion_status = state.status
        self.signal_update_gui.emit()

    def _on_pointing_state(self, state: AltAzState) -> None:
        self._azimuth = state.az
        self.signal_update_gui.emit()

    @QtCore.Slot()  # type: ignore
    def update_gui(self) -> None:
        self.setEnabled(True)

        if self._motion_status is not None:
            self.labelStatus.setText(self._motion_status)

        if self._azimuth is None:
            self.labelAzimuth.setText("N/A")
        else:
            self.labelAzimuth.setText(f"{self._azimuth:.1f}°")

    def open_roof(self) -> None:
        self.run_background(self._open_roof)

    async def _open_roof(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.init()

    def close_roof(self) -> None:
        self.run_background(self._close_roof)

    async def _close_roof(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.park()

    def stop_roof(self) -> None:
        self.run_background(self._stop_roof)

    async def _stop_roof(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.stop_motion()
