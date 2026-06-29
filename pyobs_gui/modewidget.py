import functools
from typing import Any, cast
from PySide6 import QtWidgets, QtCore, QtGui  # type: ignore
from astroplan import Observer

from pyobs.comm import Proxy, Comm
from pyobs.events import Event, ModeChangedEvent
from pyobs.interfaces import IMode, IMotion
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

        await self.comm.register_event(ModeChangedEvent, self._on_mode_changed)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IMotion, self._on_motion_state)

        if await self.comm.has_proxy(self.module, IMode):
            async with self.comm.proxy(self.module, IMode) as proxy:
                self._mode_groups = await proxy.list_mode_groups()
                self._mode_options = [await proxy.list_modes(i) for i in range(len(self._mode_groups))]
                self._modes = [await proxy.get_mode(i) for i in range(len(self._mode_groups))]

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
                cast("QtWidgets.QFormLayout", self.groupBox.layout()).addRow(self._mode_groups[i], layout)

        self.signal_update_gui.emit()

    def _on_motion_state(self, state: IMotion.State) -> None:
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
        for i in range(len(self._mode_groups)):
            self._mode_widgets[i][0].setText(self._modes[i])
            self._mode_widgets[i][1].setEnabled(initialized)

    async def _on_mode_changed(self, event: Event, sender: str) -> bool:
        if sender != self.module or not isinstance(event, ModeChangedEvent):
            return False

        g = self._mode_groups.index(event.group)
        self._modes[g] = event.mode
        self.signal_update_gui.emit()
        return True

    @QtCore.Slot(int)  # type: ignore
    def set_mode(self, group: int) -> None:
        mode = self._mode_groups[group]
        new_value, ok = QtWidgets.QInputDialog.getItem(
            self, f"Set {mode}", f"New {mode}", self._mode_options[group], 0, False
        )
        if ok:
            async def _do_set_mode() -> None:
                async with self.comm.proxy(self.module, IMode) as proxy:
                    await proxy.set_mode(new_value, group)

            self.run_background(_do_set_mode)


__all__ = ["ModeWidget"]