import functools
from typing import Any, cast
from PySide6 import QtWidgets, QtCore, QtGui  # type: ignore
from astroplan import Observer

from pyobs.comm import Comm
from pyobs.events import Event, ModeChangedEvent
from pyobs.interfaces import IMode, ModeState, IMotion, MotionState
from pyobs.utils.enums import MotionStatus
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .qt.modewidget_ui import Ui_ModeWidget


class ModeWidget(BaseWidget, Ui_ModeWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._mode_groups: list[str] = []
        self._mode_options: dict[str, list[str]] = {}
        self._modes: dict[str, str] = {}
        self._motion_status = MotionStatus.UNKNOWN
        self._mode_widgets: dict[str, tuple[QtWidgets.QLineEdit, QtWidgets.QToolButton]] = {}

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def open(
        self,
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        await self.register_event(ModeChangedEvent, self._on_mode_changed)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IMotion, self._on_motion_state)

        # permitted methods (ACLs)
        await self._fetch_permitted_methods()

        # read capabilities (static: available modes per group)
        caps = await self.comm.get_capabilities(self.module, IMode)
        if caps is not None:
            self._mode_groups = list(caps.modes.keys())
            self._mode_options = dict(caps.modes)

            self._mode_widgets = {}
            for group in self._mode_groups:
                layout = QtWidgets.QHBoxLayout()
                current = QtWidgets.QLineEdit()
                current.setReadOnly(True)
                current.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
                layout.addWidget(current)
                button = QtWidgets.QToolButton()
                button.setIcon(QtGui.QIcon(":/resources/edit-solid.svg"))
                self.colorize_button(button, QtCore.Qt.GlobalColor.green)
                button.clicked.connect(functools.partial(self.set_mode, group))
                layout.addWidget(button)
                self._mode_widgets[group] = (current, button)
                cast("QtWidgets.QFormLayout", self.groupBox.layout()).addRow(group, layout)

            # subscribe to live mode state
            await self.comm.subscribe_state(self.module, IMode, self._on_mode_state)

        self.signal_update_gui.emit()

    def _on_motion_state(self, state: MotionState) -> None:
        self._motion_status = state.status
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.setEnabled(True)
        self.textStatus.setText(self._motion_status.name)
        initialized = self._motion_status in [
            MotionStatus.SLEWING,
            MotionStatus.TRACKING,
            MotionStatus.IDLE,
            MotionStatus.POSITIONED,
        ]
        for group in self._mode_groups:
            current, button = self._mode_widgets[group]
            current.setText(self._modes.get(group, ""))
            button.setEnabled(initialized and self.permitted("set_mode"))

    def _on_mode_state(self, state: ModeState) -> None:
        self._modes = dict(state.modes)
        self.signal_update_gui.emit()

    async def _on_mode_changed(self, event: Event, sender: str) -> bool:
        """Keep for backwards compat with modules that still send ModeChangedEvent."""
        if sender != self.module or not isinstance(event, ModeChangedEvent):
            return False
        if event.group in self._mode_groups:
            self._modes[event.group] = event.mode
            self.signal_update_gui.emit()
        return True

    @QtCore.Slot(str)  # type: ignore
    def set_mode(self, group: str) -> None:
        new_value, ok = QtWidgets.QInputDialog.getItem(
            self, f"Set {group}", f"New {group}", self._mode_options[group], 0, False
        )
        if ok:

            async def _do_set_mode() -> None:
                async with self.comm.proxy(self.module, IMode) as proxy:
                    await proxy.set_mode(new_value, group)

            self.run_background(_do_set_mode)


__all__ = ["ModeWidget"]
