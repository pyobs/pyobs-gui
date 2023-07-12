import asyncio
from datetime import datetime
from enum import Enum, EnumMeta
from typing import Any, Type, Dict, Optional, Union, get_origin, get_args, List
from PyQt5 import QtWidgets, QtCore
import inspect

from astroplan import Observer

import pyobs.events
from pyobs.comm import Comm, Proxy
from pyobs.events import LogEvent, Event
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .qt.eventswidget_ui import Ui_EventsWidget


class EventsWidget(QtWidgets.QWidget, BaseWidget, Ui_EventsWidget):
    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # set up table
        self.tableEvents.setColumnCount(4)
        self.tableEvents.setHorizontalHeaderLabels(["Time", "Sender", "Event", "Data"])
        self.tableEvents.setColumnWidth(0, 80)
        self.tableEvents.setColumnWidth(1, 100)
        self.tableEvents.setColumnWidth(2, 200)

    async def open(
        self,
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        # loop all event types
        for name, cls in pyobs.events.__dict__.items():
            if isinstance(cls, type):
                # register event
                await self.comm.register_event(cls, self._handle_event)

                # get c'tor
                ctor = getattr(cls, "__init__")
                sig = inspect.signature(ctor)
                params = (
                    []
                    if len(sig.parameters) < 2
                    else [p.name for p in sig.parameters.values() if p.name not in ["self", "args", "kwargs"]]
                )

                # build name
                name = "%s (%s)" % (cls.__name__, ", ".join(params))

                # add to combo
                self.comboEvent.addItem(name, cls)

    async def _handle_event(self, event: pyobs.events.Event, sender: str):
        """Handle any incoming event.

        Args:
            event: Event itself.
            sender: Sender of event.
        """

        # ignore log events
        if isinstance(event, LogEvent):
            return

        # add row to table
        self.tableEvents.insertRow(0)

        # get time
        time = datetime.fromtimestamp(event.timestamp)

        # fill it
        self.tableEvents.setItem(0, 0, QtWidgets.QTableWidgetItem(time.strftime("%H:%M:%S")))
        self.tableEvents.setItem(0, 1, QtWidgets.QTableWidgetItem(sender))
        self.tableEvents.setItem(0, 2, QtWidgets.QTableWidgetItem(event.__class__.__name__))
        self.tableEvents.setItem(0, 3, QtWidgets.QTableWidgetItem(str(event.data)))

        # limit number of rows
        if self.tableEvents.rowCount() > 500:
            self.tableEvents.setRowCount(400)

    @QtCore.pyqtSlot()
    def on_buttonSend_clicked(self) -> None:
        # get event class
        cls = self.comboEvent.itemData(self.comboEvent.currentIndex())

        # open dialog
        dlg = SendEventDialog(self.comm, cls)
        dlg.exec_()


class SendEventDialog(QtWidgets.QDialog):
    def __init__(self, comm: Comm, event: Type[Event], **kwargs: Any):
        QtWidgets.QDialog.__init__(self, **kwargs)

        # save event type
        self._event = event
        self._comm = comm

        # add layout
        layout = QtWidgets.QFormLayout()
        self.setLayout(layout)

        # add label with event name
        title = QtWidgets.QLabel(event.__name__)
        layout.addWidget(title)

        # get c'tor and its params
        ctor = getattr(event, "__init__")
        sig = inspect.signature(ctor)

        # add input for every param
        self._widgets = {}
        for p in sig.parameters:
            if p not in ["self", "args", "kwargs"]:
                # get annotation
                ann = sig.parameters[p].annotation

                # optional?
                optional = False
                if get_origin(ann) is Union and type(None) in get_args(ann):
                    # get first not-None type hint
                    ann = list(filter(lambda x: x is not None, get_args(ann)))[0]
                    optional = True

                # create widget
                if ann == int:
                    widget = QtWidgets.QSpinBox()
                    widget.setMinimum(-100000)
                    widget.setMaximum(100000)
                elif ann == float:
                    widget = QtWidgets.QDoubleSpinBox()
                    widget.setMinimum(-1e5)
                    widget.setMaximum(1e5)
                elif type(ann) == EnumMeta:
                    widget = QtWidgets.QComboBox()
                    widget.addItems([a.value for a in ann])
                else:
                    widget = QtWidgets.QLineEdit()

                # create checkbox and layout
                widget_layout = QtWidgets.QHBoxLayout()
                checkbox = QtWidgets.QCheckBox()
                widget_layout.addWidget(checkbox)
                if not optional:
                    checkbox.setChecked(True)
                    checkbox.setEnabled(False)
                widget_layout.addWidget(widget)

                # store widget
                self._widgets[p] = (checkbox, widget, ann)

                # add to layout
                layout.addRow(p, widget_layout)

        # add dialog button box
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._send_event)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _send_event(self) -> None:
        """Actually send event."""

        # collect values
        values: Dict[str, Any] = {}
        for name, (checkbox, widget, ann) in self._widgets.items():
            if checkbox is not None and not checkbox.isChecked():
                values[name] = None
            else:
                if isinstance(widget, QtWidgets.QLineEdit):
                    values[name] = ann(widget.text())
                elif isinstance(widget, QtWidgets.QComboBox):
                    values[name] = ann(widget.currentText())
                else:
                    values[name] = widget.value()

        # create event and send it
        event = self._event(**values)
        asyncio.create_task(self._comm.send_event(event))

        # accept dialog
        self.accept()
