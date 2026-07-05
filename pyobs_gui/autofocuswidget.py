import logging
import os
from typing import Any

import qasync  # type: ignore
from PySide6 import QtCore, QtWidgets  # type: ignore

os.environ["QT_API"] = "PySide6"
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas

from pyobs.events import Event, FocusFoundEvent
from pyobs.interfaces import AutoFocusPoint, AutoFocusState, IAutoFocus, IRunning, RunningState
from .base import BaseWidget
from .qt.autofocuswidget_ui import Ui_AutoFocusWidget

log = logging.getLogger(__name__)


class AutoFocusWidget(BaseWidget, Ui_AutoFocusWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._points: list[AutoFocusPoint] = []
        self._running = False
        self._last_result: tuple[float, float] | None = None

        # add plot
        self.figure, self.ax = plt.subplots()
        layout = QtWidgets.QVBoxLayout(self.framePlot)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.framePlot.setLayout(layout)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonRunAutoFocus.clicked.connect(self._run_auto_focus)
        self.buttonAbort.clicked.connect(self._abort)

        # button colors
        self.colorize_button(self.buttonRunAutoFocus, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonAbort, QtCore.Qt.GlobalColor.red)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IRunning, self._on_running_state)
        await self.comm.subscribe_state(self.module, IAutoFocus, self._on_autofocus_state)
        await self.comm.register_event(FocusFoundEvent, self._on_focus_found)

        # permitted methods (ACLs)
        await self._fetch_permitted_methods()

    def _on_running_state(self, state: RunningState) -> None:
        if state.running and not self._running:
            # rising edge -> a new run started (possibly triggered elsewhere), clear the plot
            self._points = []
            self._last_result = None
        self._running = state.running
        self.signal_update_gui.emit()

    def _on_autofocus_state(self, state: AutoFocusState) -> None:
        self._points = state.points
        self.signal_update_gui.emit()

    async def _on_focus_found(self, event: Event, sender: str) -> bool:
        if sender != self.module or not isinstance(event, FocusFoundEvent):
            return False
        self._last_result = (event.focus, event.error or 0.0)
        self.signal_update_gui.emit()
        return True

    def update_gui(self) -> None:
        self.buttonRunAutoFocus.setEnabled(not self._running and self.permitted("auto_focus"))
        self.buttonAbort.setEnabled(self._running and self.permitted("abort"))
        self.labelStatus.setText(
            "Running..."
            if self._running
            else f"Focus: {self._last_result[0]:.3f} ± {self._last_result[1]:.3f} mm"
            if self._last_result
            else "Idle"
        )

        self.ax.clear()
        if self._points:
            self.ax.scatter([p.focus for p in self._points], [p.value for p in self._points], color="tab:blue")
        if self._last_result and not self._running:
            self.ax.axvline(self._last_result[0], color="tab:green", linestyle="--", label="fitted focus")
            self.ax.legend()
        self.ax.set_xlabel("Focus [mm]")
        self.ax.set_ylabel("Metric")
        self.ax.grid(linestyle=":", alpha=0.5)
        self.ax.set_axisbelow(True)
        self.canvas.draw()

    @qasync.asyncSlot()  # type: ignore
    async def _run_auto_focus(self) -> None:
        async with self.comm.proxy(self.module, IAutoFocus) as proxy:
            await proxy.auto_focus(self.spinCount.value(), self.spinStep.value(), self.spinExposureTime.value())

    @qasync.asyncSlot()  # type: ignore
    async def _abort(self) -> None:
        async with self.comm.proxy(self.module, IAutoFocus) as proxy:
            await proxy.abort()


__all__ = ["AutoFocusWidget"]
