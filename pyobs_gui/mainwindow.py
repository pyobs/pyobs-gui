from threading import Event
import os
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from astropy.time import Time
from colour import Color

from pyobs.events import LogEvent
from pyobs.events.clientconnected import ClientConnectedEvent
from pyobs.events.clientdisconnected import ClientDisconnectedEvent
from pyobs.interfaces import ICamera, ITelescope, IRoof, IFocuser, IScriptRunner, IWeather
from pyobs_gui.qt.mainwindow import Ui_MainWindow
from pyobs_gui.logmodel import LogModel, LogModelProxy
from pyobs_gui.widgetcamera import WidgetCamera
from pyobs_gui.widgetevents import WidgetEvents
from pyobs_gui.widgetroof import WidgetRoof
from pyobs_gui.widgetshell import WidgetShell
from pyobs_gui.widgettelescope import WidgetTelescope
from pyobs_gui.widgetfocus import WidgetFocus
from pyobs_gui.widgetscript import WidgetScript
from pyobs_gui.widgetweather import WidgetWeather


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    add_log = pyqtSignal(list)
    add_command_log = pyqtSignal(str)
    client_connected = pyqtSignal(str)
    client_disconnected = pyqtSignal(str)

    def __init__(self, comm, vfs, observer, log_latency=2, **kwargs):
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1300, 800)

        # store comm client
        self.comm = comm
        self.vfs = vfs
        self.observer = observer

        # closing
        self.closing = Event()

        # splitters
        self.splitterClients.setSizes([self.width() - 200, 200])
        self.splitterLog.setSizes([self.height() - 100, 100])

        # logs
        self.log_model = LogModel()
        self.add_log.connect(self.log_model.add_entry)
        self.log_proxy = LogModelProxy()
        self.log_proxy.setSourceModel(self.log_model)
        self.tableLog.setModel(self.log_proxy)
        self.log_model.rowsInserted.connect(lambda: QtCore.QTimer.singleShot(0, self.tableLog.scrollToBottom))
        self.log_model.rowsInserted.connect(self._resize_log_table)
        self.listClients.itemChanged.connect(self._log_client_changed)

        # list of widgets
        self._widgets = {}
        self._current_widget = None

        # add shell nav button and view
        self.shell = WidgetShell(self.comm)
        self._add_client('Shell', QtGui.QIcon(":/resources/Crystal_Clear_app_terminal.png"), self.shell)

        # add events nav button and view
        self.events = WidgetEvents(self.comm)
        self._add_client('Events', QtGui.QIcon(":/resources/Crystal_Clear_app_terminal.png"), self.events)

        # create other nav buttons and views
        for client_name in self.comm.clients:
            self._client_connected(client_name)

        # change page
        self.listPages.currentRowChanged.connect(self._change_page)

        # get clients
        self._update_client_list()

        # subscribe to events
        self.comm.register_event(LogEvent, self.process_log_entry)
        self.comm.register_event(ClientConnectedEvent, lambda x, y: self.client_connected.emit(y))
        self.comm.register_event(ClientDisconnectedEvent, lambda x, y: self.client_disconnected.emit(y))

        # signals
        self.client_connected.connect(self._client_connected)
        self.client_disconnected.connect(self._client_disconnected)

    def closeEvent(self, a0: QtGui.QCloseEvent):
        """Called when window is about to be closed."""

        # get current widget
        widget = self.stackedWidget.currentWidget()

    def _add_client(self, client: str, icon: QtGui.QIcon, widget: QtWidgets.QWidget):
        """

        Args:
            client: Name of client to add.
            icon: Icon for client in nav list.
            widget: Widget to add for client.

        Returns:

        """

        # add list item
        item = QtWidgets.QListWidgetItem()
        item.setIcon(icon)
        item.setText(client)

        # add to list
        self.listPages.addItem(item)

        # add widget
        self.stackedWidget.addWidget(widget)

        # store
        self._widgets[client] = widget

    def _change_page(self, idx: int):
        """Change page.

        Args:
            idx: Index of new page in nav list.
        """

        # get name of new page
        client = self.listPages.item(idx).text()

        # change to new page
        self.stackedWidget.setCurrentWidget(self._widgets[client])

        # get new widget
        self._current_widget = self.stackedWidget.currentWidget()

    def _update_client_list(self, *args):
        """Updates the list of clients for the log."""

        # add all clients to list
        self.listClients.clear()
        for client_name in self.comm.clients:
            item = QtWidgets.QListWidgetItem(client_name)
            item.setCheckState(QtCore.Qt.Checked)
            item.setForeground(QtGui.QColor(Color(pick_for=client_name).hex))
            self.listClients.addItem(item)

        #
        self.shell.update_client_list()

    def process_log_entry(self, entry: LogEvent, sender: str):
        """Process a new log entry.

        Args:
            entry: The log event.
            sender: Name of sender.
        """

        # date
        time = Time(entry.time, format='unix')

        # define new row and emit
        row = [time.iso.split()[1],
               str(sender),
               entry.level,
               '%s:%d' % (os.path.basename(entry.filename), entry.line),
               entry.message]
        self.add_log.emit(row)

    def _resize_log_table(self):
        """Resize log table to entries."""

        # resize columns
        self.tableLog.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        self.tableLog.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

        # this is a one-time shot, so unconnect signal
        self.log_model.rowsInserted.disconnect(self._resize_log_table)

    def _log_client_changed(self, item: QtWidgets.QListWidgetItem):
        """Update log filter."""

        # update proxy
        self.log_proxy.filter_source(str(item.text()), item.checkState() == QtCore.Qt.Checked)

    def _client_connected(self, client: str):
        """Called when a new client connects.

        Args:
            client: Name of client.
        """

        # update client list
        self._update_client_list()

        # get proxy
        proxy = self.comm[client]

        # what do we have?
        if isinstance(proxy, ICamera):
            widget = WidgetCamera(proxy, self.comm, self.vfs)
            icon = QtGui.QIcon(":/resources/Crystal_Clear_device_camera.png")
        elif isinstance(proxy, ITelescope):
            widget = WidgetTelescope(proxy, self.comm, self.observer)
            icon = QtGui.QIcon(":/resources/Crystal_Clear_action_find.png")
        elif isinstance(proxy, IRoof):
            widget = WidgetRoof(proxy, self.comm, self.observer)
            icon = QtGui.QIcon(":/resources/Crystal_Clear_app_kfm_home.png")
        elif isinstance(proxy, IFocuser):
            widget = WidgetFocus(proxy, self.comm)
            icon = QtGui.QIcon(":/resources/Crystal_Clear_app_demo.png")
        elif isinstance(proxy, IWeather):
            widget = WidgetWeather(proxy, self.comm)
            icon = QtGui.QIcon(":/resources/Crystal_Clear_app_demo.png")
        elif isinstance(proxy, IScriptRunner):
            widget = WidgetScript(proxy, self.comm)
            icon = QtGui.QIcon(":/resources/Crystal_Clear_app_demo.png")
        else:
            return

        # add it
        self._add_client(client, icon, widget)

    def _client_disconnected(self, client: str):
        """Called, when a client disconnects.

        Args:
            client: Name of client.
        """

        # update client list
        self._update_client_list()

        # not in list?
        if client not in self._widgets:
            return

        # get widget
        widget = self._widgets[client]

        # is current?
        if self.stackedWidget.currentWidget() == widget:
            self._current_widget = None

        # remove widget
        self.stackedWidget.removeWidget(widget)

        # find item in nav list and remove it
        for row in range(self.listPages.count()):
            if self.listPages.item(row).text() == client:
                self.listPages.takeItem(row)
                break

    def get_fits_headers(self, namespaces: list = None, *args, **kwargs) -> dict:
        """Returns FITS header for the current status of this module.

        Args:
            namespaces: If given, only return FITS headers for the given namespaces.

        Returns:
            Dictionary containing FITS headers.
        """
        hdr = {}
        for widget in self._widgets.values():
            if hasattr(widget, 'get_fits_headers'):
                for k, v in widget.get_fits_headers(namespaces, *args, **kwargs).items():
                    hdr[k] = v
        return hdr
