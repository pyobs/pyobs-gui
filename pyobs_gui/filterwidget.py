from typing import List, Any, Optional, Union, Dict
from PyQt5 import QtWidgets, QtCore
from astroplan import Observer

from pyobs.comm import Proxy, Comm
from pyobs.events import FilterChangedEvent, MotionStatusChangedEvent, Event
from pyobs.interfaces import IFilters
from pyobs.utils.enums import MotionStatus
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .qt.filterwidget_ui import Ui_FilterWidget


class FilterWidget(QtWidgets.QWidget, BaseWidget, Ui_FilterWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, update_interval=10, **kwargs)
        self.setupUi(self)

        # variables
        self._filter: Optional[str] = None
        self._filters: List[str] = []
        self._motion_status = MotionStatus.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

        # button colors
        self.colorize_button(self.buttonSetFilter, QtCore.Qt.green)

    async def open(
        self,
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        # subscribe to events
        await self.comm.register_event(FilterChangedEvent, self._on_filter_changed)
        await self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

    async def _init(self) -> None:
        # get current filter
        if isinstance(self.module, IFilters):
            self._motion_status = await self.module.get_motion_status()
            self._filter = await self.module.get_filter()
            self._filters = await self.module.list_filters()

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
        if isinstance(self.module, IFilters):
            self._filter = await self.module.get_filter()
            self._motion_status = await self.module.get_motion_status()

        # signal GUI update
        self.signal_update_gui.emit()

    @QtCore.pyqtSlot(name="on_buttonSetFilter_clicked")
    def set_filter(self) -> None:
        # ask for value
        new_value, ok = QtWidgets.QInputDialog.getItem(self, "Set filter", "New filter", self._filters, 0, False)
        if ok and isinstance(self.module, IFilters):
            self.run_background(self.module.set_filter, new_value)


__all__ = ["FilterWidget"]
