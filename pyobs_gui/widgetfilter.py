from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
import threading

from pyobs.comm import Comm
from pyobs.events import FilterChangedEvent, MotionStatusChangedEvent
from pyobs.interfaces import IFilters, IMotion
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetfilter import Ui_WidgetFilter


class WidgetFilter(BaseWidget, Ui_WidgetFilter):
    signal_update_gui = pyqtSignal()

    def __init__(self, module: IFilters, comm: Comm, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update, update_interval=10)
        self.setupUi(self)
        self.module = module
        self.comm = comm

        # variables
        self._filter = None
        self._motion_status = IMotion.Status.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

        # button colors
        self.colorize_button(self.buttonSetFilter, QtCore.Qt.green)

        # subscribe to events
        self.comm.register_event(FilterChangedEvent, self._on_filter_changed)
        self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

    def _init(self):
        # get current filter
        self._motion_status = self.module.get_motion_status().wait()
        self._filter = self.module.get_filter().wait()

        # update gui
        self.signal_update_gui.emit()

    def update_gui(self):
        # enable myself and set filter
        self.setEnabled(True)
        self.textStatus.setText(self._motion_status.name)
        self.textFilter.setText('' if self._filter is None else self._filter)
        initialized = self._motion_status in [IMotion.Status.SLEWING, IMotion.Status.TRACKING,
                                              IMotion.Status.IDLE, IMotion.Status.POSITIONED]
        self.buttonSetFilter.setEnabled(initialized)

    def _on_filter_changed(self, event: FilterChangedEvent, sender: str):
        """Called when filter changed.

        Args:
            event: Filter change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name:
            return

        # store new filter
        self._filter = event.filter

        # trigger GUI update
        self.signal_update_gui.emit()

    def _on_motion_status_changed(self, event: MotionStatusChangedEvent, sender: str):
        """Called when motion status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name:
            return

        # store new status
        if 'IFilters' in event.interfaces:
            self._motion_status = event.interfaces['IFilters']
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()

    def _update(self):
        # get filter and motion status
        self._filter = self.module.get_filter().wait()
        self._motion_status = self.module.get_motion_status().wait()

        # signal GUI update
        self.signal_update_gui.emit()

    @pyqtSlot(name='on_buttonSetFilter_clicked')
    def _set_filter(self):
        # get filters
        filters = self.module.list_filters().wait()

        # ask for value
        new_value, ok = QtWidgets.QInputDialog.getItem(self, 'Set filter', 'New filter', filters, 0, False)
        if ok:
            self.run_async(self.module.set_filter, new_value)


__all__ = ['WidgetFilter']
