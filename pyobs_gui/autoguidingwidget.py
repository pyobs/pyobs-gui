import logging
import math
import os
from collections import deque
from typing import Any

import qasync  # type: ignore
from PySide6 import QtCore, QtWidgets  # type: ignore

os.environ["QT_API"] = "PySide6"
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.ticker import MaxNLocator

from pyobs.interfaces import GuidingState, IAutoGuiding, IExposureTime, IRunning, OffsetFrame
from pyobs.interfaces.IExposureTime import ExposureTimeState
from pyobs.interfaces.IRunning import RunningState
from .base import BaseWidget
from .qt.autoguidingwidget_ui import Ui_AutoGuidingWidget

log = logging.getLogger(__name__)

_HISTORY_LENGTH = 50


class AutoGuidingWidget(BaseWidget, Ui_AutoGuidingWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._running = False
        self._loop_closed = False
        self._exposure_time: float | None = None
        self._offset_frame: OffsetFrame | None = None
        self._offset: tuple[float, float] | None = None  # last (lon, lat), arcsec
        self._offset_history: deque[tuple[float, float]] = deque(maxlen=_HISTORY_LENGTH)

        # add plots: offset magnitude vs. sample, and the lon/lat scatter
        self.figure, (self.ax, self.ax2) = plt.subplots(1, 2)
        layout = QtWidgets.QVBoxLayout(self.framePlot)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.framePlot.setLayout(layout)

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
        if state.running and not self._running:
            # rising edge -> a new run started (possibly triggered elsewhere), clear the history
            self._offset_history.clear()
        self._running = state.running
        self.signal_update_gui.emit()

    def _on_exptime_state(self, state: ExposureTimeState) -> None:
        # only follow live updates while the spin box isn't mid-edit, so a user's in-progress
        # value isn't clobbered by a state update from elsewhere
        was_synced = self._exposure_time is None or self.spinExposureTime.value() == self._exposure_time
        self._exposure_time = state.exposure_time
        self.labelExposureTime.setText(f"{state.exposure_time:.1f}")
        if was_synced:
            self.spinExposureTime.setValue(state.exposure_time)
        self.signal_update_gui.emit()

    def _on_guiding_state(self, state: GuidingState) -> None:
        self._loop_closed = state.loop_closed
        self._offset_frame = state.offset_frame
        if state.offset_lon is not None and state.offset_lat is not None:
            self._offset = (state.offset_lon * 3600, state.offset_lat * 3600)
            self._offset_history.append(self._offset)
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.buttonStart.setEnabled(not self._running and self.permitted("start"))
        self.buttonStop.setEnabled(self._running and self.permitted("stop"))
        self.spinExposureTime.setEnabled(self.permitted("set_exposure_time"))
        self.labelLoopState.setText(
            "Closed loop" if self._running and self._loop_closed else "Open loop" if self._running else "Stopped"
        )
        self.labelOffset.setText(f"({self._offset[0]:+.2f}, {self._offset[1]:+.2f}) arcsec" if self._offset else "")

        self.ax.clear()
        if self._offset_history:
            magnitudes = [math.sqrt(lon**2 + lat**2) for lon, lat in self._offset_history]
            self.ax.plot(range(1, len(magnitudes) + 1), magnitudes, marker="o", color="tab:blue")
        self.ax.set_xlabel("Sample")
        self.ax.set_ylabel("Offset magnitude [arcsec]")
        self.ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.ax.grid(linestyle=":", alpha=0.5)
        self.ax.set_axisbelow(True)

        self.ax2.clear()
        if self._offset_frame == OffsetFrame.RA_DEC:
            xlabel, ylabel = "RA offset [arcsec]", "Dec offset [arcsec]"
        elif self._offset_frame == OffsetFrame.ALT_AZ:
            xlabel, ylabel = "Alt offset [arcsec]", "Az offset [arcsec]"
        else:
            xlabel, ylabel = "Offset 1 [arcsec]", "Offset 2 [arcsec]"
        if self._offset_history:
            xs, ys = zip(*self._offset_history, strict=True)
            self.ax2.axhline(0, color="gray", linewidth=0.5)
            self.ax2.axvline(0, color="gray", linewidth=0.5)
            self.ax2.plot(xs, ys, marker="o", linestyle="", color="tab:orange")
            self.ax2.plot(xs[-1], ys[-1], marker="*", color="tab:green", markersize=12, linestyle="", label="latest")
            self.ax2.legend(fontsize="small")
            self.ax2.set_aspect("equal", adjustable="datalim")
        self.ax2.set_xlabel(xlabel)
        self.ax2.set_ylabel(ylabel)
        self.ax2.grid(linestyle=":", alpha=0.5)
        self.ax2.set_axisbelow(True)

        self.figure.tight_layout()
        self.canvas.draw()

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
