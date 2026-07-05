from typing import Any

import qasync
from PySide6 import QtWidgets, QtCore  # type: ignore

from pyobs.interfaces import IFilters, FilterState, IMotion, MotionState
from pyobs.utils.enums import MotionStatus
from .base import BaseWidget
from .qt.filterwidget_ui import Ui_FilterWidget


class FilterWidget(BaseWidget, Ui_FilterWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._filter: str | None = None
        self._filters: list[str] = []
        self._motion_status = MotionStatus.UNKNOWN

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonSetFilter.clicked.connect(self.set_filter)

        # button colors
        self.colorize_button(self.buttonSetFilter, QtCore.Qt.GlobalColor.green)

    async def _init(self) -> None:
        # capabilities (static, read once)
        caps = await self.comm.get_capabilities(self.module, IFilters)
        if caps is not None:
            self._filters = caps.filters

        # subscribe to state
        await self.comm.subscribe_state(self.module, IFilters, self._on_filter_state)
        await self.comm.subscribe_state(self.module, IMotion, self._on_motion_state)

        # permitted methods (ACLs)
        await self._fetch_permitted_methods()

    def _on_filter_state(self, state: FilterState) -> None:
        self._filter = state.filter
        self.signal_update_gui.emit()

    def _on_motion_state(self, state: MotionState) -> None:
        self._motion_status = state.status
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.setEnabled(True)
        self.textStatus.setText(self._motion_status)
        self.textFilter.setText("" if self._filter is None else self._filter)
        initialized = self._motion_status in [
            MotionStatus.SLEWING,
            MotionStatus.TRACKING,
            MotionStatus.IDLE,
            MotionStatus.POSITIONED,
        ]
        self.buttonSetFilter.setEnabled(initialized and self.permitted("set_filter"))

    @qasync.asyncSlot()  # type: ignore
    async def set_filter(self) -> None:
        new_value, ok = QtWidgets.QInputDialog.getItem(self, "Set filter", "New filter", self._filters, 0, False)
        if ok:
            async with self.comm.proxy(self.module, IFilters) as proxy:
                self.run_background(proxy.set_filter, new_value)


__all__ = ["FilterWidget"]
