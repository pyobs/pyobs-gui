import asyncio
import os
from typing import Optional, List, Any
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSignal
from astropy.time import Time
from colour import Color

from pyobs.events import LogEvent, ModuleOpenedEvent, ModuleClosedEvent, Event
from pyobs.interfaces import ICamera, ITelescope, IRoof, IFocuser, IWeather, IVideo, IAutonomous, ISpectrograph
from .widgetcamera import WidgetCamera
from .widgetsmixin import WidgetsMixin
from .widgettelescope import WidgetTelescope
from .widgetfocus import WidgetFocus
from .widgetweather import WidgetWeather
from .widgetvideo import WidgetVideo
from .qt.mainwindow import Ui_MainWindow
from .logmodel import LogModel, LogModelProxy
from .widgetevents import WidgetEvents
from .widgetroof import WidgetRoof
from .widgetshell import WidgetShell
from .widgetspectrograph import WidgetSpectrograph


DEFAULT_WIDGETS = {
    ICamera: WidgetCamera,
    ITelescope: WidgetTelescope,
    IRoof: WidgetRoof,
    IFocuser: WidgetFocus,
    IWeather: WidgetWeather,
    IVideo: WidgetVideo,
    ISpectrograph: WidgetSpectrograph
}

DEFAULT_ICONS = {
    ICamera: ":/resources/Crystal_Clear_device_camera.png",
    ITelescope: ":/resources/Crystal_Clear_action_find.png",
    IRoof: ":/resources/Crystal_Clear_app_kfm_home.png",
    IFocuser: ":/resources/Crystal_Clear_app_demo.png",
    IWeather: ":/resources/Crystal_Clear_app_demo.png",
    IVideo: ":/resources/Crystal_Clear_device_camera.png",
    ISpectrograph: ":/resources/Crystal_Clear_device_camera.png"
}


class PagesListWidgetItem(QtWidgets.QListWidgetItem):
    """ListWidgetItem for the pages list. Always sorts Shell and Events first"""
    def __lt__(self, other: QtWidgets.QListWidgetItem) -> bool:
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


class MainWindow(QtWidgets.QMainWindow, WidgetsMixin, Ui_MainWindow):
    add_log = pyqtSignal(list)
    add_command_log = pyqtSignal(str)

    def __init__(self, comm, vfs, observer, show_shell: bool = True, show_events: bool = True,
                 show_modules: Optional[List[str]] = None, widgets: Optional[List] = None,
                 sidebar: Optional[List] = None, **kwargs: Any):
        """Init window.

        Args:
            comm: Comm to use.
            vfs: VFS to use.
            observer: Observer to use.
            show_shell: Whether to show shell page.
            show_events: Whether to show events page.
            show_modules: If not empty, show only listed modules.
            widgets: List of custom widgets.
            sidebar: List of custom widgets for the sidebar.
        """
        QtWidgets.QMainWindow.__init__(self)
        WidgetsMixin.__init__(self)
        self.setupUi(self)
        self.resize(1300, 800)

        # store stuff
        self.comm = comm
        self.vfs = vfs
        self.observer = observer
        self.mastermind_running = False
        self.show_modules = show_modules
        self.custom_widgets = [] if widgets is None else widgets
        self.custom_sidebar_widgets = [] if sidebar is None else sidebar
        self.show_shell = show_shell
        self.show_events = show_events

        # splitters
        self.splitterClients.setSizes([self.width() - 200, 200])
        self.splitterLog.setSizes([self.height() - 100, 100])

        # logs
        self.log_model = LogModel()
        self.add_log.connect(self.log_model.add_entry)
        self.log_proxy = LogModelProxy()
        self.log_proxy.setSourceModel(self.log_model)
        self.tableLog.setModel(self.log_proxy)
        self.log_model.rowsInserted.connect(self.log_entry_added)
        self.log_model.rowsInserted.connect(self._resize_log_table)
        self.listClients.itemChanged.connect(self._log_client_changed)

        # mastermind
        self.labelAutonomousWarning.setVisible(False)
        self.labelWeatherWarning.setVisible(False)

        # list of widgets
        self._widgets = {}
        self._current_widget = None

    async def open(self):
        """Open module."""

        # open widgets
        await WidgetsMixin.open(self)

        # shell
        if self.show_shell:
            # add shell nav button and view
            self.shell = self.create_widget(WidgetShell)
            await self._add_client('Shell', QtGui.QIcon(":/resources/Crystal_Clear_app_terminal.png"), self.shell)
        else:
            self.shell = None

        # events
        if self.show_events:
            # add events nav button and view
            self.events = WidgetEvents(self.comm)
            await self._add_client('Events', QtGui.QIcon(":/resources/Crystal_Clear_app_terminal.png"), self.events)
        else:
            self.events = None

        # change page
        self.listPages.currentRowChanged.connect(self._change_page)

        # get clients
        self._update_client_list()
        await self._check_warnings()

        # subscribe to events
        await self.comm.register_event(LogEvent, self.process_log_entry)
        await self.comm.register_event(ModuleOpenedEvent, lambda x, y: self._client_connected(y))
        await self.comm.register_event(ModuleClosedEvent, lambda x, y: self._client_disconnected(y))

        # create other nav buttons and views
        for client_name in self.comm.clients:
            await self._client_connected(client_name)

        # add timer for checking warnings
        self._warning_timer = QtCore.QTimer()
        self._warning_timer.timeout.connect(lambda: asyncio.create_task(self._check_warnings()))
        self._warning_timer.start(5000)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        """Called when window is about to be closed."""

        # get current widget
        widget = self.stackedWidget.currentWidget()

    async def _add_client(self, client: str, icon: QtGui.QIcon, widget: QtWidgets.QWidget) -> None:
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

        # open and add widget
        await widget.open()
        self.stackedWidget.addWidget(widget)

        # store
        self._widgets[client] = widget

    def _change_page(self, idx: int) -> None:
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

    def _update_client_list(self) -> None:
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

    async def process_log_entry(self, entry: Event, sender: str) -> bool:
        """Process a new log entry.

        Args:
            entry: The log event.
            sender: Name of sender.
        """
        if not isinstance(entry, LogEvent):
            return False

        # date
        time = Time(entry.time, format='unix')

        # define new row and emit
        row = [time.iso.split()[1],
               str(sender),
               entry.level,
               '%s:%d' % (os.path.basename(entry.filename), entry.line),
               entry.message]
        self.add_log.emit(row)
        return True

    def _resize_log_table(self) -> None:
        """Resize log table to entries."""

        # resize columns
        self.tableLog.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeToContents)
        self.tableLog.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

        # this is a one-time shot, so unconnect signal
        self.log_model.rowsInserted.disconnect(self._resize_log_table)

    def _log_client_changed(self, item: QtWidgets.QListWidgetItem) -> None:
        """Update log filter."""

        # update proxy
        self.log_proxy.filter_source(str(item.text()), item.checkState() == QtCore.Qt.Checked)

    async def _check_warnings(self) -> None:
        """Checks, whether we got an autonomous module."""
        # get all autonomous modules
        autonomous_clients = await self.comm.clients_with_interface(IAutonomous)

        # got any?
        self.mastermind_running = len(autonomous_clients) > 0
        self.labelAutonomousWarning.setVisible(self.mastermind_running)

        # get weather modules
        weather_clients = await self.comm.clients_with_interface(IWeather)
        if len(weather_clients) > 0:
            # found one or more, just take the first one
            weather = await self.comm.proxy(weather_clients[0])
            self.labelWeatherWarning.setVisible(not await weather.is_running())
        else:
            # if there is no weather module, don't show warning
            self.labelWeatherWarning.setVisible(False)

    async def _client_connected(self, client: str) -> None:
        """Called when a new client connects.

        Args:
            client: Name of client.
        """

        # ignore it?
        if self.show_modules is not None and client not in self.show_modules:
            return

        # does client exist already?
        if client in self._widgets:
            return

        # update client list
        self._update_client_list()

        # get proxy
        proxy = await self.comm.proxy(client)

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

        # custom sidebar?
        for csw in self.custom_sidebar_widgets:
            if csw['module'] == client:
                widget.add_to_sidebar(self.create_widget(csw['widget'], module=proxy))

        # add it
        await self._add_client(client, icon, widget)

        # check mastermind
        await self._check_warnings()

    async def _client_disconnected(self, client: str) -> None:
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

        # remove from dict
        del self._widgets[client]

        # check mastermind
        await self._check_warnings()

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

    def log_entry_added(self):
        """Triggered, whenever a new log item has been added."""
        sb = self.tableLog.verticalScrollBar()
        if sb.maximum() == sb.value():
            self.tableLog.scrollToBottom()
