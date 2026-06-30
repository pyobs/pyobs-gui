import asyncio
from typing import Any

import qasync
from PySide6 import QtWidgets, QtCore  # type: ignore
from astroplan import Observer

from pyobs.comm import Comm
from pyobs.events import Event, ModuleOpenedEvent, ModuleClosedEvent
from pyobs.interfaces import IModule
from pyobs.utils.enums import ModuleState
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.base import BaseWidget


class StatusItem(QtWidgets.QWidget):
    signal_presence = QtCore.Signal(object, str)

    def __init__(self, comm: Comm, module: str):
        QtWidgets.QWidget.__init__(self)

        self.setAutoFillBackground(True)

        layout = QtWidgets.QHBoxLayout()
        self.labelStatus = QtWidgets.QLabel("UNKNOWN")
        self.labelStatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.buttonAction = QtWidgets.QPushButton("Clear error")
        self.buttonAction.setVisible(False)
        layout.addWidget(self.labelStatus)
        layout.addWidget(self.buttonAction)
        layout.setStretch(0, 3)
        layout.setStretch(1, 1)
        self.setLayout(layout)

        self.signal_presence.connect(self._apply_presence)
        self.buttonAction.clicked.connect(self.button_clicked)

        self.comm = comm
        self.name = module

    def on_presence_changed(self, state: ModuleState, error_string: str) -> None:
        """Presence callback — emits signal so Qt update happens on the main thread."""
        self.signal_presence.emit(state, error_string)

    @QtCore.Slot(object, str)  # type: ignore
    def _apply_presence(self, state: ModuleState, error_string: str) -> None:
        if state == ModuleState.READY:
            self.labelStatus.setText("READY")
            self.setStyleSheet("background-color: lime; color: black;")
            self.buttonAction.setVisible(False)
        elif state == ModuleState.ERROR:
            self.labelStatus.setText(f"ERROR: {error_string}")
            self.setStyleSheet("background-color: red; color: black;")
            self.buttonAction.setVisible(True)
        elif state == ModuleState.CLOSED:
            self.labelStatus.setText("OFFLINE")
            self.setStyleSheet("background-color: gray; color: white;")
            self.buttonAction.setVisible(False)
        else:
            self.labelStatus.setText(state.value.upper())
            self.setStyleSheet("background-color: yellow; color: black;")
            self.buttonAction.setVisible(False)

    @qasync.asyncSlot()  # type: ignore
    async def button_clicked(self) -> None:
        async with self.comm.proxy(self.name, IModule) as proxy:
            await proxy.reset_error()


class StatusWidget(BaseWidget):
    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)

        self.table = QtWidgets.QTableWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Module", "Version", "Status"])
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(200)
        self.table.verticalHeader().hide()

    async def open(
        self,
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        if self.comm is not None:
            await self.comm.register_event(ModuleOpenedEvent, self._module_opened)
            await self.comm.register_event(ModuleClosedEvent, self._module_closed)
            asyncio.create_task(self._init_clients())

    async def _init_clients(self) -> None:
        for client_name in self.comm.clients:
            await self._module_opened(ModuleOpenedEvent(), client_name)

    async def _module_opened(self, event: Event, sender: str) -> bool:
        if not isinstance(event, ModuleOpenedEvent):
            return False
        if self.comm is None:
            return False
        await self._add_module(sender)
        return True

    async def _module_closed(self, event: Event, sender: str) -> bool:
        if not isinstance(event, ModuleClosedEvent):
            return False
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None and item.text() == sender:
                self.table.removeRow(row)
                break
        return True

    async def _add_module(self, module: str) -> None:
        row = self.table.rowCount()
        self.table.setRowCount(row + 1)

        name_item = QtWidgets.QTableWidgetItem(module)
        name_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, name_item)

        # version from capabilities (read once, static)
        caps = await self.comm.get_capabilities(module, IModule)
        if caps is not None:
            ver_item = QtWidgets.QTableWidgetItem(caps.version)
            ver_item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, ver_item)

        # status widget — subscribe_presence delivers current state immediately
        widget = StatusItem(self.comm, module)
        size_item = QtWidgets.QTableWidgetItem()
        size_item.setSizeHint(widget.minimumSizeHint())
        self.table.setItem(row, 2, size_item)
        self.table.setCellWidget(row, 2, widget)
        await self.comm.subscribe_presence(module, widget.on_presence_changed)

        self.table.resizeRowsToContents()
        self.table.sortItems(0)
