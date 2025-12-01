import functools
from typing import Any, cast
from PySide6 import QtWidgets, QtCore, QtGui  # type: ignore
from astroplan import Observer

from pyobs.comm import Proxy, Comm
from pyobs.events import MotionStatusChangedEvent, Event, ModeChangedEvent
from pyobs.interfaces import IFilters, IMode, IMotion
from pyobs.utils.enums import MotionStatus
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .qt.modewidget_ui import Ui_ModeWidget


class ModeWidget(BaseWidget, Ui_ModeWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, update_func=self._update, update_interval=10, **kwargs)
        self.setupUi(self)  # type: ignore

        # variables
        self._mode_groups: list[str] = []
        self._mode_options: list[list[str]] = [[]]
        self._modes: list[str] = []
        self._motion_status = MotionStatus.UNKNOWN
        self._mode_widgets: list[tuple[QtWidgets.QLineEdit, QtWidgets.QToolButton]] = []

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def open(
        self,
        modules: list[Proxy] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        # subscribe to events
        await self.comm.register_event(ModeChangedEvent, self._on_mode_changed)
        await self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

    async def _init(self) -> None:
        module = self.module

        if isinstance(module, IMotion):
            self._motion_status = await module.get_motion_status()

        # get current filter
        if isinstance(module, IMode):
            self._mode_groups = await module.list_mode_groups()
            self._mode_options = [await module.list_modes(i) for i in range(len(self._mode_groups))]
            await self._update_modes()

            # add widgets
            self._mode_widgets = []
            for i in range(len(self._mode_groups)):
                layout = QtWidgets.QHBoxLayout()
                current = QtWidgets.QLineEdit()
                current.setReadOnly(True)
                current.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(current)
                button = QtWidgets.QToolButton()
                button.setIcon(QtGui.QIcon(":/resources/edit-solid.svg"))
                self.colorize_button(button, QtCore.Qt.GlobalColor.green)
                button.clicked.connect(functools.partial(self.set_mode, i))
                layout.addWidget(button)
                self._mode_widgets.append((current, button))
                cast(QtWidgets.QFormLayout, self.groupBox.layout()).addRow(self._mode_groups[i], layout)

        # update gui
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        # enable myself and set filter
        self.setEnabled(True)
        self.textStatus.setText(self._motion_status.name)
        initialized = self._motion_status in [
            MotionStatus.SLEWING,
            MotionStatus.TRACKING,
            MotionStatus.IDLE,
            MotionStatus.POSITIONED,
        ]
        for i in range(len(self._mode_groups)):
            self._mode_widgets[i][0].setText(str(self._modes[i]))
            self._mode_widgets[i][1].setEnabled(initialized)

    async def _on_mode_changed(self, event: Event, sender: str) -> bool:
        """Called when mode changed.

        Args:
            event: Mode change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name or not isinstance(event, ModeChangedEvent):
            return False

        # store new filter
        g = self._mode_groups.index(event.group)
        self._modes[g] = event.mode

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
        module = self.module
        if isinstance(module, IMode):
            self._modes = [await module.get_mode(i) for i in range(len(self._mode_groups))]

    async def _update(self) -> None:
        # get mode and motion status
        module = self.module
        if isinstance(module, IFilters):
            await self._update_modes()
            self._motion_status = await module.get_motion_status()

        # signal GUI update
        self.signal_update_gui.emit()

    @QtCore.Slot(int)  # type: ignore
    def set_mode(self, group: int) -> None:
        # ask for value
        mode = self._mode_groups[group]
        new_value, ok = QtWidgets.QInputDialog.getItem(
            self, f"Set {mode}", f"New {mode}", self._mode_options[group], 0, False
        )
        module = self.module
        if ok and isinstance(module, IMode):
            self.run_background(module.set_mode, new_value, group)


__all__ = ["ModeWidget"]
