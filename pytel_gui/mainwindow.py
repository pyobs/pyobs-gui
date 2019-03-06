import inspect
import pprint
from threading import RLock, Event, Thread
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from astropy.time import Time
from colour import Color

from pytel.comm import RemoteException
from pytel.events import LogEvent
from pytel.events.clientconnected import ClientConnectedEvent
from pytel.events.clientdisconnected import ClientDisconnectedEvent
from pytel_gui.qt.mainwindow import Ui_MainWindow
from pytel_gui.logmodel import LogModel, LogModelProxy
from pytel_gui.widgetshell import WidgetShell


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    add_log = pyqtSignal(list)
    add_command_log = pyqtSignal(str)
    client_list_changed = pyqtSignal()

    def __init__(self, comm, log_latency=2, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)

        # store comm client
        self.comm = comm

        # closing
        self.closing = Event()

        # splitters
        self.splitterToolBox.setSizes([self.width() - 400, 400])
        self.splitterLog.setSizes([self.height() - 100, 100])

        # auto exclusive
        self.menuShell.setCheckable(True)
        self.menuShell.setAutoExclusive(True)
        self.menuShell.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))

        # logs
        self.log_model = LogModel()
        self.add_log.connect(self.log_model.add_entry)
        self.log_proxy = LogModelProxy()
        self.log_proxy.setSourceModel(self.log_model)
        self.tableLog.setModel(self.log_proxy)
        self.log_model.rowsInserted.connect(lambda: QtCore.QTimer.singleShot(0, self.tableLog.scrollToBottom))
        self.log_model.rowsInserted.connect(self._resize_log_table)
        self.listClients.itemChanged.connect(self._log_client_changed)

        # log
        self.shell = WidgetShell(self.comm)
        self.shell.show_help.connect(self.show_help)
        self.stackedWidget.addWidget(self.shell)
        self.stackedWidget.setCurrentIndex(1)

        # get clients
        self._update_client_list()

        # subscribe to events
        self.comm.register_event(LogEvent, self.process_log_entry)
        self.comm.register_event(ClientConnectedEvent, lambda x, y: self.client_list_changed.emit())
        self.comm.register_event(ClientDisconnectedEvent, lambda x, y: self.client_list_changed.emit())

        """
        # timer for showing variables
        self.tableVariables.setColumnCount(2)
        self.tableVariables.setHorizontalHeaderLabels(['Key', 'Value'])
        self._variables_timer = QtCore.QTimer()
        self._variables_timer.timeout.connect(self._update_variables)
        self._variables_timer.start(1000)
        """

    @QtCore.pyqtSlot()
    def _update_variables(self):
        self.tableVariables.setRowCount(len(self.comm.variables))
        for i, key in enumerate(self.comm.variables.keys()):
            self.tableVariables.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
            self.tableVariables.setItem(i, 1, QtWidgets.QTableWidgetItem(str(self.comm.variables[key])))

    def _update_client_list(self, *args):
        # add all clients to list
        self.listClients.clear()
        for client_name in self.comm.clients:
            item = QtWidgets.QListWidgetItem(client_name)
            item.setCheckState(QtCore.Qt.Checked)
            item.setForeground(QtGui.QColor(Color(pick_for=client_name).hex))
            self.listClients.addItem(item)

        self.shell.update_client_list()

    def process_log_entry(self, entry: LogEvent, sender: str) -> bool:
        # date
        time = Time(entry.time, format='unix')

        # format sender
        sender = str(sender)
        sender = sender[:sender.index('@')]

        # define new row and emit
        row = [time.iso.split()[1],
               str(sender),
               entry.level,
               '%s:%d' % (os.path.basename(entry.filename), entry.line),
               entry.message]
        self.add_log.emit(row)
        return True

    def _resize_log_table(self):
        # resize columns
        self.tableLog.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        self.tableLog.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)
        # this is a one-time shot, so unconnect signal
        self.log_model.rowsInserted.disconnect(self._resize_log_table)

    def _log_client_changed(self, item: QtWidgets.QListWidgetItem):
        # update proxy
        self.log_proxy.filter_source(str(item.text()), item.checkState() == QtCore.Qt.Checked)

    def show_help(self, text):
        self.textHelp.setText(text)
