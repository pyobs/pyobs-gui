from typing import Any
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import IDome, IMotion
from pyobs.utils.enums import MotionStatus
from .base import BaseWidget
from .qt.roofwidget_ui import Ui_RoofWidget


class RoofWidget(BaseWidget, Ui_RoofWidget):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)  # type: ignore

        # status
        self.motion_status: MotionStatus | None = None
        self.azimuth: float | None = None

        # connect signals
        if isinstance(self.module, IMotion):
            self.buttonOpen.clicked.connect(self.open_roof)
            self.buttonClose.clicked.connect(self.close_roof)
            self.buttonStop.clicked.connect(self.stop_roof)
        self.signal_update_gui.connect(self.update_gui)

    async def _init(self) -> None:
        # get status and update gui
        if self.module is not None and isinstance(self.module, IMotion):
            self.motion_status = await self.module.get_motion_status()
        self.signal_update_gui.emit()

    async def _update(self) -> None:
        # azimuth and motion status
        if self.module is not None and isinstance(self.module, IMotion):
            self.motion_status = await self.module.get_motion_status()
        if self.module is not None and isinstance(self.module, IDome):
            _, self.azimuth = await self.module.get_altaz()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # set status
        if self.motion_status is not None:
            self.labelStatus.setText(self.motion_status.value)

        # open
        if self.azimuth is None:
            self.labelAzimuth.setText("N/A")
        else:
            self.labelAzimuth.setText("%.1f°" % self.azimuth)

    def open_roof(self) -> None:
        if self.module is not None and isinstance(self.module, IMotion):
            self.run_background(self.module.init)

    def close_roof(self) -> None:
        if self.module is not None and isinstance(self.module, IMotion):
            self.run_background(self.module.park)

    def stop_roof(self) -> None:
        if self.module is not None and isinstance(self.module, IMotion):
            self.run_background(self.module.stop_motion)
