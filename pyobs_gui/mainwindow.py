from threading import Event
import os
from typing import Union
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from astropy.time import Time
from colour import Color

from pyobs.events import LogEvent, ModuleOpenedEvent, ModuleClosedEvent
from pyobs.interfaces.proxies import ICameraProxy, ITelescopeProxy, IRoofProxy, IFocuserProxy, IWeatherProxy, \
    IVideoProxy, IAutonomousProxy
from pyobs.object import create_object
from .basewidget import BaseWidget
from .widgetcamera import WidgetCamera
from .widgettelescope import WidgetTelescope
from .widgetfocus import WidgetFocus
from .widgetweather import WidgetWeather
from .widgetvideo import WidgetVideo
from .qt.mainwindow import Ui_MainWindow
from .logmodel import LogModel, LogModelProxy
from .widgetevents import WidgetEvents
from .widgetroof import WidgetRoof
from .widgetshell import WidgetShell


DEFAULT_WIDGETS = {
    ICameraProxy: WidgetCamera,
    ITelescopeProxy: WidgetTelescope,
    IRoofProxy: WidgetRoof,
    IFocuserProxy: WidgetFocus,
    IWeatherProxy: WidgetWeather,
    IVideoProxy: WidgetVideo
}

DEFAULT_ICONS = {
    ICameraProxy: ":/resources/Crystal_Clear_device_camera.png",
    ITelescopeProxy: ":/resources/Crystal_Clear_action_find.png",
    IRoofProxy: ":/resources/Crystal_Clear_app_kfm_home.png",
    IFocuserProxy: ":/resources/Crystal_Clear_app_demo.png",
    IWeatherProxy: ":/resources/Crystal_Clear_app_demo.png",
    IVideoProxy: ":/resources/Crystal_Clear_device_camera.png"
}


class PagesListWidgetItem(QtWidgets.QListWidgetItem):
    """ListWidgetItem for the pages list. Always sorts Shell and Events first"""
    def __lt__(self, other):
        """Compare two items."""

        # special cases?
        if self.text() == 'Shell':
            # if self is 'Shell', it always goes first
            return True
        elif other.text() == 'Shell':
            # if other is 'Shell', it always goes later
            return False
        elif self.text() == 'Events':
            # if self is 'Events', it only goes first if other is not 'Shell'
            return other.text() != 'Shell'
        elif other.text() == 'Events':
            # if other is 'Events', self always goes later, since case of 'Shell' as self has always been dealt with
            return False
        else:
            # default case
            return QtWidgets.QListWidgetItem.__lt__(self, other)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    add_log = pyqtSignal(list)
    add_command_log = pyqtSignal(str)
    client_connected = pyqtSignal(str)
    client_disconnected = pyqtSignal(str)

    def __init__(self, comm, vfs, observer, show_shell: bool = True, show_events: bool = True,
                 show_modules: list = None, widgets: list = None, **kwargs):
        """Init window.

        Args:
            comm: Comm to use.
            vfs: VFS to use.
            observer: Observer to use.
            show_shell: Whether to show shell page.
            show_events: Whether to show events page.
            show_modules: If not empty, show only listed modules.
            widgets: List of custom widgets.
        """
        QtWidgets.QMainWindow.__init__(self)
        self.setupUi(self)
        self.resize(1300, 800)

        # store stuff
        self.comm = comm
        self.vfs = vfs
        self.observer = observer
        self.mastermind_running = False
        self.show_modules = show_modules
        self.custom_widgets = [] if widgets is None else widgets

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

        # mastermind
        self.labelAutonomousWarning.setVisible(False)

        # list of widgets
        self._widgets = {}
        self._current_widget = None

        # shell
        if show_shell:
            # add shell nav button and view
            self.shell = self.create_widget(WidgetShell)
            self._add_client('Shell', QtGui.QIcon(":/resources/Crystal_Clear_app_terminal.png"), self.shell)
        else:
            self.shell = None

        # events
        if show_events:
            # add events nav button and view
            self.events = WidgetEvents(self.comm)
            self._add_client('Events', QtGui.QIcon(":/resources/Crystal_Clear_app_terminal.png"), self.events)
        else:
            self.events = None

        # create other nav buttons and views
        for client_name in self.comm.clients:
            self._client_connected(client_name)

        # change page
        self.listPages.currentRowChanged.connect(self._change_page)

        # get clients
        self._update_client_list()
        self._check_autonomous()

        # subscribe to events
        self.comm.register_event(LogEvent, self.process_log_entry)
        self.comm.register_event(ModuleOpenedEvent, lambda x, y: self.client_connected.emit(y))
        self.comm.register_event(ModuleClosedEvent, lambda x, y: self.client_disconnected.emit(y))

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
            label: Label for icon.

        Returns:

        """

        # add list item
        item = PagesListWidgetItem()
        item.setIcon(icon)
        item.setText(client)

        # add to list and sort
        self.listPages.addItem(item)
        self.listPages.sortItems()

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
            # create item
            item = QtWidgets.QListWidgetItem(client_name)
            item.setCheckState(QtCore.Qt.Checked)
            item.setForeground(QtGui.QColor(Color(pick_for=client_name).hex))
            self.listClients.addItem(item)

        # update shell
        if self.shell is not None:
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

    def _check_autonomous(self):
        """Checks, whether we got an autonomous module."""

        # get all autonomous modules
        clients = list(self.comm.clients_with_interface(IAutonomousProxy))

        # got any?
        self.mastermind_running = len(clients) > 0
        self.labelAutonomousWarning.setVisible(self.mastermind_running)

    def create_widget(self, config: Union[dict, type], **kwargs) -> BaseWidget:
        """Creates new widget.

        Args:
            config: Config to create widget from.

        Returns:
            New widget.
        """
        if isinstance(config, dict):
            return create_object(config, vfs=self.vfs, comm=self.comm, observer=self.observer, **kwargs)
        elif isinstance(config, type):
            return config(vfs=self.vfs, comm=self.comm, observer=self.observer, **kwargs)
        else:
            raise ValueError('Wrong type.')

    def _client_connected(self, client: str):
        """Called when a new client connects.

        Args:
            client: Name of client.
        """

        # ignore it?
        if self.show_modules is not None and client not in self.show_modules:
            return

        # update client list
        self._update_client_list()

        # get proxy
        proxy = self.comm[client]

        # check mastermind
        self._check_autonomous()

        # what do we have?
        widget, icon = None, None
        for interface, klass in DEFAULT_WIDGETS.items():
            if isinstance(proxy, interface):
                widget = self.create_widget(klass, module=proxy)
                icon = QtGui.QIcon(DEFAULT_ICONS[interface])
                break

        # look at custom widgets
        for cw in self.custom_widgets:
            if cw['module'] == client:
                widget = self.create_widget(cw['widget'], module=proxy)
                icon = QtGui.QIcon(list(DEFAULT_ICONS.values())[0])

        # still nothing?
        if widget is None:
            return

        # add it
        self._add_client(client, icon, widget)

    def _client_disconnected(self, client: str):
        """Called, when a client disconnects.

        Args:
            client: Name of client.
        """

        # check mastermind
        self._check_autonomous()

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
