import logging
from typing import Any, Optional, Union, Dict, List

from PyQt5 import QtWidgets, QtCore
from astroplan import Observer

from pyobs.comm import Proxy, Comm
from pyobs.events import MotionStatusChangedEvent, Event
from pyobs.interfaces import IFocuser

from pyobs.utils.enums import MotionStatus
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .qt.focuswidget_ui import Ui_FocusWidget


log = logging.getLogger(__name__)


class FocusWidget(QtWidgets.QWidget, BaseWidget, Ui_FocusWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, update_interval=5, **kwargs)
        self.setupUi(self)

        # variables
        self._focus: Optional[float] = None
        self._focus_offset: Optional[float] = None
        self._motion_status = MotionStatus.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butSetFocusBase.clicked.connect(lambda: self._set_focus(False))
        self.butSetFocusOffset.clicked.connect(lambda: self._set_focus(True))
        self.buttonResetFocusOffset.clicked.connect(lambda: self.run_background(self.module.set_focus_offset, 0))

        # button colors
        self.colorize_button(self.butSetFocusBase, QtCore.Qt.green)
        self.colorize_button(self.butSetFocusOffset, QtCore.Qt.green)
        self.colorize_button(self.buttonResetFocusOffset, QtCore.Qt.yellow)

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
        if self.comm is not None:
            await self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

    def _set_focus(self, offset: bool = False) -> None:
        """Asks user for new focus (offset) and sets it.

        Args:
            offset: If False, base focus is set, otherwise offset.
        """
        if not isinstance(self.module, IFocuser):
            return

        # base of offset?
        title = "Focus offset" if offset else "Focus"
        value = self._focus_offset if offset else self._focus
        minval = -5 if offset else 0
        maxval = 5 if offset else 100
        setter = self.module.set_focus_offset if offset else self.module.set_focus

        # ask for value
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, title, "New value", value, minval, maxval, 2)
        if ok:
            self.run_background(setter, new_value)

    async def _init(self) -> None:
        # get status
        try:
            if isinstance(self.module, IFocuser):
                self._focus = await self.module.get_focus()
                self._focus_offset = await self.module.get_focus_offset()
                self._motion_status = await self.module.get_motion_status()
        except:
            self._focus = None
            self._focus_offset = None
            self._motion_status = MotionStatus.UNKNOWN

        # update GUI
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        # enable myself and set filter
        self.setEnabled(True)
        self.labelCurStatus.setText(self._motion_status.name)
        self.labelCurFocusBase.setText("" if self._focus is None else "%.3f" % self._focus)
        self.labelCurFocusOffset.setText("" if self._focus_offset is None else "%.3f" % self._focus_offset)
        self.labelCurFocus.setText(
            "" if self._focus is None or self._focus_offset is None else "%.3f" % (self._focus + self._focus_offset,)
        )
        initialized = self._motion_status in [
            MotionStatus.SLEWING,
            MotionStatus.TRACKING,
            MotionStatus.IDLE,
            MotionStatus.POSITIONED,
        ]
        self.buttonResetFocusOffset.setEnabled(initialized)
        self.butSetFocusOffset.setEnabled(initialized)
        self.butSetFocusBase.setEnabled(initialized)

    async def _on_motion_status_changed(self, event: Event, sender: str) -> bool:
        """Called when motion status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if self.module is None or sender != self.module.name or not isinstance(event, MotionStatusChangedEvent):
            return False

        # store new status
        if "IFocuser" in event.interfaces:
            self._motion_status = event.interfaces["IFocuser"]
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()
        return True

    async def _update(self) -> None:
        # get focus and motion status
        if isinstance(self.module, IFocuser):
            self._focus = await self.module.get_focus()
            self._focus_offset = await self.module.get_focus_offset()
            self._motion_status = await self.module.get_motion_status()

        # signal GUI update
        self.signal_update_gui.emit()


__all__ = ["FocusWidget"]
