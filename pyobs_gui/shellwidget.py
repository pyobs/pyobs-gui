import asyncio
import pprint
import traceback
from io import BytesIO
import re
from typing import Any, Optional, List, Tuple, Union, Dict
from PyQt5 import QtWidgets, QtCore
import inspect
import tokenize
from enum import Enum
import logging

from astroplan import Observer

from pyobs.comm import Comm, Proxy
from pyobs.events import ModuleOpenedEvent, Event, ModuleClosedEvent
from pyobs.utils import exceptions as exc
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


class CommandModel(QtCore.QAbstractTableModel):
    def __init__(self, comm: Comm, *args: Any, **kwargs: Any):
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)

        # create model
        self.commands: List[Tuple[str, str, str, str]] = []
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

    def doc(self, command: str) -> Optional[str]:
        for c in self.commands:
            if c[0] == command:
                return c[3]
        return None

    def rowCount(self, parent: Optional[Any] = None, *args: Any, **kwargs: Any) -> int:
        return len(self.commands)

    def columnCount(self, parent: Optional[Any] = None, *args: Any, **kwargs: Any) -> int:
        return 3

    def data(self, index: QtCore.QModelIndex, role: Any = None) -> str:
        if role == QtCore.Qt.DisplayRole:
            return self.commands[index.row()][index.column()]
        return QtCore.QVariant()


class ShellWidget(QtWidgets.QWidget, BaseWidget, Ui_ShellWidget):
    add_command_log = QtCore.pyqtSignal(str)

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)
        self.command_number = 0

        # commands
        self.command_model = None
        self.completer = None
        self.command_regexp = re.compile(r"(\w+)\.(\w+[_\w+]*)\(([^\)]*)\)")
        self.args_regexp = re.compile(r'(?:[^\s,"]|"(?:\\.|[^"])*")+')

        # signals/slots
        self.add_command_log.connect(self.textCommandLog.append)
        self.textCommandInput.commandExecuted.connect(self.execute_command)
        self.textCommandInput.textChanged.connect(self._update_docs)

    async def open(
        self,
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        # commands
        self.command_model = CommandModel(self.comm)

        # create completer
        self.completer = QtWidgets.QCompleter(self)
        self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.completer.setCompletionRole(QtCore.Qt.DisplayRole)
        self.completer.setCompletionColumn(0)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
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
        table_view.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        table_view.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        table_view.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        table_view.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        table_view.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

        # await self.command_model.init()
        await self.update_client_list()

        if self.comm is not None:
            await self.comm.register_event(ModuleOpenedEvent, self._module_changed)
            await self.comm.register_event(ModuleClosedEvent, self._module_changed)

    def _add_command_log(self, msg: str, color: Optional[str] = None) -> None:
        if color is not None:
            msg = '<span style="color:%s;">%s</span>' % (color, msg)
        self.add_command_log.emit(msg)

    def _parse_command(self, cmd: str) -> Tuple[str, str, List[Any]]:
        # tokenize command
        tokens = tokenize.tokenize(BytesIO(cmd.encode("utf-8")).readline)

        # init values
        module: Optional[str] = None
        command: Optional[str] = None
        params: List[Any] = []
        sign = 1

        # we start here
        state = ParserState.START

        # loop tokens
        for t in tokens:
            if state == ParserState.START:
                # first token is always ENCODING
                if t.type != tokenize.ENCODING:
                    raise ValueError("Invalid command.")
                state = ParserState.MODULE

            elif state == ParserState.MODULE:
                # 2nd token is always a NAME with the command
                if t.type != tokenize.NAME:
                    raise ValueError("Invalid command.")
                module = t.string
                state = ParserState.MODSEP

            elif state == ParserState.MODSEP:
                # 3rd token is always a point
                if t.type != tokenize.OP or t.string != ".":
                    raise ValueError("Invalid command.")
                state = ParserState.COMMAND

            elif state == ParserState.COMMAND:
                # 4th token is always a NAME with the command
                if t.type != tokenize.NAME:
                    raise ValueError("Invalid command.")
                command = t.string
                state = ParserState.OPEN

            elif state == ParserState.OPEN:
                # 5th token is always an OP with an opening bracket
                if t.type != tokenize.OP or t.string != "(":
                    raise ValueError("Invalid parameters.")
                state = ParserState.PARAM

            elif state == ParserState.PARAM:
                # if params list is empty, we accept an OP with a closing bracket, otherwise it must be
                # a NUMBER or STRING
                if len(params) == 0 and t.type == tokenize.OP and t.string == ")":
                    state = ParserState.CLOSE
                elif t.type == tokenize.OP and t.string == "-":
                    sign = -1
                elif t.type == tokenize.NUMBER or t.type == tokenize.STRING:
                    if t.type == tokenize.STRING:
                        if t.string[0] == t.string[-1] and t.string[0] in ['"', '"']:
                            params.append(t.string[1:-1])
                        else:
                            params.append(t.string)
                    else:
                        params.append(sign * float(t.string))
                    sign = 1
                    state = ParserState.PARAMSEP
                else:
                    raise ValueError("Invalid parameters.")

            elif state == ParserState.PARAMSEP:
                # following a PARAM, there must be an OP, either a comma, or a closing bracket
                if t.type != tokenize.OP:
                    raise ValueError("Invalid parameters.")
                if t.string == ",":
                    state = ParserState.PARAM
                elif t.string == ")":
                    state = ParserState.CLOSE
                else:
                    raise ValueError("Invalid parameters.")

            elif state == ParserState.CLOSE:
                # must be a closing bracket
                if t.type not in [tokenize.NEWLINE, tokenize.ENDMARKER]:
                    raise ValueError("Expecting end of command after closing bracket.")

                # return results
                if module is None or command is None:
                    raise ValueError("Found end of command without module and/or command.")
                return module, command, params

        # if we came here, something went wrong
        raise ValueError("Invalid parameters.")

    def execute_command(self, command: str) -> None:
        asyncio.create_task(self._execute_command(command))

    async def _execute_command(self, command: str) -> None:
        # log command
        self.command_number += 1
        self._add_command_log("$ (#%d) %s" % (self.command_number, command))

        # parse command
        try:
            client, command, params = self._parse_command(command)
        except Exception as e:
            self._add_command_log("(#%d): %s" % (self.command_number, str(e)), "red")
            return

        # get proxy
        try:
            proxy = await self.comm.proxy(client)
        except ValueError:
            self._add_command_log(f"(#{self.command_number}): Could not find module: {str(client)}", "red")
            return

        # execute command
        try:
            response = await proxy.execute(command, *params)
        except ValueError as e:
            log.exception(f"(#{self.command_number}): Something has gone wrong.")
            self._add_command_log(f"(#{self.command_number}): Invalid parameter: {str(e)}", "red")
            return
        except exc.RemoteError as e:
            self._add_command_log(f"(#{self.command_number}) Exception raised: {str(e)}", "red")
            return

        # log response
        msg = "OK" if response is None else pprint.pformat(response)
        self._add_command_log("(#%d) %s" % (self.command_number, msg), "lime")

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
        await self.command_model.init()
        self.completer.setModel(self.command_model)
