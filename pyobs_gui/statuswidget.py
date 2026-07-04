import asyncio
import dataclasses
import html
import logging
from typing import Any

import qasync
from PySide6 import QtWidgets, QtCore, QtGui  # type: ignore
from astroplan import Observer

from pyobs.comm import Comm
from pyobs.events import Event, ModuleOpenedEvent, ModuleClosedEvent
from pyobs.interfaces import IModule, Interface
from pyobs.utils.enums import ModuleState
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.base import BaseWidget

log = logging.getLogger(__name__)

# text colors for the different kinds of module detail rows, so their type is
# recognizable at a glance without reading the row's text. Two variants since a
# fixed palette reads fine on a light background but is low-contrast on a dark
# one (or vice versa) — picked based on the app's actual palette at runtime.
_LIGHT_DETAIL_COLORS = {
    "interfaces": "#5F6368",  # gray — static metadata
    "capabilities": "#1A5276",  # blue — static metadata
    "state": "#1E7B34",  # green — live data
    "key": "#202124",  # near-black — field names within a row
    "value": "#B45309",  # amber — plain field values
    "type": "#6A1B9A",  # purple — class name of a nested dataclass value
}
_DARK_DETAIL_COLORS = {
    "interfaces": "#9AA0A6",  # gray — static metadata
    "capabilities": "#8AB4F8",  # blue — static metadata
    "state": "#81C995",  # green — live data
    "key": "#E8EAED",  # near-white — field names within a row
    "value": "#F2A660",  # amber — plain field values
    "type": "#C58AF9",  # purple — class name of a nested dataclass value
}


def _detail_colors() -> dict[str, str]:
    app = QtWidgets.QApplication.instance()
    palette = QtWidgets.QApplication.palette() if app is not None else QtGui.QPalette()
    is_dark = palette.color(QtGui.QPalette.ColorRole.Base).lightness() < 128
    return _DARK_DETAIL_COLORS if is_dark else _LIGHT_DETAIL_COLORS


def _html_prefix(color: str, text: str) -> str:
    return f'<span style="color: {color};">{html.escape(text)}</span>'


def _format_value_html(value: Any, colors: dict[str, str]) -> str:
    """Render a field value, recursing into nested dataclasses and lists/tuples of them."""
    if dataclasses.is_dataclass(value) and not isinstance(value, type):
        type_name = _html_prefix(colors["type"], type(value).__name__)
        fields_html = ", ".join(
            f"{_html_prefix(colors['key'], f.name)}={_format_value_html(getattr(value, f.name), colors)}"
            for f in dataclasses.fields(value)
        )
        return f"{type_name}({fields_html})"
    if isinstance(value, (list, tuple)):
        items = ", ".join(_format_value_html(v, colors) for v in value)
        open_bracket, close_bracket = ("[", "]") if isinstance(value, list) else ("(", ")")
        return f"{open_bracket}{items}{close_bracket}"
    return _html_prefix(colors["value"], repr(value))


def _format_dataclass_html(obj: Any, colors: dict[str, str]) -> str:
    pairs = []
    for f in dataclasses.fields(obj):
        key = _html_prefix(colors["key"], f.name)
        value = _format_value_html(getattr(obj, f.name), colors)
        pairs.append(f"{key}={value}")
    return ", ".join(pairs)


def _detail_label(html_text: str) -> QtWidgets.QLabel:
    label = QtWidgets.QLabel(html_text)
    label.setTextFormat(QtCore.Qt.TextFormat.RichText)
    return label


class StatusItem(QtWidgets.QWidget):
    signal_presence = QtCore.Signal(object, str)

    def __init__(self, comm: Comm, module: str):
        QtWidgets.QWidget.__init__(self)

        self.setAutoFillBackground(True)

        layout = QtWidgets.QHBoxLayout()
        self.labelStatus = QtWidgets.QLabel("UNKNOWN")
        self.labelStatus.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
        self.buttonAction = QtWidgets.QPushButton("Clear error")
        self.buttonAction.setVisible(False)
        layout.addWidget(self.labelStatus)
        layout.addWidget(self.buttonAction)
        layout.setStretch(0, 3)
        layout.setStretch(1, 1)
        self.setLayout(layout)

        self.signal_presence.connect(self._apply_presence)
        self.buttonAction.clicked.connect(self.button_clicked)

        self.comm = comm
        self.name = module

    def on_presence_changed(self, state: ModuleState, error_string: str) -> None:
        """Presence callback — emits signal so Qt update happens on the main thread."""
        self.signal_presence.emit(state, error_string)

    @QtCore.Slot(object, str)  # type: ignore
    def _apply_presence(self, state: ModuleState, error_string: str) -> None:
        if state == ModuleState.READY:
            self.labelStatus.setText("READY")
            self.setStyleSheet("background-color: lime; color: black;")
            self.buttonAction.setVisible(False)
        elif state == ModuleState.ERROR:
            self.labelStatus.setText(f"ERROR: {error_string}")
            self.setStyleSheet("background-color: red; color: black;")
            self.buttonAction.setVisible(True)
        elif state == ModuleState.CLOSED:
            self.labelStatus.setText("OFFLINE")
            self.setStyleSheet("background-color: gray; color: white;")
            self.buttonAction.setVisible(False)
        else:
            self.labelStatus.setText(state.value.upper())
            self.setStyleSheet("background-color: yellow; color: black;")
            self.buttonAction.setVisible(False)

    @qasync.asyncSlot()  # type: ignore
    async def button_clicked(self) -> None:
        async with self.comm.proxy(self.name, IModule) as proxy:
            await proxy.reset_error()


class StateItem(QtCore.QObject):
    """Keeps a tree child row's label in sync with live state updates for one module/interface."""

    signal_state = QtCore.Signal(object)

    def __init__(self, label: QtWidgets.QLabel, prefix_html: str, colors: dict[str, str]):
        QtCore.QObject.__init__(self)
        self.label = label
        self.prefix_html = prefix_html
        self.colors = colors
        self.signal_state.connect(self._apply_state)

    def on_state_changed(self, state: Any) -> None:
        """State callback — emits signal so Qt update happens on the main thread."""
        self.signal_state.emit(state)

    @QtCore.Slot(object)  # type: ignore
    def _apply_state(self, state: Any) -> None:
        self.label.setText(f"{self.prefix_html} {_format_dataclass_html(state, self.colors)}")


class StatusWidget(BaseWidget):
    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)

        self._colors = _detail_colors()

        self.tree = QtWidgets.QTreeWidget()
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.tree)
        self.setLayout(layout)

        self.tree.setColumnCount(3)
        self.tree.setHeaderLabels(["Module", "Version", "Status"])
        self.tree.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)
        self.tree.setFocusPolicy(QtCore.Qt.FocusPolicy.NoFocus)
        self.tree.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree.header().setStretchLastSection(True)
        self.tree.header().setMinimumSectionSize(200)
        self.tree.itemClicked.connect(self._toggle_expanded)

        # presence callback per module, so _module_closed can unsubscribe it -- otherwise a
        # callback bound to a since-removed StatusItem lingers in the comm layer and blows up
        # on the module's next presence update
        self._presence_callbacks: dict[str, Any] = {}

    @staticmethod
    def _toggle_expanded(item: QtWidgets.QTreeWidgetItem, column: int) -> None:
        """Let a click anywhere in a module row expand/collapse it, not just its arrow."""
        if item.childCount() > 0:
            item.setExpanded(not item.isExpanded())

    async def open(
        self,
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        if self.comm is not None:
            await self.comm.register_event(ModuleOpenedEvent, self._module_opened)
            await self.comm.register_event(ModuleClosedEvent, self._module_closed)
            asyncio.create_task(self._init_clients())

    async def _init_clients(self) -> None:
        for client_name in self.comm.clients:
            await self._module_opened(ModuleOpenedEvent(), client_name)

    async def _module_opened(self, event: Event, sender: str) -> bool:
        if not isinstance(event, ModuleOpenedEvent):
            return False
        if self.comm is None:
            return False
        await self._add_module(sender)
        return True

    async def _module_closed(self, event: Event, sender: str) -> bool:
        if not isinstance(event, ModuleClosedEvent):
            return False
        for row in range(self.tree.topLevelItemCount()):
            item = self.tree.topLevelItem(row)
            if item is not None and item.text(0) == sender:
                self.tree.takeTopLevelItem(row)
                break

        callback = self._presence_callbacks.pop(sender, None)
        if callback is not None and self.comm is not None:
            await self.comm.unsubscribe_presence(sender, callback)
        return True

    async def _add_module(self, module: str) -> None:
        item = QtWidgets.QTreeWidgetItem()
        item.setText(0, module)

        # version from capabilities (read once, static)
        caps = await self.comm.get_capabilities(module, IModule)
        if caps is not None:
            item.setText(1, caps.version)

        self._insert_module_item(item)

        # status widget — subscribe_presence delivers current state immediately
        widget = StatusItem(self.comm, module)
        item.setSizeHint(2, widget.minimumSizeHint())
        self.tree.setItemWidget(item, 2, widget)
        self._presence_callbacks[module] = widget.on_presence_changed
        await self.comm.subscribe_presence(module, widget.on_presence_changed)

        try:
            await self._add_module_details(module, item)
        except Exception:
            log.debug("Could not fetch details for module %s.", module, exc_info=True)

    def _insert_module_item(self, item: QtWidgets.QTreeWidgetItem) -> None:
        """Insert a top-level module item, keeping rows sorted by module name."""
        name = item.text(0)
        index = self.tree.topLevelItemCount()
        for i in range(self.tree.topLevelItemCount()):
            existing = self.tree.topLevelItem(i)
            if existing is not None and existing.text(0) > name:
                index = i
                break
        self.tree.insertTopLevelItem(index, item)

    def _add_detail_row(self, parent: QtWidgets.QTreeWidgetItem, html_text: str) -> QtWidgets.QLabel:
        """Add a spanned child row rendering the given rich text, and return its label."""
        child = QtWidgets.QTreeWidgetItem()
        parent.addChild(child)
        # must be set after addChild — a no-op on a not-yet-attached item
        child.setFirstColumnSpanned(True)
        label = _detail_label(html_text)
        child.setSizeHint(0, label.sizeHint())
        self.tree.setItemWidget(child, 0, label)
        return label

    async def _add_module_details(self, module: str, item: QtWidgets.QTreeWidgetItem) -> None:
        """Fetch and add child rows with interfaces, capabilities and live state."""
        interfaces: list[type[Interface]] = await self.comm.get_interfaces(module)

        names = ", ".join(interface.__name__ for interface in interfaces)
        self._add_detail_row(item, _html_prefix(self._colors["interfaces"], f"Interfaces: {names}"))

        for interface in interfaces:
            if interface.capabilities is not None:
                caps = await self.comm.get_capabilities(module, interface)
                if caps is not None:
                    prefix = _html_prefix(self._colors["capabilities"], f"Capabilities ({interface.__name__}):")
                    self._add_detail_row(item, f"{prefix} {_format_dataclass_html(caps, self._colors)}")

        for interface in interfaces:
            if interface.has_own_state():
                prefix = _html_prefix(self._colors["state"], f"State ({interface.__name__}):")
                label = self._add_detail_row(item, prefix)
                updater = StateItem(label, prefix, self._colors)
                await self.comm.subscribe_state(module, interface, updater.on_state_changed)
