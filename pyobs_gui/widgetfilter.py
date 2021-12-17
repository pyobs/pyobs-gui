import asyncio

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from pyobs.comm import Comm
from pyobs.events import FilterChangedEvent, MotionStatusChangedEvent, Event
from pyobs.interfaces import IFilters
from pyobs.utils.enums import MotionStatus
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetfilter import Ui_WidgetFilter


class WidgetFilter(BaseWidget, Ui_WidgetFilter):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs):
        BaseWidget.__init__(self, update_func=self._update, update_interval=10, **kwargs)
        self.setupUi(self)

        # variables
        self._filter = None
        self._motion_status = MotionStatus.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

        # button colors
        self.colorize_button(self.buttonSetFilter, QtCore.Qt.green)

    async def open(self):
        """Open widget."""
        await BaseWidget.open(self)

        # subscribe to events
        await self.comm.register_event(FilterChangedEvent, self._on_filter_changed)
        await self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

    async def _init(self):
        # get current filter
        self._motion_status = await self.module.get_motion_status()
        self._filter = await self.module.get_filter()

        # update gui
        self.signal_update_gui.emit()

    def update_gui(self):
        # enable myself and set filter
        self.setEnabled(True)
        self.textStatus.setText(self._motion_status.name)
        self.textFilter.setText('' if self._filter is None else self._filter)
        initialized = self._motion_status in [MotionStatus.SLEWING, MotionStatus.TRACKING,
                                              MotionStatus.IDLE, MotionStatus.POSITIONED]
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
        if 'IFilters' in event.interfaces:
            self._motion_status = event.interfaces['IFilters']
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()
        return True

    async def _update(self):
        # get filter and motion status
        self._filter = await self.module.get_filter()
        self._motion_status = await self.module.get_motion_status()

        # signal GUI update
        self.signal_update_gui.emit()

    #@pyqtSlot(name='on_buttonSetFilter_clicked')
    def on_buttonSetFilter_clicked(self):
        asyncio.create_task(self._set_filter())

    async def _set_filter(self):
        # get filters
        filters = await self.module.list_filters()

        # ask for value
        new_value, ok = QtWidgets.QInputDialog.getItem(self, 'Set filter', 'New filter', filters, 0, False)
        if ok:
            self.run_background(self.module.set_filter, new_value)


__all__ = ['WidgetFilter']
