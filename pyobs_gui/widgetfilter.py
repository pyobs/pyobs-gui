from PyQt5.QtCore import pyqtSignal
import threading

from pyobs.events import FilterChangedEvent, MotionStatusChangedEvent
from pyobs.interfaces import IFilters, IMotion
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetfilter import Ui_WidgetFilter


class WidgetFilter(BaseWidget, Ui_WidgetFilter):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, parent=None):
        BaseWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: IFilters
        self.comm = comm        # type: Comm

        # variables
        self._filter = None
        self._motion_status = IMotion.Status.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butSetFilter.clicked.connect(lambda: self.run_async(self.module.set_filter,
                                                                 self.comboFilter.currentText()))

        # subscribe to events
        self.comm.register_event(FilterChangedEvent, self._on_filter_changed)
        self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

    def _init(self):
        # get all filters
        if isinstance(self.module, IFilters):
            self.comboFilter.addItems(self.module.list_filters().wait())

        # get current filter
        self._motion_status = self.module.get_motion_status().wait()
        self._filter = self.module.get_filter().wait()

        # update gui
        self.signal_update_gui.emit()

    def update_gui(self):
        # enable myself and set filter
        self.setEnabled(True)
        self.labelCurStatus.setText(self._motion_status.name)
        self.labelCurFilter.setText('' if self._filter is None else self._filter)

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
