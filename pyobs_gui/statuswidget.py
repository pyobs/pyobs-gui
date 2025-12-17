import asyncio
from asyncio import Task
from typing import Any, Dict, Optional, cast, Union, List

import qasync
from PySide6 import QtWidgets, QtCore  # type: ignore
from astroplan import Observer

from pyobs.comm import Comm, Proxy
from pyobs.events import Event, ModuleOpenedEvent, ModuleClosedEvent
from pyobs.interfaces import IModule
from pyobs.utils.enums import ModuleState
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.base import BaseWidget


class StatusItem(QtWidgets.QWidget):
    def __init__(self, comm: Comm, proxy: Proxy):
        QtWidgets.QWidget.__init__(self)

        # allow for background
        self.setAutoFillBackground(True)

        # add layout
        layout = QtWidgets.QHBoxLayout()

        # add fields
        self.labelStatus = QtWidgets.QLabel()
        self.labelStatus.setText("UNKNOWN")
        self.labelStatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.buttonAction = QtWidgets.QPushButton()
        self.buttonAction.setText("Clear error")
        self.buttonAction.setVisible(False)
        layout.addWidget(self.labelStatus)
        layout.addWidget(self.buttonAction)

        # set layout
        layout.setStretch(0, 3)
        layout.setStretch(1, 1)
        self.setLayout(layout)

        # connect
        self.buttonAction.clicked.connect(self.button_clicked)

        # store
        self.comm = comm
        self.name = proxy.name
        self.module = cast(IModule, proxy)

        # remember last
        self.last_state: Optional[ModuleState] = None
        self.last_error: Optional[str] = None

    async def update_status(self) -> None:
        """Update status of module and display it."""
        # get state and error string
        state = await self.module.get_state()

        # if nothing changed, end here
        if state == self.last_state:
            return

        # set status
        if state == ModuleState.READY:
            self.labelStatus.setText("READY")
            self.setStyleSheet("background-color: lime; color: black;")
            self.buttonAction.setVisible(False)

        elif state == ModuleState.ERROR:
            error = await self.module.get_error_string()
            self.labelStatus.setText(f"ERROR: {error}")
            self.setStyleSheet("background-color: red; color: black;")
            self.buttonAction.setVisible(True)
            self.last_error = error

        else:
            self.labelStatus.setText(f"{state.value.upper()}")
            self.setStyleSheet("background-color: yellow; color: black;")
            self.buttonAction.setVisible(False)

        # store it
        self.last_state = state

    @qasync.asyncSlot()  # type: ignore
    async def button_clicked(self) -> None:
        """Do button action."""

        # for now, it's always clear error
        await self.module.reset_error()


class StatusWidget(BaseWidget):
    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, update_func=self._update_status, **kwargs)

        # create table
        self.table = QtWidgets.QTableWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

        # table settings
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Module", "Version", "Status"])
        self.table.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setMinimumSectionSize(200)
        self.table.verticalHeader().hide()

        # stuff
        self._status_task: Task[Any] | None = None

    async def open(
        self,
        modules: list[Proxy] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        if self.comm is not None:
            # register events
            await self.comm.register_event(ModuleOpenedEvent, self._module_opened)
            await self.comm.register_event(ModuleClosedEvent, self._module_closed)

            # add clients
            asyncio.create_task(self._init_clients())

        # trigger status updates
        self._status_task = asyncio.create_task(self._update_status())

    async def _init_clients(self) -> None:
        # create other nav buttons and views
        for client_name in self.comm.clients:
            await self._module_opened(ModuleOpenedEvent(), client_name)

    async def _module_opened(self, event: Event, sender: str) -> bool:
        """Called when module was opened."""
        if not isinstance(event, ModuleOpenedEvent):
            return False

        # add module
        if self.comm is None:
            return False
        proxy = await self.comm.proxy(sender)
        await self._add_module(proxy)
        return True

    async def _module_closed(self, event: Event, sender: str) -> bool:
        """Called when module was closed."""
        if not isinstance(event, ModuleClosedEvent):
            return False

        # find and remove it
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item is not None and item.text() == sender:
                self.table.removeRow(row)
                break

        # success
        return True

    async def _add_module(self, module: Proxy) -> None:
        # add row
        row = self.table.rowCount()
        self.table.setRowCount(row + 1)

        # set module name
        item = QtWidgets.QTableWidgetItem(module.name)
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 0, item)

        # set version
        if isinstance(module, IModule):
            item = QtWidgets.QTableWidgetItem(await module.get_version())
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setItem(row, 1, item)

        # add widget for status
        if self.comm is not None:
            widget = StatusItem(self.comm, module)
            item = QtWidgets.QTableWidgetItem()
            item.setSizeHint(widget.minimumSizeHint())
            self.table.setItem(row, 2, item)
            self.table.setCellWidget(row, 2, widget)

        # sort
        self.table.resizeRowsToContents()
        self.table.sortItems(0)

    async def _update_status(self) -> None:
        """Update status for all modules."""

        while True:
            # loop all rows
            futures = []
            for row in range(self.table.rowCount()):
                # get widget and update it
                widget = cast(StatusItem, self.table.cellWidget(row, 2))
                if widget is not None:
                    futures.append(asyncio.create_task(widget.update_status()))

            # await futures
            for fut in futures:
                await fut

            # sleep a little
            await asyncio.sleep(5)
