import logging
from typing import TYPE_CHECKING, Any

from PySide6 import QtCore, QtWidgets  # type: ignore

from pyobs.interfaces import IRoboticScheduler, IRunnable, IRunning, RunningState, SchedulerState
from .base import BaseWidget
from .qt.schedulewidget_ui import Ui_ScheduleWidget

if TYPE_CHECKING:
    from pyobs.utils.time import Time

log = logging.getLogger(__name__)

# get_schedule() can be a live portal HTTP call (LcoObservationArchive) -- poll it much less
# often than the widget's 1s update tick.
_SCHEDULE_POLL_INTERVAL = 30
_SCHEDULE_LIMIT = 20


class ScheduleWidget(BaseWidget, Ui_ScheduleWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, update_func=self._tick, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._running = False
        self._last_reschedule: Time | None = None
        self._ticks = 0

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonStart.clicked.connect(self._start)
        self.buttonStop.clicked.connect(self._stop)
        self.buttonReschedule.clicked.connect(self._reschedule)

        # button colors
        self.colorize_button(self.buttonStart, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonStop, QtCore.Qt.GlobalColor.red)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IRunning, self._on_running_state)
        await self.comm.subscribe_state(self.module, IRoboticScheduler, self._on_scheduler_state)

        # permitted methods (ACLs)
        await self._fetch_permitted_methods()

        # initial schedule -- subscribe_state only carries last_reschedule/time, never the
        # schedule itself (see the interface design), so this is the only way to populate the
        # table on open
        await self._refresh_schedule()

    def _on_running_state(self, state: RunningState) -> None:
        self._running = state.running
        self.signal_update_gui.emit()

    def _on_scheduler_state(self, state: SchedulerState) -> None:
        self._last_reschedule = state.last_reschedule
        self.signal_update_gui.emit()

    async def _tick(self) -> None:
        self._ticks += 1
        if self._ticks % _SCHEDULE_POLL_INTERVAL == 0:
            await self._refresh_schedule()
        self.signal_update_gui.emit()

    async def _refresh_schedule(self) -> None:
        try:
            async with self.comm.proxy(self.module, IRoboticScheduler) as proxy:
                schedule = await proxy.get_schedule(limit=_SCHEDULE_LIMIT)
        except Exception as e:
            log.warning("Could not fetch schedule for %s: %s", self.module, e)
            return

        self.tableSchedule.setRowCount(len(schedule))
        for row, task in enumerate(schedule):
            values = [
                task.start.iso[:19] if task.start is not None else "",
                task.end.iso[:19] if task.end is not None else "",
                task.name,
                task.target or "",
                task.state or "",
                f"{task.priority:.1f}" if task.priority is not None else "",
            ]
            for col, value in enumerate(values):
                item = QtWidgets.QTableWidgetItem(value)
                item.setFlags(item.flags() & ~QtCore.Qt.ItemFlag.ItemIsEditable)
                self.tableSchedule.setItem(row, col, item)

    def update_gui(self) -> None:
        self.buttonStart.setEnabled(not self._running and self.permitted("start"))
        self.buttonStop.setEnabled(self._running and self.permitted("stop"))
        self.buttonReschedule.setEnabled(self.permitted("run"))
        last = self._last_reschedule.iso[:19] if self._last_reschedule is not None else "never"
        self.labelStatus.setText(f"{'Running' if self._running else 'Stopped'} — last re-schedule: {last}")

    def _start(self) -> None:
        self.run_background(self._start_scheduler, disable=self.buttonStart)

    async def _start_scheduler(self) -> None:
        async with self.comm.proxy(self.module, IRoboticScheduler) as proxy:
            await proxy.start()

    def _stop(self) -> None:
        self.run_background(self._stop_scheduler, disable=self.buttonStop)

    async def _stop_scheduler(self) -> None:
        async with self.comm.proxy(self.module, IRoboticScheduler) as proxy:
            await proxy.stop()

    def _reschedule(self) -> None:
        self.run_background(self._run_reschedule, disable=self.buttonReschedule)

    async def _run_reschedule(self) -> None:
        async with self.comm.proxy(self.module, IRunnable) as proxy:
            await proxy.run()
        await self._refresh_schedule()


__all__ = ["ScheduleWidget"]
