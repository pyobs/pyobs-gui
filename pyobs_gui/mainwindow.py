import asyncio
import os
from typing import Optional, List, Any, Dict, Tuple, Union
from PyQt5 import QtWidgets, QtCore, QtGui
from astroplan import Observer
from astropy.time import Time
from colour import Color
import qtawesome as qta

from pyobs.comm import Comm, Proxy
from pyobs.events import LogEvent, ModuleOpenedEvent, ModuleClosedEvent, Event
from pyobs.interfaces import (
    ICamera,
    ITelescope,
    IRoof,
    IFocuser,
    IWeather,
    IVideo,
    IAutonomous,
    ISpectrograph,
    IFilters,
)
from pyobs.vfs import VirtualFileSystem
from .base import BaseWindow, BaseWidget
from .camerawidget import CameraWidget
from .filterwidget import FilterWidget
from .statuswidget import StatusWidget
from .telescopewidget import TelescopeWidget
from .focuswidget import FocusWidget
from .weatherwidget import WeatherWidget
from .videowidget import VideoWidget
from .qt.mainwindow import Ui_MainWindow
from .logmodel import LogModel, LogModelProxy
from .eventswidget import EventsWidget
from .roofwidget import RoofWidget
from .shellwidget import ShellWidget
from .spectrographwidget import SpectrographWidget


DEFAULT_WIDGETS = {
    ICamera: CameraWidget,
    ITelescope: TelescopeWidget,
    IRoof: RoofWidget,
    IFocuser: FocusWidget,
    IWeather: WeatherWidget,
    IVideo: VideoWidget,
    ISpectrograph: SpectrographWidget,
    IFilters: FilterWidget,
}

DEFAULT_ICONS = {
    None: "fa5.question-circle",
    ICamera: "fa5s.camera",
    ITelescope: "msc.telescope",
    IRoof: "ph.house",
    IFocuser: "mdi.image-filter-center-focus",
    IWeather: "fa5s.cloud-sun",
    IVideo: "fa5s.video",
    ISpectrograph: "ei.graph",
    IFilters: "ei.graph",
}


DEFAULT_CONFIG = [
    {"widget": ShellWidget, "label": "Shell", "always": True},
    {"widget": EventsWidget, "label": "Events", "always": True},
    {"widget": StatusWidget, "label": "Status", "always": True},
    {"widget": CameraWidget, "interfaces": "ICamera", "icon": "fa5s.camera"},
    {"widget": TelescopeWidget, "interfaces": "ITelescope", "icon": "msc.telescope"},
    {"widget": RoofWidget, "interfaces": "IRoof", "icon": "ph.house"},
    {"widget": FocusWidget, "interfaces": "IFocuser", "icon": "mdi.image-filter-center-focus"},
    {"widget": WeatherWidget, "interfaces": "IWeather", "icon": "fa5s.cloud-sun"},
    {"widget": VideoWidget, "interfaces": "IVideo", "icon": "fa5s.video"},
    {"widget": SpectrographWidget, "interfaces": "ISpectrograph", "icon": "ei.graph"},
    {"widget": FilterWidget, "interfaces": "IFilters", "icon": "mdi.air-filter"},
]


class PagesListWidgetItem(QtWidgets.QListWidgetItem):
    """ListWidgetItem for the pages list. Always sorts Shell and Events first"""

    def __lt__(self, other: QtWidgets.QListWidgetItem) -> bool:
        """Compare two items."""

        # special cases
        special = ["Shell", "Events", "Status"]

        # do they apply?
        if self.text() in special and other.text() not in special:
            # self is special, other not
            return True
        elif self.text() not in special and other.text() in special:
            # self not in special, other is
            return False
        elif self.text() in special and other.text() in special:
            # both are
            return special.index(self.text()) < special.index(other.text())
        else:
            # none are
            return QtWidgets.QListWidgetItem.__lt__(self, other)


class MainWindow(QtWidgets.QMainWindow, BaseWindow, Ui_MainWindow):
    add_log = QtCore.pyqtSignal(list)
    add_command_log = QtCore.pyqtSignal(str)

    def __init__(
        self,
        show_shell: bool = True,
        show_events: bool = True,
        show_status: bool = True,
        show_modules: Optional[List[str]] = None,
        widgets: Optional[List[Dict[str, Any]]] = None,
        sidebar: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ):
        """Init window.

        Args:
            show_shell: Whether to show shell page.
            show_events: Whether to show events page.
            show_status: Whether to show status page.
            show_modules: If not empty, show only listed modules.
            widgets: List of custom widgets.
            sidebar: List of custom widgets for the sidebar.
        """
        QtWidgets.QMainWindow.__init__(self)
        BaseWindow.__init__(self, **kwargs)
        self.setupUi(self)
        self.resize(1300, 800)

        # store stuff
        self.mastermind_running = False
        self.show_modules = show_modules
        self.custom_widgets = [] if widgets is None else widgets
        self.custom_sidebar_widgets = [] if sidebar is None else sidebar
        self.show_shell = show_shell
        self.show_events = show_events
        self.show_status = show_status
        self.warning_task: Optional[asyncio.Task] = None

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
        self._widgets: Dict[str, QtWidgets.QWidget] = {}
        self._current_widget = None
        self.shell: Optional[ShellWidget] = None
        self.events: Optional[EventsWidget] = None
        self.status: Optional[StatusWidget] = None

    async def open(self, **kwargs: Any) -> None:
        """Open module."""

        # get module
        module = kwargs.pop("module")

        # open widgets
        await BaseWindow.open(self, modules=[module], **kwargs)

        # shell
        if self.show_shell:
            # add shell nav button and view
            self.shell = self.create_widget(ShellWidget)
            await self._add_client("Shell", qta.icon("msc.terminal-powershell"), self.shell, None)
        else:
            self.shell = None

        # events
        if self.show_events:
            # add events nav button and view
            self.events = self.create_widget(EventsWidget)
            await self._add_client("Events", qta.icon("msc.symbol-event"), self.events, None)
        else:
            self.events = None

        # status
        if self.show_status:
            self.status = self.create_widget(StatusWidget)
            await self._add_client("Status", qta.icon("fa5s.wifi"), self.status, None)
        else:
            self.status = None

        # change page
        self.listPages.currentRowChanged.connect(self._change_page)

        # get clients
        await self._update_client_list()
        await self._check_warnings()

        # subscribe to events
        await self.comm.register_event(LogEvent, self.process_log_entry)
        await self.comm.register_event(ModuleOpenedEvent, self._client_connected)
        await self.comm.register_event(ModuleClosedEvent, self._client_disconnected)

        # create other nav buttons and views
        for client_name in self.comm.clients:
            await self._client_connected(Event(), client_name)

        # add timer for checking warnings
        self.warning_task = asyncio.create_task(self._check_warning_task())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.warning_task is not None:
            self.warning_task.cancel()
        if self.module is not None:
            self.module.quit()

    async def _add_client(
        self, client: str, icon: QtGui.QIcon, widget: BaseWidget, proxy: Optional[Proxy] = None
    ) -> None:
        """

        Args:
            client: Name of client to add.
            icon: Icon for client in nav list.
            widget: Widget to add for client.
            proxy: Proxy for client.

        Returns:

        """

        # add list item
        item = PagesListWidgetItem()
        item.setIcon(icon)
        item.setText(client)
        item.setSizeHint(QtCore.QSize(80, 80))

        # add to list and sort
        self.listPages.addItem(item)
        self.listPages.sortItems()

        # open and add widget
        await widget.open(modules=[proxy], comm=self.comm, observer=self.observer, vfs=self.vfs)
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

    async def _update_client_list(self) -> None:
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
            await self.shell.update_client_list()

    async def process_log_entry(self, entry: Event, sender: str) -> bool:
        """Process a new log entry.

        Args:
            entry: The log event.
            sender: Name of sender.
        """
        if not isinstance(entry, LogEvent):
            return False

        # date
        time = Time(entry.time, format="unix")

        # define new row and emit
        row = [
            time.iso.split()[1],
            str(sender),
            entry.level,
            "%s:%d" % (os.path.basename(entry.filename), entry.line),
            entry.message,
        ]
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

    async def _check_warning_task(self) -> None:
        while True:
            await self._check_warnings()
            await asyncio.sleep(5)

    async def _check_warnings(self) -> None:
        """Checks, whether we got an autonomous module."""
        # get all autonomous modules
        autonomous_clients = await self.comm.clients_with_interface(IAutonomous)
        self.mastermind_running = False
        for auto_client in autonomous_clients:
            proxy = await self.comm.safe_proxy(auto_client, IAutonomous)
            if await proxy.is_running():
                self.mastermind_running = True
                break

        # got any?
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

    async def _client_connected(self, event: Event, client: str) -> bool:
        """Called when a new client connects.

        Args:
            client: Name of client.
        """

        # ignore it?
        if self.show_modules is not None and client not in self.show_modules:
            return False

        # does client exist already?
        if client in self._widgets:
            return False

        # update client list
        await self._update_client_list()

        # get proxy
        proxy = await self.comm.proxy(client)

        # what do we have?
        widget, icon = None, None
        for interface, klass in DEFAULT_WIDGETS.items():
            if isinstance(proxy, interface):
                widget = self.create_widget(klass, module=proxy)
                icon = qta.icon(DEFAULT_ICONS[interface])
                break

        # look at custom widgets
        for cw in self.custom_widgets:
            if cw["module"] == client:
                widget = self.create_widget(cw["widget"], module=proxy)

                # got an icon?
                icon = qta.icon(cw["icon"]) if "icon" in cw else qta.icon(DEFAULT_ICONS[None])

        # still nothing?
        if widget is None:
            return False

        # custom sidebar?
        for csw in self.custom_sidebar_widgets:
            if csw["module"] == client:
                widget.add_to_sidebar(self.create_widget(csw["widget"], module=proxy))

        # add it
        await self._add_client(client, icon, widget, proxy)

        # check mastermind
        await self._check_warnings()
        return True

    async def _client_disconnected(self, event: Event, client: str) -> bool:
        """Called, when a client disconnects.

        Args:
            client: Name of client.
        """

        # update client list
        await self._update_client_list()

        # not in list?
        if client not in self._widgets:
            return False

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
        return True

    def get_fits_headers(self, namespaces: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Tuple[Any, str]]:
        """Returns FITS header for the current status of this module.

        Args:
            namespaces: If given, only return FITS headers for the given namespaces.

        Returns:
            Dictionary containing FITS headers.
        """
        hdr = {}
        for widget in self._widgets.values():
            if hasattr(widget, "get_fits_headers"):
                for k, v in widget.get_fits_headers(namespaces, **kwargs).items():
                    hdr[k] = v
        return hdr

    def log_entry_added(self) -> None:
        """Triggered, whenever a new log item has been added."""
        sb = self.tableLog.verticalScrollBar()
        if sb.maximum() == sb.value():
            self.tableLog.scrollToBottom()
