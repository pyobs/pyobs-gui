from typing import Any

import qasync
from PySide6 import QtWidgets, QtCore  # type: ignore

from pyobs.events import FilterChangedEvent, MotionStatusChangedEvent, Event
from pyobs.interfaces import IFilters
from pyobs.utils.enums import MotionStatus
from .base import BaseWidget
from .qt.filterwidget_ui import Ui_FilterWidget


class FilterWidget(BaseWidget, Ui_FilterWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, update_func=self._update, update_interval=10, **kwargs)
        self.setupUi(self)  # type: ignore

        # variables
        self._filter: str | None = None
        self._filters: list[str] = []
        self._motion_status = MotionStatus.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonSetFilter.clicked.connect(self.set_filter)

        # button colors
        self.colorize_button(self.buttonSetFilter, QtCore.Qt.green)

    async def open(self, **kwargs: Any) -> None:  # type: ignore
        """Open module."""
        await BaseWidget.open(self, **kwargs)

        # subscribe to events
        await self.comm.register_event(FilterChangedEvent, self._on_filter_changed)
        await self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

    async def _init(self) -> None:
        # get current filter
        module = self.module
        if isinstance(module, IFilters):
            self._motion_status = await module.get_motion_status()
            self._filter = await module.get_filter()
            self._filters = await module.list_filters()

        # update gui
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        # enable myself and set filter
        self.setEnabled(True)
        self.textStatus.setText(self._motion_status.name)
        self.textFilter.setText("" if self._filter is None else self._filter)
        initialized = self._motion_status in [
            MotionStatus.SLEWING,
            MotionStatus.TRACKING,
            MotionStatus.IDLE,
            MotionStatus.POSITIONED,
        ]
        self.buttonSetFilter.setEnabled(initialized)

    async def _on_filter_changed(self, event: Event, sender: str) -> bool:
        """Called when filter changed.

        Args:
            event: Filter change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name or not isinstance(event, FilterChangedEvent):
            return False

        # store new filter
        self._filter = event.filter

        # trigger GUI update
        self.signal_update_gui.emit()
        return True

    async def _on_motion_status_changed(self, event: Event, sender: str) -> bool:
        """Called when motion status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name or not isinstance(event, MotionStatusChangedEvent):
            return False

        # store new status
        if "IFilters" in event.interfaces:
            self._motion_status = event.interfaces["IFilters"]
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()
        return True

    async def _update(self) -> None:
        # get filter and motion status
        module = self.module
        if isinstance(module, IFilters):
            self._filter = await module.get_filter()
            self._motion_status = await module.get_motion_status()

        # signal GUI update
        self.signal_update_gui.emit()

    @qasync.asyncSlot()  # type: ignore
    async def set_filter(self) -> None:
        # ask for value
        module = self.module
        new_value, ok = QtWidgets.QInputDialog.getItem(self, "Set filter", "New filter", self._filters, 0, False)
        if ok and isinstance(module, IFilters):
            self.run_background(module.set_filter, new_value)


__all__ = ["FilterWidget"]
