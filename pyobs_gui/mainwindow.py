import asyncio
import logging
import os
from dataclasses import dataclass
from typing import Optional, List, Any, Dict, Callable, Tuple, Type
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
    ICooling,
    Interface,
    ITelescope,
    IRoof,
    IFocuser,
    IRunning,
    ITemperatures,
    IWeather,
    IVideo,
    IAutonomous,
    IRobotic,
    IRoboticScheduler,
    ISpectrograph,
    IFilters,
    IMode,
    IModule,
)

from .base import BaseWindow, BaseWidget, cancel_and_drain
from .acquisitionwidget import AcquisitionWidget
from .autofocuswidget import AutoFocusWidget
from .autoguidingwidget import AutoGuidingWidget
from .camerawidget import CameraWidget
from .coolingwidget import CoolingWidget
from .filterwidget import FilterWidget
from .fitsheaderswidget import FitsHeadersWidget
from .modewidget import ModeWidget
from .roboticwidget import RoboticWidget
from .schedulewidget import ScheduleWidget
from .statuswidget import StatusWidget
from .telescopewidget import TelescopeWidget
from .focuswidget import FocusWidget
from .temperatureswidget import TemperaturesWidget
from .weatherwidget import WeatherWidget
from .videowidget import VideoWidget
from .qt.mainwindow_ui import Ui_MainWindow
from .logmodel import LogModel, LogModelProxy
from .eventswidget import EventsWidget
from .roofwidget import RoofWidget
from .shellwidget import ShellWidget
from .spectrographwidget import SpectrographWidget

log = logging.getLogger(__name__)

# icon shown for a custom widget entry (in widgets:/sidebar: config) that declares no icon of
# its own
_DEFAULT_ICON = "fa5.question-circle"


@dataclass(frozen=True)
class MainWidgetEntry:
    """One row of the MAIN_WIDGETS registry: an interface, the main widget it drives, its tab
    label/icon, the sidebar widgets it declares, and the two demotion mechanisms (see
    specs/2026-08-28-gui-main-vs-sidebar-widgets.md, D1/D6)."""

    interface: Type[Interface]
    widget: Type[BaseWidget]
    label: str
    icon: str
    sidebar: Tuple[Tuple[Optional[Type[Interface]], Type[BaseWidget]], ...] = ()
    # cross-interface demotion: only promoted into `main` when nothing else matched (D1)
    sidebar_preferred: bool = False
    # same-interface pairing: always rendered together whenever this entry survives into `main`
    # (D6); no MAIN_WIDGETS entry sets this yet -- first consumer is the VideoWidget split,
    # tracked separately in specs/2026-09-01-gui-video-widget-split.md
    paired_sidebar_widget: Optional[Type[BaseWidget]] = None


MAIN_WIDGETS: List[MainWidgetEntry] = [
    # IFilters/ICooling/ITemperatures are NOT declared here even though Camera wants them in its
    # sidebar -- they're sidebar_preferred entries below, so collect_main_widgets()'s promotion
    # rule already demotes them into the sidebar whenever Camera (or any other non-preferred
    # match) wins. Declaring them here too would add each one to the sidebar twice (confirmed
    # regression, PR #157 review) -- only FitsHeadersWidget, which has no registry entry of its
    # own, belongs in a declared `sidebar` tuple.
    MainWidgetEntry(ICamera, CameraWidget, "Camera", "fa5s.camera", sidebar=((None, FitsHeadersWidget),)),
    # IFilters/IFocuser/ITemperatures: same reasoning as Camera above -- all sidebar_preferred,
    # already demoted into the sidebar by the promotion rule, not declared here.
    MainWidgetEntry(ITelescope, TelescopeWidget, "Telescope", "msc.telescope"),
    MainWidgetEntry(IRoof, RoofWidget, "Roof", "ph.house"),
    MainWidgetEntry(IFocuser, FocusWidget, "Focuser", "mdi.image-filter-center-focus", sidebar_preferred=True),
    MainWidgetEntry(IAutoFocus, AutoFocusWidget, "Auto focus", "mdi.chart-bell-curve"),
    MainWidgetEntry(IAcquisition, AcquisitionWidget, "Acquisition", "mdi.target"),
    MainWidgetEntry(IAutoGuiding, AutoGuidingWidget, "Auto guiding", "mdi.crosshairs-gps"),
    MainWidgetEntry(IWeather, WeatherWidget, "Weather", "fa5s.cloud-sun"),
    MainWidgetEntry(IVideo, VideoWidget, "Video", "fa5s.video", sidebar=((None, FitsHeadersWidget),)),
    MainWidgetEntry(ISpectrograph, SpectrographWidget, "Spectrograph", "ei.graph"),
    MainWidgetEntry(IFilters, FilterWidget, "Filter wheel", "mdi.air-filter", sidebar_preferred=True),
    MainWidgetEntry(ITemperatures, TemperaturesWidget, "Temperatures", "mdi.thermometer", sidebar_preferred=True),
    MainWidgetEntry(ICooling, CoolingWidget, "Cooling", "mdi.snowflake", sidebar_preferred=True),
    MainWidgetEntry(IMode, ModeWidget, "Mode", "ei.video"),
    # not part of the #150 audit's original snippet (added to DEFAULT_WIDGETS by the later
    # irobotic-widgets plan, #825/PR #155) -- kept here so the registry consolidation doesn't
    # regress robotic-module support
    MainWidgetEntry(IRobotic, RoboticWidget, "Robotic", "mdi.robot"),
    MainWidgetEntry(IRoboticScheduler, ScheduleWidget, "Scheduler", "mdi.calendar-clock"),
]

# added to every module's sidebar unconditionally, regardless of interface matches or promotion
# (D2) -- for content that isn't tied to any one interface. Empty today: FITS headers only make
# sense for modules that actually write FITS files (ICamera, IVideo), so that's a per-entry
# `sidebar=((None, FitsHeadersWidget), ...)` declaration on those two MAIN_WIDGETS rows instead
# of a universal one -- see those entries above. Kept as a real (if currently unused) mechanism
# since D2 explicitly wants an escape hatch for genuinely module-agnostic sidebar content.
ALWAYS_SIDEBAR_WIDGETS: Tuple[Type[BaseWidget], ...] = ()


@dataclass
class WidgetChoice:
    """One instantiated main widget plus everything needed to place it: its tab label/icon, the
    sidebar widgets it declares (or its class's `sidebar_fills` override, see
    collect_main_widgets), and its D6 paired sidebar widget class, if any."""

    widget: BaseWidget
    label: str
    icon: QtGui.QIcon
    sidebar: Tuple[Tuple[Optional[Type[Interface]], Type[BaseWidget]], ...] = ()
    paired_sidebar_widget: Optional[Type[BaseWidget]] = None
    # the MAIN_WIDGETS interface this choice originated from (None for a custom widgets: entry
    # that isn't replacing a registry slot) -- used only to dedupe a sidebar_preferred choice
    # against an overlapping declared `sidebar` fill on another entry, see open_module_page()
    interface: Optional[Type[Interface]] = None


def _custom_widget_choice(
    cw: Dict[str, Any], make_widget: Callable[[Any], BaseWidget], interface: Optional[Type[Interface]] = None
) -> WidgetChoice:
    widget = make_widget(cw["widget"])
    label = cw.get("label", type(widget).__name__)
    icon = qta.icon(cw["icon"]) if "icon" in cw else qta.icon(_DEFAULT_ICON)
    # a custom widgets: entry has no registry `sidebar` tuple of its own -- fall back to the
    # widget class's own `sidebar_fills`, if it declares one (see "Sidebar fills: the
    # class-attribute option"), so wiring e.g. CameraWidget in via custom config doesn't lose
    # its built-in sidebar
    sidebar = getattr(type(widget), "sidebar_fills", ())
    # `interface` is set only when this entry is replacing a registry slot in place (D3), so it
    # still "counts" as covering that interface for open_module_page()'s sidebar dedup even
    # though the widget class itself is now a custom one
    return WidgetChoice(widget=widget, label=label, icon=icon, sidebar=sidebar, interface=interface)


def collect_main_widgets(
    matchable: Any,
    make_widget: Callable[[Any], BaseWidget],
    custom: Optional[List[Dict[str, Any]]] = None,
) -> Tuple[List[WidgetChoice], List[WidgetChoice]]:
    """Walks MAIN_WIDGETS for every entry whose interface `matchable` (a comm proxy or a Module
    instance) implements, applies the sidebar_preferred promotion rule (D1), then layers the
    custom widgets: config on top (D3).

    Returns `(main, sidebar_preferred)`:
      - `main`: ordered list of widgets to show as page content. Empty means "no page for this
        module" (today's behavior, unchanged).
      - `sidebar_preferred`: matches that were NOT promoted into `main` (because `main` was
        already non-empty) and should instead fill the page's sidebar.
    """
    matches = [e for e in MAIN_WIDGETS if isinstance(matchable, e.interface)]
    main_entries = [e for e in matches if not e.sidebar_preferred]
    sidebar_preferred_entries: List[MainWidgetEntry] = []
    if main_entries:
        sidebar_preferred_entries = [e for e in matches if e.sidebar_preferred]
    else:
        # nothing else matched -- promote every sidebar_preferred match into main instead, so a
        # standalone filter-wheel/focuser/temperature-sensor/cooling module still gets its own
        # page (or tabs, if it matches more than one)
        main_entries = [e for e in matches if e.sidebar_preferred]

    custom = custom or []

    # D3: interface: None + overwrite: true -- the page becomes exactly the custom entries
    overwrite_entries = [cw for cw in custom if cw.get("interface") is None and cw.get("overwrite")]
    if overwrite_entries:
        return [_custom_widget_choice(cw, make_widget) for cw in overwrite_entries], []

    def entry_choice(entry: MainWidgetEntry) -> WidgetChoice:
        return WidgetChoice(
            widget=make_widget(entry.widget),
            label=entry.label,
            icon=qta.icon(entry.icon),
            sidebar=getattr(entry.widget, "sidebar_fills", entry.sidebar),
            paired_sidebar_widget=entry.paired_sidebar_widget,
            interface=entry.interface,
        )

    main_choices: List[WidgetChoice] = [entry_choice(e) for e in main_entries]
    sidebar_preferred_choices: List[WidgetChoice] = [entry_choice(e) for e in sidebar_preferred_entries]

    for cw in custom:
        interface_name = cw.get("interface")
        if interface_name is not None and cw.get("overwrite"):
            # ambiguous combination: overwrite_entries above only fires for interface: None, so
            # this entry falls through to the interface-replace branch below and its
            # `overwrite` key is simply never read -- not a bug, but silent, so flag it
            log.warning(
                "Custom widget config for interface %r also sets overwrite: true; overwrite is "
                "only honored without an interface -- this entry replaces just that interface's "
                "slot, overwrite is ignored.",
                interface_name,
            )
        if interface_name is not None:
            # replace the same-interface slot in place, whether it's a plain main-widget slot or
            # one currently demoted into the sidebar (sidebar_preferred); keeps tab/sidebar order.
            # Ignored with a log if the module doesn't actually implement that interface at all.
            idx = next((i for i, e in enumerate(main_entries) if e.interface.__name__ == interface_name), None)
            if idx is not None and isinstance(matchable, main_entries[idx].interface):
                main_choices[idx] = _custom_widget_choice(cw, make_widget, interface=main_entries[idx].interface)
                continue
            sidx = next(
                (i for i, e in enumerate(sidebar_preferred_entries) if e.interface.__name__ == interface_name), None
            )
            if sidx is not None and isinstance(matchable, sidebar_preferred_entries[sidx].interface):
                sidebar_preferred_choices[sidx] = _custom_widget_choice(
                    cw, make_widget, interface=sidebar_preferred_entries[sidx].interface
                )
                continue
            log.warning("Custom widget config for interface %r ignored: module doesn't implement it.", interface_name)
        elif not cw.get("overwrite"):
            # no interface, no overwrite -- appended as an extra tab
            main_choices.append(_custom_widget_choice(cw, make_widget))

    return main_choices, sidebar_preferred_choices


class ModulePage(BaseWidget):
    """Page host for one connected module -- the universal page host, whether the module matched
    one main widget or several (D2). Exactly one widget renders directly with no tab chrome;
    two or more get a QTabWidget, one tab per widget. The sidebar column is a property of the
    page, shared across every tab: add_to_sidebar()/get_fits_headers() are inherited unchanged
    from BaseWidget (they already work on any object exposing `self.widgetSidebar`); only
    discard() and get_fits_headers() need widening to also cover the tab widgets themselves.
    """

    def __init__(
        self,
        choices: List[WidgetChoice],
        sidebar_preferred: Optional[List[WidgetChoice]] = None,
        custom_sidebar: Optional[List[Dict[str, Any]]] = None,
        **kwargs: Any,
    ) -> None:
        BaseWidget.__init__(self, **kwargs)
        self.choices = choices
        self.widgets: List[BaseWidget] = [c.widget for c in choices]
        self.tab_widget: Optional[QtWidgets.QTabWidget] = None
        # carried through from collect_main_widgets() for open_module_page() to consume once
        # this page's widgets have actually opened -- see its sidebar-fill steps (c) and (e)
        self.sidebar_preferred_choices: List[WidgetChoice] = sidebar_preferred or []
        self.custom_sidebar: List[Dict[str, Any]] = custom_sidebar or []

        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        if len(choices) == 1:
            content: QtWidgets.QWidget = choices[0].widget
        else:
            self.tab_widget = QtWidgets.QTabWidget()
            for choice in choices:
                self.tab_widget.addTab(choice.widget, choice.icon, choice.label)
            content = self.tab_widget
        layout.addWidget(content, 1)

        # sidebar column -- BaseWidget.add_to_sidebar() fills this in via `hasattr(self,
        # "widgetSidebar")`, exactly like the per-widget .ui-declared ones (camerawidget.ui etc.).
        # Wrapped in a QScrollArea since the shared sidebar (D2) aggregates fills across every
        # tab, so it can grow taller than any single old widget's hand-picked sidebar ever did.
        self.widgetSidebar = QtWidgets.QWidget()

        self.sidebar_scroll = QtWidgets.QScrollArea()
        self.sidebar_scroll.setWidget(self.widgetSidebar)
        self.sidebar_scroll.setWidgetResizable(True)
        self.sidebar_scroll.setFrameShape(QtWidgets.QFrame.Shape.NoFrame)
        self.sidebar_scroll.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.sidebar_scroll.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.sidebar_scroll.setMaximumWidth(320)
        self.sidebar_scroll.setVisible(False)
        layout.addWidget(self.sidebar_scroll)

    def remove_widget(self, widget: BaseWidget) -> None:
        """Removes one tab (D5: a partially-failed open drops just that widget's tab, keeping
        the rest of the page). No-op if `widget` is the page's sole (non-tabbed) content --
        callers are expected to have already checked for the all-failed case."""
        if widget not in self.widgets:
            return
        self.widgets.remove(widget)
        if self.tab_widget is not None:
            idx = self.tab_widget.indexOf(widget)
            if idx != -1:
                self.tab_widget.removeTab(idx)

    def hide_if_empty_sidebar(self) -> None:
        self.sidebar_scroll.setVisible(len(self.sidebar_widgets) > 0)

    async def discard(self) -> None:
        for widget in list(self.widgets):
            await widget.discard()
        await super().discard()

    def get_fits_headers(self, namespaces: Optional[List[str]] = None, **kwargs: Any) -> dict[str, FitsHeaderEntry]:
        hdr: dict[str, FitsHeaderEntry] = {}
        for widget in self.widgets:
            if hasattr(widget, "get_fits_headers"):
                for k, v in widget.get_fits_headers(namespaces, **kwargs).items():
                    hdr[k] = v
        for k, v in super().get_fits_headers(namespaces, **kwargs).items():
            hdr[k] = v
        return hdr


async def open_module_page(
    page: ModulePage,
    client: str,
    comm: Any,
    observer: Any,
    vfs: Any,
    create_widget: Callable[..., BaseWidget],
) -> bool:
    """Opens every one of `page`'s main widgets concurrently (D5), then applies the sidebar
    fills in order: (a) ALWAYS_SIDEBAR_WIDGETS, (b) each surviving choice's declared/class
    sidebar fills, (c) promoted-away sidebar_preferred matches, (d) paired sidebar widgets (D6),
    (e) custom sidebar entries. Shared between MainWindow._open_client (background, per-client
    open task) and ModuleWindow.open() (standalone mode) so both get identical behavior.

    A failing widget is logged, discarded, and its tab dropped; the page survives as long as at
    least one widget opened successfully -- returns False only when every widget failed, so the
    caller can treat that like a whole-client open failure (mirrors today's single-widget
    _fail_open path).
    """
    await page.open(modules=[client], comm=comm, observer=observer, vfs=vfs)

    results = await asyncio.gather(
        *(w.open(modules=[client], comm=comm, observer=observer, vfs=vfs) for w in page.widgets),
        return_exceptions=True,
    )
    survivors: List[WidgetChoice] = []
    for choice, result in zip(list(page.choices), results, strict=True):
        if isinstance(result, BaseException):
            if isinstance(result, asyncio.CancelledError):
                raise result
            log.error("Failed to open widget %s for %s", type(choice.widget).__name__, client, exc_info=result)
            page.remove_widget(choice.widget)
            await choice.widget.discard()
        else:
            survivors.append(choice)

    if not survivors:
        return False

    for klass in ALWAYS_SIDEBAR_WIDGETS:
        await page.add_to_sidebar(create_widget(klass, module=client))

    # an interface already covered by a demoted sidebar_preferred match (below) is skipped here
    # even if some survivor's declared `sidebar` tuple also names it -- keyed by interface, not
    # widget class, so this still holds when a custom widgets: entry (D3) has replaced that
    # demoted slot with a different widget class. Defends against the exact double-add
    # regression PR #157 review found in the production registry (Camera/Telescope's declared
    # fills used to duplicate their own sidebar_preferred entries); the registry itself no
    # longer declares such overlaps, but this keeps a future one from silently reintroducing
    # duplicate sidebar widgets
    demoted_interfaces = {c.interface for c in page.sidebar_preferred_choices if c.interface is not None}
    for choice in survivors:
        for interface, klass in choice.sidebar:
            if interface is not None and interface in demoted_interfaces:
                continue
            if interface is None or await comm.has_proxy(client, interface):
                await page.add_to_sidebar(create_widget(klass, module=client))

    for sidebar_choice in page.sidebar_preferred_choices:
        # add_to_sidebar() -> _open_child() opens the widget itself (module/comm/observer/vfs
        # come from `page`, set by page.open() above) -- no separate explicit open() call here,
        # so a failure is caught by add_to_sidebar's own isolation (D5) like every other fill
        await page.add_to_sidebar(sidebar_choice.widget)

    for choice in survivors:
        if choice.paired_sidebar_widget is not None:
            sidebar_widget = create_widget(choice.paired_sidebar_widget, module=client)
            choice.widget.paired_sidebar = sidebar_widget  # type: ignore[attr-defined]
            sidebar_widget.paired_main = choice.widget  # type: ignore[attr-defined]
            await page.add_to_sidebar(sidebar_widget)

    for csw in page.custom_sidebar:
        await page.add_to_sidebar(create_widget(csw["widget"], module=client))

    page.hide_if_empty_sidebar()
    return True


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


class StayOpenMenu(QtWidgets.QMenu):  # type: ignore
    """A QMenu that stays open when a checkable action inside it is clicked, so several
    clients can be toggled in one go instead of reopening the menu after every click."""

    def mouseReleaseEvent(self, event: QtGui.QMouseEvent) -> None:
        action = self.activeAction()
        if action is not None and action.isCheckable():
            action.trigger()
            return
        super().mouseReleaseEvent(event)


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
        on_logout: Optional[Callable[[], None]] = None,
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
            on_logout: If given, the bottom-left button reads "Log out" and invokes this
                instead of closing the window -- used in standalone (login-window) mode, where
                the GUI module stays alive and reconnects rather than the whole app quitting.
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
        self._logging_out = False

        # splitters
        self.splitterClients.setSizes([self.width() - 40, 40])
        self.splitterLog.setSizes([self.height() - 140, 140])
        # splitterNav's width is actively reasserted on every resizeEvent instead of being set once
        # here -- see resizeEvent() for why
        self._nav_width = 230
        self.splitterNav.splitterMoved.connect(self._on_nav_splitter_moved)

        # logs
        self.log_model = LogModel()
        self.add_log.connect(self.log_model.add_entry)
        self.log_proxy = LogModelProxy()
        self.log_proxy.setSourceModel(self.log_model)
        self.tableLog.setModel(self.log_proxy)
        self.log_model.rowsInserted.connect(self.log_entry_added)
        self.log_model.rowsInserted.connect(self._resize_log_table)

        # log tools: clear / copy / select-clients-shown, icon-only, next to the log table
        self.widgetLogTools.setMaximumWidth(40)
        self.buttonClearLog.setIcon(qta.icon("fa5s.trash"))
        self.buttonClearLog.clicked.connect(self._clear_log)
        self.buttonCopyLog.setIcon(qta.icon("fa5s.copy"))
        self.buttonCopyLog.clicked.connect(self._copy_log)
        self.buttonSelectClients.setIcon(qta.icon("fa5s.filter"))
        self._clients_menu = StayOpenMenu(self)
        self.buttonSelectClients.setMenu(self._clients_menu)

        # mastermind
        self.labelAutonomousWarning.setVisible(False)
        self.labelWeatherWarning.setVisible(False)

        # top bar
        if on_logout is not None:
            self.buttonQuit.setText("Log out")
            self.buttonQuit.clicked.connect(on_logout)
        else:
            self.buttonQuit.clicked.connect(self.close)

        # list of widgets
        self._widgets: Dict[str, BaseWidget] = {}
        # client -> current page in the stacked widget (a "Loading…" placeholder until the
        # widget's open() finished, then the widget itself) -- see _add_client/_open_client
        self._pages: Dict[str, QtWidgets.QWidget] = {}
        # client -> in-flight background open task (see _add_client)
        self._pending_opens: Dict[str, asyncio.Task[None]] = {}
        self._current_widget = None
        self.shell: Optional[ShellWidget] = None
        self.events: Optional[EventsWidget] = None
        self.status: Optional[StatusWidget] = None
        self._modules_header_added = False

        # navbar keyboard shortcuts: slot -> currently bound page name, session-only (see
        # pyobs-core/specs/plans/gui-navbar-shortcuts.md)
        self._slot_bindings: Dict[str, str] = {}
        self.listPages.setItemDelegate(NavPageItemDelegate(self._slot_bindings, self))
        self._setup_shortcuts()

    async def open(self, **kwargs: Any) -> None:  # type: ignore
        """Open module."""

        # get module
        module = kwargs.pop("module")

        # open widgets
        await BaseWindow.open(self, modules=[module], **kwargs)

        # who are we logged in as?
        self.labelLoggedInAs.setText(f"Logged in as: {self.comm.name}")

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
        self._update_clients_menu()
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
        # create other nav buttons and views -- in parallel, so a slow module (e.g. the
        # telescope) no longer blocks every other module from appearing
        await asyncio.gather(*(self._client_connected(Event(), c) for c in self.comm.clients))

        # one fresh warning pass now that all modules are in (the periodic task keeps it
        # current afterwards)
        await self._check_warnings()

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        if self.warning_task is not None:
            self.warning_task.cancel()
        if self._logging_out:
            # GUI._logout() is replacing this window with a fresh one -- the module itself
            # stays alive and reconnects, so it must not be quit here.
            return
        if self.module is not None:
            # quit() exists on Module but is not declared on Proxy
            self.module.quit()  # pyrefly: ignore [missing-attribute] —

    def close_for_logout(self) -> None:
        """Closes this window as part of GUI._logout()'s reconnect flow, without quitting the
        module (see closeEvent)."""
        self._logging_out = True
        self.close()

    async def discard_all_widgets(self) -> None:
        """Unregisters every widget's comm event handlers/subscriptions -- must be awaited
        *before* this window is closed/deleted as part of a reconnect (GUI._logout()), otherwise
        a stray in-flight event/state callback can fire after Qt has already destroyed the
        widget it targets (e.g. "libshiboken: Internal C++ object already deleted")."""
        # cancel and drain any in-flight background opens first, so no _open_client task is
        # still mutating the stackedWidget / a widget after teardown begins -- cancel all
        # before draining any, so they unwind concurrently instead of one after another
        for task in self._pending_opens.values():
            task.cancel()
        for task in list(self._pending_opens.values()):
            await cancel_and_drain(task)
        self._pending_opens.clear()

        for widget in list(self._widgets.values()):
            await widget.discard()

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

        # register immediately, so _change_page and the shortcuts always find the client --
        # even while the widget's open() is still running below
        self._widgets[client] = widget

        # placeholder page: clickable now, explains the delay, needs no per-widget changes
        placeholder = self._make_loading_page(client, icon)
        self.stackedWidget.addWidget(placeholder)
        self._pages[client] = placeholder

        # open in the background; swap in the real widget when done
        self._pending_opens[client] = asyncio.create_task(self._open_client(client, widget))

    async def _open_client(self, client: str, widget: BaseWidget) -> None:
        try:
            if isinstance(widget, ModulePage):
                # D5: gather-open with per-tab failure handling, then apply sidebar fills.
                # Raise so the except branch below runs the same _fail_open teardown as a
                # plain single-widget open failure -- open_module_page returns False only
                # when every one of the page's main widgets failed.
                if not await open_module_page(widget, client, self.comm, self.observer, self.vfs, self.create_widget):
                    raise RuntimeError(f"All main widgets failed to open for {client}")
            else:
                await widget.open(
                    modules=[client] if client is not None else [],
                    comm=self.comm,
                    observer=self.observer,
                    vfs=self.vfs,
                )
        except Exception:
            # open() failed (RPC errors etc.): tear the client down rather than leaving a
            # permanent "Loading…" dead page behind. Note asyncio.CancelledError is NOT
            # caught here (it subclasses BaseException), so a mid-open disconnect -- which
            # cancels this task -- still unwinds through the finally below and never reaches
            # this branch.
            log.exception("Failed to open widget for %s", client)
            await self._fail_open(client, widget)
            return
        finally:
            self._pending_opens.pop(client, None)

        # swap placeholder -> real widget at the same stackedWidget index
        placeholder = self._pages.get(client)
        if placeholder is None:
            return  # client disconnected while opening

        # capture BEFORE removeWidget(placeholder): once the placeholder is removed from the
        # stack it can never again be currentWidget(), so the check has to happen first or the
        # "user is sitting on this page" branch below can never fire
        was_current = self.stackedWidget.currentWidget() is placeholder

        idx = self.stackedWidget.indexOf(placeholder)
        self.stackedWidget.removeWidget(placeholder)
        placeholder.deleteLater()
        self.stackedWidget.insertWidget(idx, widget)
        self._pages[client] = widget

        # if the user is sitting on this page, show the real widget now -- showEvent ->
        # _init() runs and the content fills in
        if was_current:
            self.stackedWidget.setCurrentWidget(widget)

    async def _fail_open(self, client: str, widget: BaseWidget) -> None:
        """Undo a failed _add_client: nav item, placeholder page, and registry entries.
        No-op if the client already disconnected mid-open (its own teardown handled it)."""
        if self._pages.get(client) is None:
            return
        self._widgets.pop(client, None)
        for row in range(self.listPages.count()):
            if self.listPages.item(row).text() == client:
                self.listPages.takeItem(row)
                break
        placeholder = self._pages.pop(client, None)
        if placeholder is not None:
            if self.stackedWidget.currentWidget() is placeholder:
                self._current_widget = None
            self.stackedWidget.removeWidget(placeholder)
            placeholder.deleteLater()
        await widget.discard()

    def _make_loading_page(self, client: str, icon: QtGui.QIcon) -> QtWidgets.QWidget:
        """Returns a plain "Loading <client>…" page (module icon + grey label) that stands in
        for the real widget while its open() is still running. No new dependency."""
        page = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(page)
        layout.addStretch()
        icon_label = QtWidgets.QLabel()
        icon_label.setPixmap(icon.pixmap(48, 48))
        icon_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        label = QtWidgets.QLabel(f"Loading {client}…")
        label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("color: grey;")
        layout.addWidget(label)
        layout.addStretch()
        return page

    @QtCore.Slot(int)  # type: ignore
    def _change_page(self, idx: int) -> None:
        """Change page.

        Args:
            idx: Index of new page in nav list.
        """

        # get name of new page
        item = self.listPages.item(idx)
        client = item.text() if item is not None else None

        # section headers (and an empty selection) aren't real pages -- they are in neither
        # self._pages nor self._widgets
        if client not in self._pages:
            return

        # change to new page (may be a placeholder while the widget is still opening)
        self.stackedWidget.setCurrentWidget(self._pages[client])

        # get new widget
        self._current_widget = self.stackedWidget.currentWidget()

    def _setup_shortcuts(self) -> None:
        """Creates the 17 fixed/assignable navbar shortcuts. Handlers do dynamic lookups against
        self._widgets / self._slot_bindings at press-time, since module pages come and go but the
        shortcut objects themselves live for the app's lifetime. Every shortcut requires Ctrl (or
        Ctrl+Alt) so no text/numeric-entry widget can ever mistake one for ordinary input -- see
        pyobs-core/specs/plans/gui-navbar-shortcuts.md for why that's a structural guarantee
        rather than one that needs per-widget-type verification.
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

    def _update_clients_menu(self) -> None:
        """Rebuilds the select-clients menu for the log -- cheap and purely local, so it can run
        per connect/disconnect. (The Shell command model is the Shell widget's own job -- it
        rebuilds debounced and only while its page is visible, see shellwidget.py.)"""

        # rebuild the menu -- every connected client, checked (shown) by default. A checkbox
        # inside a QWidgetAction (rather than a plain checkable QAction) both lets the entry's
        # text be colored to match the client's color in the log table, and -- as a side effect
        # -- keeps the menu open on click, since the click is consumed by the checkbox widget
        # itself rather than by QMenu's own action-triggering/auto-close logic.
        self._clients_menu.clear()
        for client_name in self.comm.clients:
            checkbox = QtWidgets.QCheckBox(client_name, self._clients_menu)
            checkbox.setChecked(True)
            palette = checkbox.palette()
            palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(Color(pick_for=client_name).hex))
            checkbox.setPalette(palette)
            checkbox.toggled.connect(lambda checked, name=client_name: self.log_proxy.filter_source(name, checked))

            action = QtWidgets.QWidgetAction(self._clients_menu)
            action.setDefaultWidget(checkbox)
            self._clients_menu.addAction(action)

    def _clear_log(self) -> None:
        self.log_model.clear()

    def _copy_log(self) -> None:
        QtWidgets.QApplication.clipboard().setText(self.log_model.to_text())

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
                running_state = proxy.get_state(IRunning) if proxy is not None else None
                if running_state is not None and running_state.running:
                    self.mastermind_running = True
                    break

        # got any?
        self.labelAutonomousWarning.setVisible(self.mastermind_running)

        # get weather modules
        weather_clients = await self.comm.clients_with_interface(IWeather)
        if len(weather_clients) > 0:
            # found one or more, just take the first one
            async with self.comm.proxy(weather_clients[0]) as weather:
                weather_running_state = weather.get_state(IRunning)
                is_running = weather_running_state is not None and weather_running_state.running
                self.labelWeatherWarning.setVisible(not is_running)
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
            except exc.PyobsError:
                pass

        # does client exist already?
        if client in self._widgets:
            return False

        # update client list (cheap menu rebuild; the shell model is the shell's own job)
        self._update_clients_menu()

        # what do we have? (D1/D3: registry match + custom widgets: config merge/overwrite)
        custom = [cw for cw in self.custom_widgets if cw["module"] == client]
        async with self.comm.proxy(client) as proxy:
            main_choices, sidebar_preferred_choices = collect_main_widgets(
                proxy, lambda klass: self.create_widget(klass, module=client), custom
            )

        # still nothing?
        if not main_choices:
            return False

        # custom sidebar (D2: applied at page-assembly time, always visible regardless of the
        # module's widget type -- see ModulePage)
        custom_sidebar = [csw for csw in self.custom_sidebar_widgets if csw["module"] == client]

        # D4: nav icon is the first matched (or custom-replacing) entry's icon
        icon = main_choices[0].icon
        if not self._modules_header_added:
            self._add_section_header("Modules")
            self._modules_header_added = True
        page = self.create_widget(
            ModulePage,
            choices=main_choices,
            sidebar_preferred=sidebar_preferred_choices,
            custom_sidebar=custom_sidebar,
        )
        await self._add_client(client, icon, page)
        return True

    async def _client_disconnected(self, event: Event, client: str) -> bool:
        """Called, when a client disconnects.

        Args:
            client: Name of client.
        """

        # update client list (cheap menu rebuild; the shell model is the shell's own job)
        self._update_clients_menu()

        # not in list?
        if client not in self._widgets:
            return False

        # cancel a pending open BEFORE discard(), and await the cancellation: cancel() is not
        # synchronous (the coroutine only unwinds at its next await inside widget.open()), so
        # without this await, widget.discard() below could run concurrently with the tail of a
        # not-yet-finished open() -- e.g. sidebar widgets added after discard, or handlers
        # re-registered after unregister. This race is newly exposed by registering the widget
        # early in _add_client: before, the widget wasn't in self._widgets mid-open, so this
        # method returned early and discard() could never run while open() was in flight.
        task = self._pending_opens.pop(client, None)
        if task is not None:
            await cancel_and_drain(task)

        # get widget
        widget = self._widgets[client]

        # is current? (the placeholder may be the current page mid-open)
        if self.stackedWidget.currentWidget() in (widget, self._pages.get(client)):
            self._current_widget = None

        # remove placeholder page, if any -- a dict pop alone would leave a ghost QWidget in
        # the stack, and if it was the current page it would stay visible after the module
        # vanished
        placeholder = self._pages.pop(client, None)
        if placeholder is not None:
            self.stackedWidget.removeWidget(placeholder)
            placeholder.deleteLater()

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
