import logging
from typing import Any

from PySide6 import QtCore  # type: ignore

from pyobs.events import Event, TaskFailedEvent, TaskFinishedEvent, TaskStartedEvent
from pyobs.interfaces import IRobotic, IRunning, RoboticState, RunningState
from pyobs.utils.time import Time
from .base import BaseWidget
from .qt.roboticwidget_ui import Ui_RoboticWidget

log = logging.getLogger(__name__)


def _format_time(t: Time | None) -> str:
    return t.iso[:19] if t is not None else ""


def _format_countdown(end: Time | None) -> str:
    if end is None:
        return ""
    seconds = (end - Time.now()).sec
    if seconds <= 0:
        return "overdue"
    hours, remainder = divmod(int(seconds), 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{secs:02d}"


class RoboticWidget(BaseWidget, Ui_RoboticWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, update_func=self._tick, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._running = False
        self._state = RoboticState()

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonStart.clicked.connect(self._start)
        self.buttonStop.clicked.connect(self._stop)

        # button colors
        self.colorize_button(self.buttonStart, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonStop, QtCore.Qt.GlobalColor.red)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IRunning, self._on_running_state)
        await self.comm.subscribe_state(self.module, IRobotic, self._on_robotic_state)
        await self.register_event(TaskStartedEvent, self._on_task_event)
        await self.register_event(TaskFinishedEvent, self._on_task_event)
        await self.register_event(TaskFailedEvent, self._on_task_event)

        # permitted methods (ACLs)
        await self._fetch_permitted_methods()

    def _on_running_state(self, state: RunningState) -> None:
        self._running = state.running
        self.signal_update_gui.emit()

    def _on_robotic_state(self, state: RoboticState) -> None:
        self._state = state
        self.signal_update_gui.emit()

    async def _on_task_event(self, event: Event, sender: str) -> bool:
        if sender != self.module or not isinstance(event, (TaskStartedEvent, TaskFinishedEvent, TaskFailedEvent)):
            return False
        # RoboticState (pushed separately, see _on_robotic_state) is the source of truth for what
        # to render -- these events only trigger a re-render of whatever's already cached, so a
        # missed event never leaves the widget showing stale data.
        self.signal_update_gui.emit()
        return True

    async def _tick(self) -> None:
        # _update_loop (BaseWidget) calls this every second while the module is READY, driving
        # the countdown -- no separate timer needed.
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.buttonStart.setEnabled(not self._running and self.permitted("start"))
        self.buttonStop.setEnabled(self._running and self.permitted("stop"))
        self.labelStatus.setText("Running" if self._running else "Stopped")

        current = self._state.current
        self.textCurrentName.setText(current.name if current is not None else "")
        self.textCurrentTarget.setText((current.target or "") if current is not None else "")
        self.textCurrentObsnum.setText((current.obsnum or "") if current is not None else "")
        self.textCurrentStart.setText(_format_time(current.start) if current is not None else "")
        self.textCurrentEta.setText(_format_countdown(current.end) if current is not None else "")

        next_task = self._state.next
        self.textNextName.setText(next_task.name if next_task is not None else "")
        self.textNextTarget.setText((next_task.target or "") if next_task is not None else "")
        self.textNextStart.setText(_format_time(next_task.start) if next_task is not None else "")
        self.textCantRunReason.setText(self._state.cant_run_reason or "")

    def _start(self) -> None:
        self.run_background(self._start_robotic, disable=self.buttonStart)

    async def _start_robotic(self) -> None:
        async with self.comm.proxy(self.module, IRobotic) as proxy:
            await proxy.start()

    def _stop(self) -> None:
        self.run_background(self._stop_robotic, disable=self.buttonStop)

    async def _stop_robotic(self) -> None:
        async with self.comm.proxy(self.module, IRobotic) as proxy:
            await proxy.stop()


__all__ = ["RoboticWidget"]
