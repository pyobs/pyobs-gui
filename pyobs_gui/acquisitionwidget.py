import logging
import os
from typing import Any

import qasync  # type: ignore
from PySide6 import QtCore, QtWidgets  # type: ignore

os.environ["QT_API"] = "PySide6"
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from pyobs.interfaces import AcquisitionAttempt, AcquisitionResult, AcquisitionState, IAcquisition, IRunning
from pyobs.interfaces.IRunning import RunningState
from .base import BaseWidget
from .qt.acquisitionwidget_ui import Ui_AcquisitionWidget

log = logging.getLogger(__name__)


class AcquisitionWidget(BaseWidget, Ui_AcquisitionWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._attempts: list[AcquisitionAttempt] = []
        self._running = False
        self._result: AcquisitionResult | None = None

        # add plots: distance vs. attempt, and the 2D offset trajectory
        self.figure, (self.ax, self.ax2) = plt.subplots(1, 2)
        layout = QtWidgets.QVBoxLayout(self.framePlot)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.framePlot.setLayout(layout)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonAcquire.clicked.connect(self._acquire)
        self.buttonAbort.clicked.connect(self._abort)

        # button colors
        self.colorize_button(self.buttonAcquire, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonAbort, QtCore.Qt.GlobalColor.red)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IRunning, self._on_running_state)
        await self.comm.subscribe_state(self.module, IAcquisition, self._on_acquisition_state)

        # permitted methods (ACLs)
        await self._fetch_permitted_methods()

    def _on_running_state(self, state: RunningState) -> None:
        if state.running and not self._running:
            # rising edge -> a new run started (possibly triggered elsewhere), clear the plot
            self._attempts = []
            self._result = None
        self._running = state.running
        self.signal_update_gui.emit()

    def _on_acquisition_state(self, state: AcquisitionState) -> None:
        self._attempts = state.attempts
        self._result = state.result
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.buttonAcquire.setEnabled(not self._running and self.permitted("acquire_target"))
        self.buttonAbort.setEnabled(self._running and self.permitted("abort"))
        self.labelStatus.setText("Acquiring..." if self._running else "Acquired." if self._result else "Idle")

        if self._result:
            self.labelResultRa.setText(f"{self._result.ra:.5f}")
            self.labelResultDec.setText(f"{self._result.dec:.5f}")
            self.labelResultAlt.setText(f"{self._result.alt:.3f}")
            self.labelResultAz.setText(f"{self._result.az:.3f}")
            if self._result.off_ra is not None and self._result.off_dec is not None:
                self.labelOffsetType.setText("RA/Dec offset:")
                self.labelResultOffset.setText(f"({self._result.off_ra:+.5f}, {self._result.off_dec:+.5f})")
            elif self._result.off_alt is not None and self._result.off_az is not None:
                self.labelOffsetType.setText("Alt/Az offset:")
                self.labelResultOffset.setText(f"({self._result.off_alt:+.3f}, {self._result.off_az:+.3f})")
            else:
                self.labelOffsetType.setText("Offset:")
                self.labelResultOffset.setText("")
        else:
            self.labelResultRa.setText("")
            self.labelResultDec.setText("")
            self.labelResultAlt.setText("")
            self.labelResultAz.setText("")
            self.labelOffsetType.setText("Offset:")
            self.labelResultOffset.setText("")

        self.ax.clear()
        if self._attempts:
            self.ax.plot(
                [a.attempt for a in self._attempts],
                [a.distance for a in self._attempts],
                marker="o",
                color="tab:blue",
            )
        self.ax.set_xlabel("Attempt")
        self.ax.set_ylabel("Distance to target [arcsec]")
        self.ax.grid(linestyle=":", alpha=0.5)
        self.ax.set_axisbelow(True)

        self.ax2.clear()
        ra_dec = [(a.offset_ra, a.offset_dec) for a in self._attempts if a.offset_ra is not None]
        alt_az = [(a.offset_alt, a.offset_az) for a in self._attempts if a.offset_alt is not None]
        if ra_dec:
            xlabel, ylabel, points = "RA offset [deg]", "Dec offset [deg]", ra_dec
        elif alt_az:
            xlabel, ylabel, points = "Alt offset [deg]", "Az offset [deg]", alt_az
        else:
            xlabel, ylabel, points = "Offset 1 [deg]", "Offset 2 [deg]", []
        if points:
            xs, ys = zip(*points, strict=True)
            self.ax2.axhline(0, color="gray", linewidth=0.5)
            self.ax2.axvline(0, color="gray", linewidth=0.5)
            self.ax2.plot(xs, ys, marker="o", color="tab:orange")
            self.ax2.plot(xs[0], ys[0], marker="s", color="tab:red", markersize=8, linestyle="", label="start")
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
    async def _acquire(self) -> None:
        async with self.comm.proxy(self.module, IAcquisition) as proxy:
            await proxy.acquire_target()

    @qasync.asyncSlot()  # type: ignore
    async def _abort(self) -> None:
        async with self.comm.proxy(self.module, IAcquisition) as proxy:
            await proxy.abort()


__all__ = ["AcquisitionWidget"]
