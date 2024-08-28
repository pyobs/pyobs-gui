import functools
from typing import List, Any, Optional, Union, Dict
from PyQt5 import QtWidgets, QtCore, Qt
from astroplan import Observer

from pyobs.comm import Proxy, Comm
from pyobs.events import FilterChangedEvent, MotionStatusChangedEvent, Event
from pyobs.interfaces import IFilters, IMode
from pyobs.utils.enums import MotionStatus
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .qt.modewidget_ui import Ui_ModeWidget


class ModeWidget(QtWidgets.QWidget, BaseWidget, Ui_ModeWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, update_interval=10, **kwargs)
        self.setupUi(self)

        # variables
        self._mode_groups: List[str] = []
        self._mode_options: List[List[str]] = [[]]
        self._modes = List[int]
        self._motion_status = MotionStatus.UNKNOWN
        self._mode_widgets: List[QtWidgets.QLineEdit] = []

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

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
        if isinstance(self.module, IMode):
            self._mode_groups = await self.module.list_mode_groups()
            self._mode_options = [await self.module.list_modes(i) for i in range(len(self._mode_groups))]
            await self._update_modes()
            print(self._mode_groups)
            print(self._mode_options)

            # add widgets
            self._mode_widgets = []
            for i in range(len(self._mode_groups)):
                layout = QtWidgets.QHBoxLayout()
                current = QtWidgets.QLineEdit()
                current.setReadOnly(True)
                current.setAlignment(QtCore.Qt.AlignCenter)
                self._mode_widgets.append(current)
                layout.addWidget(current)
                button = QtWidgets.QToolButton()
                button.setIcon(Qt.QIcon(":/resources/edit-solid.svg"))
                self.colorize_button(button, QtCore.Qt.green)
                button.clicked.connect(functools.partial(self.set_mode, i))
                layout.addWidget(button)
                self.groupBox.layout().addRow(self._mode_groups[i], layout)

        # update gui
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        # enable myself and set filter
        self.setEnabled(True)
        self.textStatus.setText(self._motion_status.name)
        for i in range(len(self._mode_groups)):
            self._mode_widgets[i].setText(self._modes[i])
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
        if "IMode" in event.interfaces:
            self._motion_status = event.interfaces["IMode"]
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()
        return True

    async def _update_modes(self) -> None:
        self._modes = [await self.module.get_mode(i) for i in range(len(self._mode_groups))]

    async def _update(self) -> None:
        # get mode and motion status
        if isinstance(self.module, IFilters):
            await self._update_modes()
            self._motion_status = await self.module.get_motion_status()

        # signal GUI update
        self.signal_update_gui.emit()

    @QtCore.pyqtSlot(int)
    def set_mode(self, group: int) -> None:
        # ask for value
        mode = self._mode_groups[group]
        new_value, ok = QtWidgets.QInputDialog.getItem(
            self, f"Set {mode}", f"New {mode}", self._mode_options[group], 0, False
        )
        if ok and isinstance(self.module, IMode):
            self.run_background(self.module.set_mode, new_value, group)


__all__ = ["ModeWidget"]
