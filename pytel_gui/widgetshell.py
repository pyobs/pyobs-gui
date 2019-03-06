import pprint
from threading import Thread
import re
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal
import inspect

from pytel.comm import RemoteException
from .qt.widgetshell import Ui_WidgetShell


class CommandModel(QtCore.QAbstractTableModel):
    def __init__(self, comm, *args, **kwargs):
        QtCore.QAbstractTableModel.__init__(self, *args, **kwargs)

        # create model
        self.commands = []
        for client_name in comm.clients:
            # get proxy
            proxy = comm[client_name]

            # loop commands
            for method in proxy.method_names:
                # get name
                name = '%s.%s' % (client_name, method)

                # get signature
                params = []
                for param_name, param in proxy.signature(method).parameters.items():
                    if param_name not in ['self', 'args', 'kwargs']:
                        # parameter name itself
                        arg = param_name

                        # go a type?
                        if param.annotation != inspect.Parameter.empty:
                            arg += ': ' + param.annotation.__name__

                        # default value?
                        if param.default != inspect.Parameter.empty:
                            arg += ' = ' + str(param.default)

                        params.append(arg)

                # get first line of documentation
                doc = proxy.interface_method(method).__doc__
                short_doc = doc.split('\n')[0]

                # append to list
                self.commands.append((name, '(' + ', '.join(params) + ')', short_doc, doc))

        # sort
        self.commands.sort(key=lambda m: m[0])

    def doc(self, command):
        for c in self.commands:
            if c[0] == command:
                return c[3]
        return None

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.commands)

    def columnCount(self, parent=None, *args, **kwargs):
        return 3

    def data(self, index: QtCore.QModelIndex, role=None):
        if role == QtCore.Qt.DisplayRole:
            return self.commands[index.row()][index.column()]


class WidgetShell(QtWidgets.QWidget, Ui_WidgetShell):
    add_command_log = pyqtSignal(str)
    show_help = pyqtSignal(str)

    def __init__(self, comm, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.comm = comm

        # commands
        self.command_model = None
        self.command_regexp = re.compile(r'(\w+)\.(\w+[_\w+]*)\(([^\)]*)\)')
        self.args_regexp = re.compile(r'(?:[^\s,"]|"(?:\\.|[^"])*")+')

        # create completer
        self.completer = QtWidgets.QCompleter(self)
        self.completer.setCompletionMode(QtWidgets.QCompleter.PopupCompletion)
        self.completer.setCompletionRole(QtCore.Qt.DisplayRole)
        self.completer.setCompletionColumn(0)
        self.completer.setCaseSensitivity(QtCore.Qt.CaseInsensitive)
        self.textCommandInput.setCompleter(self.completer)
        self.update_client_list()

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

        # signals/slots
        self.add_command_log.connect(self.textCommandLog.append)
        self.textCommandInput.commandExecuted.connect(self.execute_command)
        self.textCommandInput.textChanged.connect(self._update_docs)

    def _add_command_log(self, msg, color=None):
        if color is not None:
            msg = '<span style="color:%s;">%s</span>' % (color, msg)
        self.add_command_log.emit(msg)

    def execute_command(self, command):
        self._add_command_log('$ ' + command, 'blue')

        # parse command
        m1 = self.command_regexp.match(command)
        if not m1:
            self._add_command_log('Invalid syntax', 'red')
            return
        module = m1.group(1)
        command = m1.group(2)

        # get module
        mod = self.comm[module]

        # split arguments, if any
        args = [a for a in self.args_regexp.findall(m1.group(3))]

        # remove quotes
        args = [a[1:-1] if a[0] == a[-1] and a[0] in ['"', "'"] else a for a in args]

        # execute command in new thread
        thread = Thread(target=self._execute_command_async, args=(mod, command, *args),
                        name=module + '.' + command)
        thread.start()

    def _execute_command_async(self, mod, command, *args):
        # execute command
        try:
            response = mod.execute_safely(command, *args)
        except ValueError as e:
            self._add_command_log('Invalid parameter: %s' % str(e), 'red')
            return
        except RemoteException as e:
            if e:
                self._add_command_log('Remote error: %s' % str(e), 'red')
            else:
                self._add_command_log('Unknown Remote error', 'red')
            return

        # log response
        self._add_command_log(pprint.pformat(response))

    def _update_docs(self):
        # get current input
        cmd = str(self.textCommandInput.text())
        if '(' in cmd:
            cmd = cmd[:cmd.index('(')]

        # get documentation
        doc = self.command_model.doc(cmd)
        if not doc:
            doc = ''

        # emit doc
        self.show_help.emit(doc)

    def update_client_list(self):
        # create model for commands
        self.command_model = CommandModel(self.comm)
        self.completer.setModel(self.command_model)
