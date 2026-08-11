from __future__ import annotations

import logging
from typing import Any, TYPE_CHECKING
import qasync  # type: ignore
from PySide6 import QtCore  # type: ignore

from pyobs.interfaces import IAbortable, IExposure, ExposureState
from pyobs.utils.enums import ExposureStatus
from .base import BaseWidget

from .qt.spectrographwidget_ui import Ui_SpectrographWidget

if TYPE_CHECKING:
    from astroplan import Observer
    from pyobs.vfs import VirtualFileSystem
    from pyobs.comm import Comm


log = logging.getLogger(__name__)


class SpectrographWidget(BaseWidget, Ui_SpectrographWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any) -> None:
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self.exposure_status = ExposureStatus.IDLE
        self.exposures_left = 0

        # before first update, disable myself
        self.setEnabled(False)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butExpose.clicked.connect(self.grab_spectrum)
        self.butAbort.clicked.connect(self.abort)

    async def open(
        self,
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)
        await self.datadisplay.open(modules=modules, comm=comm, observer=observer, vfs=vfs)

        self.butAbort.setVisible(await self.comm.has_proxy(self.module, IAbortable))

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IExposure, self._on_exposure_state)

    def _on_exposure_state(self, state: ExposureState) -> None:
        self.exposure_status = state.status
        self.signal_update_gui.emit()

    @qasync.asyncSlot()  # type: ignore
    async def grab_spectrum(self) -> None:
        broadcast = self.checkBroadcast.isChecked()

        # take the requested number of spectra; an exception (e.g. from a failed exposure,
        # or abort() zeroing exposures_left mid-loop) stops the sequence
        self.exposures_left = self.spinCount.value()
        self.signal_update_gui.emit()
        while self.exposures_left > 0:
            await self.datadisplay.grab_data(broadcast)
            self.exposures_left -= 1
            self.signal_update_gui.emit()

    @qasync.asyncSlot()  # type: ignore
    async def abort(self) -> None:
        # stop the sequence after the current spectrum finishes aborting
        self.exposures_left = 0
        async with self.comm.proxy(self.module, IAbortable) as proxy:
            await proxy.abort()

    def update_gui(self) -> None:
        self.setEnabled(True)

        self.butExpose.setEnabled(self.exposure_status == ExposureStatus.IDLE)
        self.butAbort.setEnabled(self.exposure_status != ExposureStatus.IDLE)

        self.butAbort.setText("Abort sequence" if self.exposures_left > 1 else "Abort")

        if self.exposures_left > 0:
            self.labelExposuresLeft.setText(f"{self.exposures_left} spectrum/spectra left")
        else:
            self.labelExposuresLeft.setText("")

        msg = ""
        if self.exposure_status == ExposureStatus.IDLE:
            self.progressExposure.setValue(0)
            msg = "IDLE"
        elif self.exposure_status == ExposureStatus.EXPOSING:
            msg = ""
        elif self.exposure_status == ExposureStatus.READOUT:
            self.progressExposure.setValue(100)
            msg = "READOUT"

        self.labelStatus.setText(msg)
