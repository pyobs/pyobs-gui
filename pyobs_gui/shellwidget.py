import asyncio
import pprint
from io import BytesIO
import re
from typing import Any
from PySide6 import QtWidgets, QtCore  # type: ignore
import inspect
import tokenize
from enum import Enum
import logging
from astroplan import Observer

from pyobs.comm import Comm, Proxy
from pyobs.events import ModuleOpenedEvent, Event, ModuleClosedEvent
from pyobs.utils import exceptions as exc
from pyobs.utils.shellcommand import ShellCommand
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .qt.shellwidget_ui import Ui_ShellWidget


log = logging.getLogger(__name__)


class ParserState(Enum):
    START = 0
    MODULE = 1
    MODSEP = 2
    COMMAND = 3
    OPEN = 4
    PARAM = 5
    PARAMSEP = 6
    CLOSE = 7


class CommandModel(QtCore.QAbstractTableModel):  # type: ignore
    def __init__(self, comm: Comm, *args: Any, **kwargs: Any):
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)

        # create model
        self.commands: list[tuple[str, str, str, str]] = []
        self.comm = comm

    async def init(self) -> None:
        self.commands = []
        command_names = []
        for client_name in self.comm.clients:
            # loop interfaces
            for interface in await self.comm.get_interfaces(client_name):
                # loop methods
                for method_name, member in inspect.getmembers(interface):
                    # not a method?
                    if not inspect.isfunction(member):
                        continue

                    # get name
                    name = "%s.%s" % (client_name, method_name)

                    # exists?
                    if name in command_names:
                        continue
                    command_names.append(name)

                    # get signature
                    params = []
                    for param_name, param in inspect.signature(member).parameters.items():
                        if param_name not in ["self", "args", "kwargs"]:
                            # parameter name itself
                            arg = param_name

                            # go a type?
                            if param.annotation != inspect.Parameter.empty and hasattr(param.annotation, "__name__"):
                                arg += ": " + param.annotation.__name__

                            # default value?
                            if param.default != inspect.Parameter.empty:
                                arg += " = " + str(param.default)

                            params.append(arg)

                    # get first line of documentation
                    doc = str(member.__doc__)
                    short_doc = doc.split("\n")[0]

                    # append to list
                    self.commands.append((name, "(" + ", ".join(params) + ")", short_doc, doc))

        # sort
        self.commands.sort(key=lambda m: m[0])

    def doc(self, command: str) -> str | None:
        for c in self.commands:
            if c[0] == command:
                return c[3]
        return None

    def rowCount(self, parent: Any | None = None, *args: Any, **kwargs: Any) -> int:
        return len(self.commands)

    def columnCount(self, parent: Any | None = None, *args: Any, **kwargs: Any) -> int:
        return 3

    def data(self, index: QtCore.QModelIndex, role: Any = None) -> str:
        if role == QtCore.Qt.ItemDataRole.DisplayRole:
            return str(self.commands[index.row()][index.column()])
        return ""


class ShellWidget(BaseWidget, Ui_ShellWidget):
    add_command_log = QtCore.Signal(str)

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore
        self.command_number = 0

        # commands
        self.command_model: CommandModel | None = None
        self.completer: QtWidgets.QCompleter | None = None
        self.command_regexp = re.compile(r"(\w+)\.(\w+[_\w+]*)\(([^\)]*)\)")
        self.args_regexp = re.compile(r'(?:[^\s,"]|"(?:\\.|[^"])*")+')

        # signals/slots
        self.add_command_log.connect(self.textCommandLog.append)
        self.textCommandInput.commandExecuted.connect(self.execute_command)
        self.textCommandInput.textChanged.connect(self._update_docs)

    async def open(
        self,
        modules: list[Proxy] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        # commands
        self.command_model = CommandModel(self.comm)

        # create completer
        self.completer = QtWidgets.QCompleter(self)
        self.completer.setCompletionMode(QtWidgets.QCompleter.CompletionMode.PopupCompletion)
        self.completer.setCompletionRole(QtCore.Qt.ItemDataRole.DisplayRole)
        self.completer.setCompletionColumn(0)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseSensitivity.CaseInsensitive)
        self.completer.setModel(self.command_model)
        self.textCommandInput.setCompleter(self.completer)

        # create widget for popup
        table_view = QtWidgets.QTableView(self)
        self.completer.setPopup(table_view)
        table_view.verticalHeader().hide()
        table_view.setShowGrid(False)
        table_view.setMinimumHeight(50)
        table_view.horizontalHeader().hide()
        table_view.horizontalHeader().setStretchLastSection(False)
        table_view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table_view.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        table_view.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeMode.Stretch)
        table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
        table_view.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)

        # await self.command_model.init()
        await self.update_client_list()

        if self.comm is not None:
            await self.comm.register_event(ModuleOpenedEvent, self._module_changed)
            await self.comm.register_event(ModuleClosedEvent, self._module_changed)

    def _add_command_log(self, msg: str, color: str | None = None) -> None:
        if color is not None:
            msg = '<span style="color:%s;">%s</span>' % (color, msg)
        self.add_command_log.emit(msg)

    def execute_command(self, command: str) -> None:
        asyncio.create_task(self._execute_command(command))

    async def _execute_command(self, command: str) -> None:
        try:
            cmd = ShellCommand.parse(command)
            self._add_command_log(str(cmd))
        except Exception as e:
            self._add_command_log(f"$ {command}")
            self._add_command_log(f"{str(e)}", "red")
            return

        # execute command
        response = await cmd.execute(self.comm)

        # log response
        self._add_command_log(str(response), response.color)

    def _update_docs(self) -> None:
        return

        # get current input
        cmd = str(self.textCommandInput.text())
        if "(" in cmd:
            cmd = cmd[: cmd.index("(")]

        # get documentation
        doc = self.command_model.doc(cmd)
        if not doc:
            doc = ""

    async def _module_changed(self, event: Event, sender: str) -> bool:
        asyncio.create_task(self.update_client_list())
        return True

    async def update_client_list(self) -> None:
        # create model for commands
        if self.command_model is not None and self.completer is not None:
            await self.command_model.init()
            self.completer.setModel(self.command_model)
