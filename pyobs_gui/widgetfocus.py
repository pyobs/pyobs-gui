import threading
import logging
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from pyobs.events import MotionStatusChangedEvent

from pyobs.interfaces import IFocuser, IMotion
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetfocus import Ui_WidgetFocus


log = logging.getLogger(__name__)


class WidgetFocus(BaseWidget, Ui_WidgetFocus):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update, update_interval=5)
        self.setupUi(self)
        self.module = module    # type: IFocuser
        self.comm = comm        # type: Comm

        # variables
        self._focus = None
        self._motion_status = IMotion.Status.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butSetFocus.clicked.connect(lambda: self.run_async(self.module.set_focus,
                                                                self.spinFocus.value()))

        # subscribe to events
        self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

    def _init(self):
        # get current filter
        self._focus = self.module.get_focus().wait()
        self._motion_status = self.module.get_motion_status().wait()
        self.signal_update_gui.emit()

    def update_gui(self):
        # enable myself and set filter
        self.setEnabled(True)
        self.labelCurStatus.setText(self._motion_status.name)
        self.labelCurFocus.setText('' if self._focus is None else '%.3f' % self._focus)

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
        if 'IFocuser' in event.interfaces:
            self._motion_status = event.interfaces['IFocuser']
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()

    def _update(self):
        # get focus and motion status
        self._focus = self.module.get_focus().wait()
        self._motion_status = self.module.get_motion_status().wait()

        # signal GUI update
        self.signal_update_gui.emit()


__all__ = ['WidgetFocus']
