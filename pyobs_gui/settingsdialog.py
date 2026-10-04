"""Settings dialog, standalone mode only -- see specs/2026-10-04-settings-dialog.md.

Edits a `GuiSettings`. Apply/OK hand the result to `on_apply` (the GUI saves it and puts it into
effect); a problem, in the input or reported by `on_apply`, is shown in the dialog and keeps it open.
"""

from __future__ import annotations

import logging

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import ValidationError
from pyobs.object import get_class_from_string
from PySide6 import QtWidgets  # type: ignore

from .settings import GuiSettings, NotificationSettings, VfsSettings

if TYPE_CHECKING:
    from collections.abc import Callable

log = logging.getLogger(__name__)

# VFS classes offered in the class box (any other class path can still be typed)
_VFS_CLASSES = [
    "pyobs.vfs.HttpFile",
    "pyobs.vfs.LocalFile",
    "pyobs.vfs.SMBFile",
    "pyobs.vfs.SFTPFile",
    "pyobs.vfs.SSHFile",
    "pyobs.vfs.ArchiveFile",
    "pyobs.vfs.MemoryFile",
    "pyobs.vfs.TempFile",
]


@dataclass
class _RootEntry:
    name: str
    klass: str
    params: str  # YAML mapping, without the class


class SettingsDialog(QtWidgets.QDialog):
    # Every leaf of GuiSettings and the attribute of the widget that edits it. A test checks that
    # this covers the schema, so a new setting can't be added without a place in the dialog.
    FIELD_WIDGETS = {
        "notifications.enabled": "_notif_enabled",
        "notifications.min_log_level": "_notif_level",
        "notifications.only_when_inactive": "_notif_inactive",
        "notifications.muted_modules": "_notif_muted",
        "notifications.rate_limit": "_notif_rate",
        "vfs.roots": "_roots_list",
    }

    def __init__(
        self,
        settings: GuiSettings,
        modules: list[str],
        on_apply: Callable[[GuiSettings], None],
        parent: QtWidgets.QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(640, 480)
        self._on_apply = on_apply
        self._modules = sorted(modules)
        self._entries: list[_RootEntry] = []
        self._current = -1

        layout = QtWidgets.QVBoxLayout(self)
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(self._build_notifications_tab(), "Notifications")
        tabs.addTab(self._build_vfs_tab(), "VFS")
        layout.addWidget(tabs)

        self._error = QtWidgets.QLabel()
        self._error.setWordWrap(True)
        self._error.setStyleSheet("color: #c0392b;")
        self._error.setVisible(False)
        layout.addWidget(self._error)

        buttons = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Apply
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._ok)
        buttons.rejected.connect(self.reject)
        buttons.button(QtWidgets.QDialogButtonBox.StandardButton.Apply).clicked.connect(self._apply)
        layout.addWidget(buttons)

        self._load(settings)

    # ── notifications tab ────────────────────────────────────────────────────

    def _build_notifications_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(tab)

        self._notif_enabled = QtWidgets.QCheckBox("Show desktop notifications")
        form.addRow(self._notif_enabled)

        self._notif_level = QtWidgets.QComboBox()
        self._notif_level.addItems(["ERROR", "CRITICAL"])
        form.addRow("Log events from level", self._notif_level)

        self._notif_inactive = QtWidgets.QCheckBox("Only when this window is not active")
        form.addRow(self._notif_inactive)

        self._notif_rate = QtWidgets.QDoubleSpinBox()
        self._notif_rate.setRange(0, 3600)
        self._notif_rate.setSuffix(" s")
        self._notif_rate.setToolTip("Repeats from the same module within this time are combined. 0 turns it off.")
        form.addRow("Combine repeats within", self._notif_rate)

        # muted modules: list, plus a box (completing from the connected modules) to add to it
        self._notif_muted = QtWidgets.QListWidget()
        self._notif_muted.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self._muted_add = QtWidgets.QLineEdit()
        self._muted_add.setPlaceholderText("Module name")
        self._muted_add.setCompleter(QtWidgets.QCompleter(self._modules, self))
        self._muted_add.returnPressed.connect(self._add_muted)
        add = QtWidgets.QPushButton("Add")
        add.clicked.connect(self._add_muted)
        remove = QtWidgets.QPushButton("Remove selected")
        remove.clicked.connect(self._remove_muted)
        add_row = QtWidgets.QHBoxLayout()
        add_row.addWidget(self._muted_add)
        add_row.addWidget(add)
        muted = QtWidgets.QVBoxLayout()
        muted.addWidget(self._notif_muted)
        muted.addLayout(add_row)
        muted.addWidget(remove)
        form.addRow("Never notify for", muted)
        return tab

    def _add_muted(self) -> None:
        name = self._muted_add.text().strip()
        if name and name not in self._muted():
            self._notif_muted.addItem(name)
        self._muted_add.clear()

    def _remove_muted(self) -> None:
        for item in self._notif_muted.selectedItems():
            self._notif_muted.takeItem(self._notif_muted.row(item))

    def _muted(self) -> list[str]:
        return [self._notif_muted.item(i).text() for i in range(self._notif_muted.count())]

    # ── VFS tab ──────────────────────────────────────────────────────────────

    def _build_vfs_tab(self) -> QtWidgets.QWidget:
        tab = QtWidgets.QWidget()
        layout = QtWidgets.QHBoxLayout(tab)

        # left: the roots
        left = QtWidgets.QVBoxLayout()
        self._roots_list = QtWidgets.QListWidget()
        self._roots_list.currentRowChanged.connect(self._select_root)
        left.addWidget(self._roots_list)
        add = QtWidgets.QPushButton("Add root")
        add.clicked.connect(self._add_root)
        remove = QtWidgets.QPushButton("Remove root")
        remove.clicked.connect(self._remove_root)
        left.addWidget(add)
        left.addWidget(remove)
        layout.addLayout(left, 1)

        # right: the selected root
        self._root_form = QtWidgets.QWidget()
        form = QtWidgets.QFormLayout(self._root_form)
        self._root_name = QtWidgets.QLineEdit()
        self._root_name.setPlaceholderText("e.g. cache, as in /cache/image.fits")
        self._root_name.textEdited.connect(self._root_name_edited)
        form.addRow("Name", self._root_name)
        self._root_class = QtWidgets.QComboBox()
        self._root_class.setEditable(True)
        self._root_class.addItems(_VFS_CLASSES)
        form.addRow("Class", self._root_class)
        self._root_params = QtWidgets.QPlainTextEdit()
        self._root_params.setPlaceholderText("download: http://example.com/\ntoken: ...")
        form.addRow("Parameters (YAML)", self._root_params)
        note = QtWidgets.QLabel("Parameters, including tokens, are stored in clear text in the settings file.")
        note.setWordWrap(True)
        form.addRow(note)
        layout.addWidget(self._root_form, 2)
        return tab

    def _commit_form(self) -> None:
        """Store the form into the entry it is showing."""
        if 0 <= self._current < len(self._entries):
            entry = self._entries[self._current]
            entry.name = self._root_name.text().strip()
            entry.klass = self._root_class.currentText().strip()
            entry.params = self._root_params.toPlainText()

    def _show_entry(self, row: int) -> None:
        self._current = row
        self._root_form.setEnabled(row >= 0)
        if row < 0:
            self._root_name.clear()
            self._root_params.clear()
            return
        entry = self._entries[row]
        self._root_name.setText(entry.name)
        self._root_class.setCurrentText(entry.klass)
        self._root_params.setPlainText(entry.params)

    def _select_root(self, row: int) -> None:
        # the row has already changed, _current still is the one that was shown
        self._commit_form()
        self._show_entry(row)

    def _root_name_edited(self, text: str) -> None:
        item = self._roots_list.currentItem()
        if item is not None:
            item.setText(text.strip() or "(unnamed)")

    def _add_root(self) -> None:
        self._commit_form()
        self._entries.append(_RootEntry("", _VFS_CLASSES[0], ""))
        self._roots_list.addItem("(unnamed)")
        self._roots_list.setCurrentRow(len(self._entries) - 1)

    def _remove_root(self) -> None:
        row = self._roots_list.currentRow()
        if row < 0:
            return
        self._current = -1  # the entry is going away, don't commit the form into the next one
        del self._entries[row]
        self._roots_list.takeItem(row)
        self._show_entry(self._roots_list.currentRow())

    # ── load / collect ───────────────────────────────────────────────────────

    def _load(self, settings: GuiSettings) -> None:
        n = settings.notifications
        self._notif_enabled.setChecked(n.enabled)
        self._notif_level.setCurrentText(n.min_log_level)
        self._notif_inactive.setChecked(n.only_when_inactive)
        self._notif_rate.setValue(n.rate_limit)
        self._notif_muted.addItems(n.muted_modules)

        for name, config in settings.vfs.roots.items():
            params = {k: v for k, v in config.items() if k != "class"}
            text = yaml.safe_dump(params, default_flow_style=False, sort_keys=False).strip() if params else ""
            self._entries.append(_RootEntry(name, config["class"], text))
            self._roots_list.addItem(name)
        self._show_entry(-1)
        if self._entries:
            self._roots_list.setCurrentRow(0)

    def collect(self) -> GuiSettings:
        """The settings as currently entered.

        Raises:
            ValueError: Something entered is invalid, the message says what.
        """
        self._commit_form()
        notifications = NotificationSettings(
            enabled=self._notif_enabled.isChecked(),
            min_log_level=self._notif_level.currentText(),  # type: ignore[arg-type]
            only_when_inactive=self._notif_inactive.isChecked(),
            muted_modules=self._muted(),
            rate_limit=self._notif_rate.value(),
        )

        roots: dict[str, dict[str, Any]] = {}
        for entry in self._entries:
            if not entry.name:
                raise ValueError("A VFS root has no name.")
            if entry.name in roots:
                raise ValueError(f"VFS root '{entry.name}' exists more than once.")
            try:
                params = yaml.safe_load(entry.params) if entry.params.strip() else {}
            except yaml.YAMLError as e:
                raise ValueError(f"Parameters of VFS root '{entry.name}' are not valid YAML: {e}") from e
            if not isinstance(params, dict):
                raise ValueError(f"Parameters of VFS root '{entry.name}' must be 'key: value' lines.")
            if "class" in params:
                raise ValueError(f"VFS root '{entry.name}': set the class in the Class box, not in the parameters.")
            if not entry.klass:
                raise ValueError(f"VFS root '{entry.name}' has no class.")
            try:
                get_class_from_string(entry.klass)
            except Exception as e:
                raise ValueError(f"VFS root '{entry.name}': class '{entry.klass}' cannot be loaded: {e}") from e
            roots[entry.name] = {"class": entry.klass, **params}

        try:
            return GuiSettings(notifications=notifications, vfs=VfsSettings(roots=roots))
        except ValidationError as e:
            raise ValueError(str(e)) from e

    # ── buttons ──────────────────────────────────────────────────────────────

    def _show_error(self, message: str) -> None:
        self._error.setText(message)
        self._error.setVisible(bool(message))

    def _apply(self) -> bool:
        try:
            settings = self.collect()
            self._on_apply(settings)
        except Exception as e:
            if not isinstance(e, ValueError):
                log.exception("Could not apply settings.")
            self._show_error(str(e))
            return False
        self._show_error("")
        return True

    def _ok(self) -> None:
        if self._apply():
            self.accept()


__all__ = ["SettingsDialog"]
