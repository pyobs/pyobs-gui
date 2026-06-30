import logging
from typing import Any

import qasync  # type: ignore
from PySide6 import QtWidgets, QtCore  # type: ignore

from pyobs.interfaces import IFocuser, FocuserState, IMotion, MotionState
from pyobs.utils.enums import MotionStatus
from .base import BaseWidget
from .qt.focuswidget_ui import Ui_FocusWidget

log = logging.getLogger(__name__)


class FocusWidget(BaseWidget, Ui_FocusWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._focus: float | None = None
        self._focus_offset: float | None = None
        self._motion_status = MotionStatus.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butSetFocusBase.clicked.connect(self._set_focus_base)
        self.butSetFocusOffset.clicked.connect(self._set_focus_offset)
        self.buttonResetFocusOffset.clicked.connect(self._reset_focus_offset)

        # button colors
        self.colorize_button(self.butSetFocusBase, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.butSetFocusOffset, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonResetFocusOffset, QtCore.Qt.GlobalColor.yellow)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IFocuser, self._on_focuser_state)
        await self.comm.subscribe_state(self.module, IMotion, self._on_motion_state)

    def _on_focuser_state(self, state: FocuserState) -> None:
        self._focus = state.focus
        self._focus_offset = state.focus_offset
        self.signal_update_gui.emit()

    def _on_motion_state(self, state: MotionState) -> None:
        self._motion_status = state.status
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.setEnabled(True)
        self.labelCurStatus.setText(self._motion_status)
        self.labelCurFocusBase.setText("" if self._focus is None else f"{self._focus:.3f}")
        self.labelCurFocusOffset.setText("" if self._focus_offset is None else f"{self._focus_offset:.3f}")
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

    @qasync.asyncSlot()  # type: ignore
    async def _set_focus_base(self) -> None:
        value = self._focus or 0.0
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, "Focus", "New value", value, 0, 100, 2)
        if ok:
            async with self.comm.proxy(self.module, IFocuser) as proxy:
                await proxy.set_focus(new_value)

    @qasync.asyncSlot()  # type: ignore
    async def _set_focus_offset(self) -> None:
        value = self._focus_offset or 0.0
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, "Focus offset", "New value", value, -5, 5, 2)
        if ok:
            async with self.comm.proxy(self.module, IFocuser) as proxy:
                await proxy.set_focus_offset(new_value)

    @qasync.asyncSlot()  # type: ignore
    async def _reset_focus_offset(self) -> None:
        async with self.comm.proxy(self.module, IFocuser) as proxy:
            await proxy.set_focus_offset(0.0)


__all__ = ["FocusWidget"]
