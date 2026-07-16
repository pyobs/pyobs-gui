import asyncio
import os
from typing import Optional, List, Any, Dict
from PySide6 import QtWidgets, QtCore, QtGui  # type: ignore
from pyobs.utils.time import Time
from colour import Color  # type: ignore

os.environ["QT_API"] = "pyside6"
import qtawesome as qta  # type: ignore

import pyobs.utils.exceptions as exc
from pyobs.events import LogEvent, ModuleOpenedEvent, ModuleClosedEvent, Event
from pyobs.interfaces import (
    FitsHeaderEntry,
    IAcquisition,
    IAutoFocus,
    IAutoGuiding,
    ICamera,
    ITelescope,
    IRoof,
    IFocuser,
    IWeather,
    IVideo,
    IAutonomous,
    ISpectrograph,
    IFilters,
    IMode,
    IModule,
)

from .base import BaseWindow, BaseWidget
from .acquisitionwidget import AcquisitionWidget
from .autofocuswidget import AutoFocusWidget
from .autoguidingwidget import AutoGuidingWidget
from .camerawidget import CameraWidget
from .filterwidget import FilterWidget
from .modewidget import ModeWidget
from .statuswidget import StatusWidget
from .telescopewidget import TelescopeWidget
from .focuswidget import FocusWidget
from .weatherwidget import WeatherWidget
from .videowidget import VideoWidget
from .qt.mainwindow_ui import Ui_MainWindow
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
    IAutoFocus: AutoFocusWidget,
    IAcquisition: AcquisitionWidget,
    IAutoGuiding: AutoGuidingWidget,
    IWeather: WeatherWidget,
    IVideo: VideoWidget,
    ISpectrograph: SpectrographWidget,
    IFilters: FilterWidget,
    IMode: ModeWidget,
}

DEFAULT_ICONS = {
    None: "fa5.question-circle",
    ICamera: "fa5s.camera",
    ITelescope: "msc.telescope",
    IRoof: "ph.house",
    IFocuser: "mdi.image-filter-center-focus",
    IAutoFocus: "mdi.chart-bell-curve",
    IAcquisition: "mdi.target",
    IAutoGuiding: "mdi.crosshairs-gps",
    IWeather: "fa5s.cloud-sun",
    IVideo: "fa5s.video",
    ISpectrograph: "ei.graph",
    IFilters: "ei.graph",
    IMode: "ei.video",
}


DEFAULT_CONFIG = [
    {"widget": ShellWidget, "label": "Shell", "always": True},
    {"widget": EventsWidget, "label": "Events", "always": True},
    {"widget": StatusWidget, "label": "Status", "always": True},
    {"widget": CameraWidget, "interfaces": "ICamera", "icon": "fa5s.camera"},
    {"widget": TelescopeWidget, "interfaces": "ITelescope", "icon": "msc.telescope"},
    {"widget": RoofWidget, "interfaces": "IRoof", "icon": "ph.house"},
    {"widget": FocusWidget, "interfaces": "IFocuser", "icon": "mdi.image-filter-center-focus"},
    {"widget": AutoFocusWidget, "interfaces": "IAutoFocus", "icon": "mdi.chart-bell-curve"},
    {"widget": AcquisitionWidget, "interfaces": "IAcquisition", "icon": "mdi.target"},
    {"widget": AutoGuidingWidget, "interfaces": "IAutoGuiding", "icon": "mdi.crosshairs-gps"},
    {"widget": WeatherWidget, "interfaces": "IWeather", "icon": "fa5s.cloud-sun"},
    {"widget": VideoWidget, "interfaces": "IVideo", "icon": "fa5s.video"},
    {"widget": SpectrographWidget, "interfaces": "ISpectrograph", "icon": "ei.graph"},
    {"widget": FilterWidget, "interfaces": "IFilters", "icon": "mdi.air-filter"},
]


def _is_float(s: str) -> bool:
    try:
        float(s)
        return True
    except ValueError:
        return False


# fixed order for the "Tools" section and its header; anything else (the "Modules" header and
# all actual modules) sorts after this, with real modules ordered alphabetically among themselves
_PAGE_ORDER = ["Tools", "Shell", "Events", "Status", "Modules"]

# fixed, non-reassignable shortcuts for the always-present Tools pages: Ctrl+1/2/3
_FIXED_SHORTCUTS: Dict[str, str] = {"1": "Shell", "2": "Events", "3": "Status"}

# user-assignable slot keys: Ctrl+N recalls, Ctrl+Alt+N (re)binds to the currently selected page
_ASSIGNABLE_SLOTS: List[str] = ["4", "5", "6", "7", "8", "9", "0"]


class PagesListWidgetItem(QtWidgets.QListWidgetItem):  # type: ignore
    """ListWidgetItem for the pages list. Pins the Tools/Modules headers and Shell/Events/Status in place."""

    def __lt__(self, other: QtWidgets.QListWidgetItem) -> bool:
        """Compare two items."""

        self_rank = _PAGE_ORDER.index(self.text()) if self.text() in _PAGE_ORDER else len(_PAGE_ORDER)
        other_rank = _PAGE_ORDER.index(other.text()) if other.text() in _PAGE_ORDER else len(_PAGE_ORDER)
        if self_rank != other_rank:
            return self_rank < other_rank
        return self.text() < other.text()


class NavPageItemDelegate(QtWidgets.QStyledItemDelegate):  # type: ignore
    """Paints listPages rows normally, then overlays a small colored circular badge (digit
    inside a filled circle, sized to match the row's font) right after the name for any page
    currently bound to a slot. Reads slot_bindings live (not a snapshot), so it always reflects
    the latest bindings without needing to be reconstructed."""

    def __init__(self, slot_bindings: Dict[str, str], parent: Optional[QtCore.QObject] = None):
        super().__init__(parent)
        self._slot_bindings = slot_bindings  # same dict instance MainWindow mutates

    def paint(
        self,
        painter: QtGui.QPainter,
        option: QtWidgets.QStyleOptionViewItem,
        index: QtCore.QModelIndex | QtCore.QPersistentModelIndex,
    ) -> None:
        super().paint(painter, option, index)  # unchanged icon + name + selection rendering

        name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        slot = next((s for s, bound_name in self._slot_bindings.items() if bound_name == name), None)
        if slot is None:
            return

        # position the badge just after the rendered name
        fm = option.fontMetrics
        has_icon = index.data(QtCore.Qt.ItemDataRole.DecorationRole) is not None
        icon_w = option.decorationSize.width() + 4 if has_icon else 0
        text_x = option.rect.left() + icon_w + 4
        text_w = fm.horizontalAdvance(name)

        # circle diameter matches the row's font size
        diameter = fm.height()
        cx = text_x + text_w + 4 + diameter / 2
        cy = option.rect.center().y()

        # on a selected row, the row background itself is painted in the Highlight color, so a
        # Highlight-filled circle there would blend in -- swap the fill/text colors so the badge
        # still stands out against a Highlight-colored row background
        is_selected = bool(option.state & QtWidgets.QStyle.StateFlag.State_Selected)
        fill_role = QtGui.QPalette.ColorRole.HighlightedText if is_selected else QtGui.QPalette.ColorRole.Highlight
        text_role = QtGui.QPalette.ColorRole.Highlight if is_selected else QtGui.QPalette.ColorRole.HighlightedText

        painter.save()
        painter.setRenderHint(QtGui.QPainter.RenderHint.Antialiasing)
        painter.setPen(QtCore.Qt.PenStyle.NoPen)
        painter.setBrush(option.palette.color(fill_role))
        painter.drawEllipse(QtCore.QPointF(cx, cy), diameter / 2, diameter / 2)

        painter.setFont(option.font)
        painter.setPen(option.palette.color(text_role))
        circle_rect = QtCore.QRectF(cx - diameter / 2, cy - diameter / 2, diameter, diameter)
        painter.drawText(circle_rect, QtCore.Qt.AlignmentFlag.AlignCenter, slot)
        painter.restore()


class MainWindow(QtWidgets.QMainWindow, BaseWindow, Ui_MainWindow):  # type: ignore
    add_log = QtCore.Signal(list)
    add_command_log = QtCore.Signal(str)

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
        BaseWindow.__init__(self)
        self.setupUi(self)  # type: ignore
        self.resize(1600, 900)

        # store stuff
        self.mastermind_running = False
        self.show_modules = show_modules
        self.custom_widgets = [] if widgets is None else widgets
        self.custom_sidebar_widgets = [] if sidebar is None else sidebar
        self.show_shell = show_shell
        self.show_events = show_events
        self.show_status = show_status
        self.warning_task: Optional[asyncio.Task[Any]] = None

        # splitters
        self.splitterClients.setSizes([self.width() - 200, 200])
        self.splitterLog.setSizes([self.height() - 100, 100])
        # splitterNav's width is actively reasserted on every resizeEvent instead of being set once
        # here -- see resizeEvent() for why
        self._nav_width = 190
        self.splitterNav.splitterMoved.connect(self._on_nav_splitter_moved)

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
        self._widgets: Dict[str, BaseWidget] = {}
        self._current_widget = None
        self.shell: Optional[ShellWidget] = None
        self.events: Optional[EventsWidget] = None
        self.status: Optional[StatusWidget] = None
        self._modules_header_added = False

        # navbar keyboard shortcuts: slot -> currently bound page name, session-only (see
        # DEV_NavbarShortcuts.md)
        self._slot_bindings: Dict[str, str] = {}
        self.listPages.setItemDelegate(NavPageItemDelegate(self._slot_bindings, self))
        self._setup_shortcuts()

    async def open(self, **kwargs: Any) -> None:  # type: ignore
        """Open module."""

        # get module
        module = kwargs.pop("module")

        # open widgets
        await BaseWindow.open(self, modules=[module], **kwargs)

        # tools header
        if self.show_shell or self.show_events or self.show_status:
            self._add_section_header("Tools")

        # shell
        if self.show_shell:
            # add shell nav button and view
            self.shell = self.create_widget(ShellWidget)
            await self._add_client("Shell", qta.icon("msc.terminal-powershell"), self.shell)
        else:
            self.shell = None

        # events
        if self.show_events:
            # add events nav button and view
            self.events = self.create_widget(EventsWidget)
            await self._add_client("Events", qta.icon("msc.symbol-event"), self.events)
        else:
            self.events = None

        # status
        if self.show_status:
            self.status = self.create_widget(StatusWidget)
            await self._add_client("Status", qta.icon("fa5s.wifi"), self.status)
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

        # add clients
        asyncio.create_task(self._init_clients())

        # add timer for checking warnings
        self.warning_task = asyncio.create_task(self._check_warning_task())

    async def _init_clients(self) -> None:
        # create other nav buttons and views
        for client_name in self.comm.clients:
            await self._client_connected(Event(), client_name)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.warning_task is not None:
            self.warning_task.cancel()
        if self.module is not None:
            # quit() exists on Module but is not declared on Proxy
            self.module.quit()  # pyrefly: ignore [missing-attribute] —

    def _on_nav_splitter_moved(self, pos: int, index: int) -> None:
        """Remember the user's chosen nav width whenever they drag the splitter handle."""
        self._nav_width = self.splitterNav.sizes()[0]

    def resizeEvent(self, event: QtGui.QResizeEvent) -> None:
        super().resizeEvent(event)
        # QSplitter doesn't reliably preserve a fixed pixel width for one pane across window
        # resizes (the window manager sends a few more resizes right after the window is first
        # shown, settling on its final geometry, and each one can silently collapse listPages back
        # to its minimum) -- so just reassert the desired width on every resize instead of trying
        # to set it once and trust Qt to keep it. self._nav_width is only ever changed by the user
        # actually dragging the handle (see _on_nav_splitter_moved).
        self.splitterNav.setSizes([self._nav_width, self.width() - self._nav_width])

    def _add_section_header(self, text: str) -> None:
        """Adds a non-interactive section header (e.g. "Tools", "Modules") to the pages list.

        Args:
            text: Header text. Must be one of the entries in _PAGE_ORDER so it sorts into place.
        """
        item = PagesListWidgetItem()
        item.setText(text)
        item.setFlags(QtCore.Qt.ItemFlag.NoItemFlags)
        font = item.font()
        font.setBold(True)
        font.setPointSize(max(1, font.pointSize() - 1))
        item.setFont(font)
        item.setForeground(QtGui.QColor(QtCore.Qt.GlobalColor.gray))

        self.listPages.addItem(item)
        self.listPages.sortItems()

    async def _add_client(self, client: str, icon: QtGui.QIcon, widget: BaseWidget) -> None:
        """

        Args:
            client: Name of client to add.
            icon: Icon for client in nav list.
            widget: Widget to add for client.
            module: Module name of client.

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
        await widget.open(
            modules=[client] if client is not None else [], comm=self.comm, observer=self.observer, vfs=self.vfs
        )
        self.stackedWidget.addWidget(widget)

        # store
        self._widgets[client] = widget

    @QtCore.Slot(int)  # type: ignore
    def _change_page(self, idx: int) -> None:
        """Change page.

        Args:
            idx: Index of new page in nav list.
        """

        # get name of new page
        item = self.listPages.item(idx)
        client = item.text() if item is not None else None

        # section headers (and an empty selection) aren't real pages
        if client not in self._widgets:
            return

        # change to new page
        self.stackedWidget.setCurrentWidget(self._widgets[client])

        # get new widget
        self._current_widget = self.stackedWidget.currentWidget()

    def _setup_shortcuts(self) -> None:
        """Creates the 17 fixed/assignable navbar shortcuts. Handlers do dynamic lookups against
        self._widgets / self._slot_bindings at press-time, since module pages come and go but the
        shortcut objects themselves live for the app's lifetime. Every shortcut requires Ctrl (or
        Ctrl+Alt) so no text/numeric-entry widget can ever mistake one for ordinary input -- see
        DEV_NavbarShortcuts.md for why that's a structural guarantee rather than one that needs
        per-widget-type verification.
        """
        self._shortcuts: List[QtGui.QShortcut] = []

        for key, name in _FIXED_SHORTCUTS.items():
            sc = QtGui.QShortcut(QtGui.QKeySequence(f"Ctrl+{key}"), self)
            sc.activated.connect(lambda name=name: self._go_to_page(name))
            self._shortcuts.append(sc)

        for slot in _ASSIGNABLE_SLOTS:
            recall = QtGui.QShortcut(QtGui.QKeySequence(f"Ctrl+{slot}"), self)
            recall.activated.connect(lambda slot=slot: self._recall_slot(slot))
            self._shortcuts.append(recall)

            bind = QtGui.QShortcut(QtGui.QKeySequence(f"Ctrl+Alt+{slot}"), self)
            bind.activated.connect(lambda slot=slot: self._bind_slot(slot))
            self._shortcuts.append(bind)

    def _go_to_page(self, name: str) -> None:
        """Fixed Ctrl+1/2/3 handler. No-ops if the page was never created."""
        if name not in self._widgets:
            return
        self._select_page_by_name(name)

    def _select_page_by_name(self, name: str) -> None:
        """Selects the listPages row for `name`; selection change drives the existing
        currentRowChanged -> _change_page path, so this never touches stackedWidget directly."""
        for row in range(self.listPages.count()):
            item = self.listPages.item(row)
            if item is not None and item.text() == name:
                self.listPages.setCurrentRow(row)
                return

    def _bind_slot(self, slot: str) -> None:
        """Ctrl+Alt+N: binds the currently selected page to slot N, silently overwriting any
        previous binding for that slot."""
        item = self.listPages.currentItem()
        if item is None:
            return
        name = item.text()
        if name not in self._widgets:  # defensive; headers are NoItemFlags and unselectable anyway
            return
        self._slot_bindings[slot] = name
        self.listPages.viewport().update()
        self.statusBar().showMessage(f"Bound Ctrl+{slot} to '{name}'", 3000)

    def _recall_slot(self, slot: str) -> None:
        """Ctrl+N: switches to whatever is bound to slot N. No-ops if unbound or disconnected."""
        name = self._slot_bindings.get(slot)
        if name is None or name not in self._widgets:
            return
        self._select_page_by_name(name)

    async def _update_client_list(self) -> None:
        """Updates the list of clients for the log."""

        # add all clients to list
        self.listClients.clear()
        for client_name in self.comm.clients:
            # create item
            item = QtWidgets.QListWidgetItem(client_name)
            item.setCheckState(QtCore.Qt.CheckState.Checked)
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
        if _is_float(entry.time):
            time = Time(entry.time, format="unix")
        else:
            time = Time(entry.time)

        # define new row and emit
        row = [
            time.iso.split()[1],
            sender,
            entry.level,
            "%s:%d" % (os.path.basename(entry.filename), entry.line),
            entry.message,
        ]
        self.add_log.emit(row)
        return True

    def _resize_log_table(self) -> None:
        """Resize log table to entries."""

        # resize columns
        self.tableLog.horizontalHeader().resizeSections(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        self.tableLog.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeMode.ResizeToContents)

        # this is a one-time shot, so unconnect signal
        self.log_model.rowsInserted.disconnect(self._resize_log_table)

    def _log_client_changed(self, item: QtWidgets.QListWidgetItem) -> None:
        """Update log filter."""

        # update proxy
        self.log_proxy.filter_source(item.text(), item.checkState() == QtCore.Qt.CheckState.Checked)

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
            async with self.comm.safe_proxy(auto_client, IAutonomous) as proxy:
                if proxy is not None and await proxy.is_running():
                    self.mastermind_running = True
                    break

        # got any?
        self.labelAutonomousWarning.setVisible(self.mastermind_running)

        # get weather modules
        weather_clients = await self.comm.clients_with_interface(IWeather)
        if len(weather_clients) > 0:
            # found one or more, just take the first one
            async with self.comm.proxy(weather_clients[0]) as weather:
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

        # fully denied by ACLs? if the fetch itself fails or pyobs-core doesn't support ACLs yet,
        # fail open and show the module as usual
        if hasattr(IModule, "get_permitted_methods"):
            try:
                async with self.comm.proxy(client, IModule) as proxy:
                    if len(await proxy.get_permitted_methods()) == 0:
                        return False
            # TODO: PyObsError was renamed to PyobsError in pyobs-core (exception-handling rollout
            # step 2, tracks pyobs-core#446) -- update once pyobs-core is bumped past that change.
            except exc.PyObsError:
                pass

        # does client exist already?
        if client in self._widgets:
            return False

        # update client list
        await self._update_client_list()

        # what do we have?
        async with self.comm.proxy(client) as proxy:
            widget, icon = None, None
            for interface, klass in DEFAULT_WIDGETS.items():
                if isinstance(proxy, interface):
                    widget = self.create_widget(klass, module=client)
                    icon = qta.icon(DEFAULT_ICONS[interface])
                    break

        # look at custom widgets
        for cw in self.custom_widgets:
            if cw["module"] == client:
                widget = self.create_widget(cw["widget"], module=client)

                # got an icon?
                icon = qta.icon(cw["icon"]) if "icon" in cw else qta.icon(DEFAULT_ICONS[None])

        # still nothing?
        if widget is None:
            return False

        # custom sidebar?
        for csw in self.custom_sidebar_widgets:
            if csw["module"] == client:
                await widget.add_to_sidebar(self.create_widget(csw["widget"], module=client))

        # add it
        if icon is None:
            icon = qta.icon(DEFAULT_ICONS[None])
        if not self._modules_header_added:
            self._add_section_header("Modules")
            self._modules_header_added = True
        await self._add_client(client, icon, widget)

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

        # unregister its event handlers and those of its sidebar widgets, so it stops
        # reacting to events and can actually be garbage-collected instead of lingering
        # forever as a stale Comm._event_handlers entry
        await widget.discard()

        # remove from dict
        del self._widgets[client]

        # check mastermind
        await self._check_warnings()
        return True

    def get_fits_headers(self, namespaces: Optional[List[str]] = None, **kwargs: Any) -> dict[str, FitsHeaderEntry]:
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
