from __future__ import annotations

from typing import Any, TYPE_CHECKING
import qasync  # type: ignore
from PySide6 import QtCore  # type: ignore

from pyobs.interfaces import IMotion, IPointingAltAz
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
        await self.comm.subscribe_state(self.module, IPointingAltAz, self._on_pointing_state)

    def _on_motion_state(self, state: IMotion.State) -> None:
        self._motion_status = state.status
        self.signal_update_gui.emit()

    def _on_pointing_state(self, state: IPointingAltAz.State) -> None:
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

    @qasync.asyncSlot()  # type: ignore
    async def open_roof(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.init()

    @qasync.asyncSlot()  # type: ignore
    async def close_roof(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.park()

    @qasync.asyncSlot()  # type: ignore
    async def stop_roof(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.stop_motion()