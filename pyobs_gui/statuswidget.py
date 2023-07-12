import asyncio
from asyncio import Task
from datetime import datetime
from typing import Any, Type, Dict, Optional, cast, Union, List
from PyQt5 import QtWidgets, QtCore
import inspect

from astroplan import Observer

import pyobs.events
from pyobs.comm import Comm, Proxy
from pyobs.events import LogEvent, Event, ModuleOpenedEvent, ModuleClosedEvent
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

    def button_clicked(self) -> None:
        """Do button action."""

        # for now, it's always clear error
        asyncio.create_task(self.module.reset_error())


class StatusWidget(QtWidgets.QTableWidget, BaseWidget):
    def __init__(self, **kwargs: Any):
        QtWidgets.QTableWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update_status, **kwargs)

        # table settings
        self.setColumnCount(3)
        self.setHorizontalHeaderLabels(["Module", "Version", "Status"])
        self.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setMinimumSectionSize(200)
        self.verticalHeader().hide()

        # stuff
        self._status_task: Optional[Task] = None

    async def open(
        self,
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        # register events
        await self.comm.register_event(ModuleOpenedEvent, self._module_opened)
        await self.comm.register_event(ModuleClosedEvent, self._module_closed)

        # add all existing modules
        for mod in self.comm.clients:
            await self._module_opened(ModuleOpenedEvent(), mod)

        # trigger status updates
        # self._status_task = asyncio.create_task(self._update_status())

    async def _module_opened(self, event: Event, sender: str) -> bool:
        """Called when module was opened."""
        if not isinstance(event, ModuleOpenedEvent):
            return False

        # add module
        proxy = await self.comm.proxy(sender)
        await self._add_module(proxy)
        return True

    async def _module_closed(self, event: Event, sender: str) -> bool:
        """Called when module was closed."""
        if not isinstance(event, ModuleClosedEvent):
            return False

        # find and remove it
        for row in range(self.rowCount()):
            if self.item(row, 0).text() == sender:
                self.removeRow(row)
                break

        # success
        return True

    async def _add_module(self, module: Proxy) -> None:
        # add row
        row = self.rowCount()
        self.setRowCount(row + 1)

        # set module name
        item = QtWidgets.QTableWidgetItem(module.name)
        item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.setItem(row, 0, item)

        # set version
        if isinstance(module, IModule):
            item = QtWidgets.QTableWidgetItem(await module.get_version())
            item.setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.setItem(row, 1, item)

        # add widget for status
        widget = StatusItem(self.comm, module)
        item = QtWidgets.QTableWidgetItem()
        item.setSizeHint(widget.minimumSizeHint())
        self.setItem(row, 2, item)
        self.setCellWidget(row, 2, widget)

        # sort
        self.resizeRowsToContents()
        self.sortItems(0)

    async def _update_status(self) -> None:
        """Update status for all modules."""

        while True:
            # loop all rows
            futures = []
            for row in range(self.rowCount()):
                # get widget and update it
                widget = self.cellWidget(row, 2)
                if widget is not None:
                    futures.append(asyncio.create_task(widget.update_status()))

            # await futures
            for fut in futures:
                await fut

            # sleep a little
            await asyncio.sleep(5)
