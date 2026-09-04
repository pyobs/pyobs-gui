import dataclasses
import logging
from typing import Any, Callable, Dict, List, Optional, cast

from PySide6 import QtCore, QtWidgets  # type: ignore

from pyobs.interfaces import ConfigAppliedState, ConfigFieldSchema, ConfigSchema, IStructuredConfig
from pyobs.interfaces.IStructuredConfig import ConfigValue
from pyobs.utils.enums import AccessLevel
from .base import BaseWidget

log = logging.getLogger(__name__)


@dataclasses.dataclass
class _FieldEditor:
    """One schema field's editor: the widget shown to the user, plus get/set callables that
    translate between it and the ConfigValue on the wire.

    `children` holds the sub-editors of an `object`-with-`nested` field -- its own get_value/
    set_value recurse into them instead of touching `widget` directly. An opaque field (no
    schema to render) has no editor to speak of: get_value/set_value are a plain passthrough of
    the last raw value it was given, so a field we can't edit still round-trips unchanged
    through Apply instead of being silently dropped or nulled out.
    """

    widget: QtWidgets.QWidget
    get_value: Callable[[], ConfigValue]
    set_value: Callable[[ConfigValue], None]
    children: Optional[Dict[str, "_FieldEditor"]] = None
    level: AccessLevel = AccessLevel.BASIC
    # the row's label, so the basic/expert toggle can hide it alongside `display_widget` --
    # addRow(str, widget) auto-creates one, but we build it explicitly at each row-adding call
    # site instead so we have a handle on it (QFormLayout.labelForField exists but is keyed
    # per-layout-instance, awkward to thread through recursion; a direct reference is simpler)
    row_label: Optional[QtWidgets.QLabel] = None
    # set only when the field has a description: a small container with `widget` on top and the
    # description label below it. `widget` itself (get_value/set_value's target) never changes
    # shape, so a description doesn't affect how values round-trip -- only what goes in the row.
    row_widget: Optional[QtWidgets.QWidget] = None

    @property
    def display_widget(self) -> QtWidgets.QWidget:
        return self.row_widget if self.row_widget is not None else self.widget


def _collect_by_level(editor: "_FieldEditor", level: AccessLevel) -> List["_FieldEditor"]:
    """Recursively gather every editor (including nested-object children) tagged at exactly the
    given level, for the basic/expert toggle to show/hide as a group."""
    editors = [editor] if editor.level == level else []
    for child in (editor.children or {}).values():
        editors.extend(_collect_by_level(child, level))
    return editors


def _wrap_with_description(widget: QtWidgets.QWidget, description: Optional[str]) -> Optional[QtWidgets.QWidget]:
    """Stack `widget` over a dimmed, word-wrapped description label, for the field's row to show
    the description below the input rather than only as e.g. a tooltip. Returns None (meaning:
    just use `widget` directly, no wrapping) when there's no description."""
    if not description:
        return None
    container = QtWidgets.QWidget()
    layout = QtWidgets.QVBoxLayout(container)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(2)
    layout.addWidget(widget)
    description_label = QtWidgets.QLabel(description)
    description_label.setWordWrap(True)
    # palette(mid) is a 3D-effect shade (borders/shadows), too dark to read comfortably as text;
    # placeholder-text is Qt's actual semantic role for secondary-but-legible text
    description_label.setStyleSheet("color: palette(placeholder-text);")
    layout.addWidget(description_label)
    return container


def _nested_get(children: Dict[str, _FieldEditor]) -> Dict[str, ConfigValue]:
    return {name: child.get_value() for name, child in children.items()}


def _nested_set(children: Dict[str, _FieldEditor], value: ConfigValue) -> None:
    if not isinstance(value, dict):
        return
    for name, child in children.items():
        if name in value:
            child.set_value(value[name])


def _build_editor(name: str, schema: ConfigFieldSchema, on_change: Callable[[], None]) -> _FieldEditor:
    """Build one field's editor from its schema (recursively, for a nested object)."""

    if schema.type == "str":
        line_edit = QtWidgets.QLineEdit()
        if schema.default is not None:
            line_edit.setText(str(schema.default))
        line_edit.textChanged.connect(lambda _: on_change())
        return _FieldEditor(
            line_edit,
            line_edit.text,
            lambda value: line_edit.setText(str(value)),
            level=schema.level,
            row_widget=_wrap_with_description(line_edit, schema.description),
        )

    if schema.type == "int":
        spin_box = QtWidgets.QSpinBox()
        spin_box.setRange(-2_147_483_647, 2_147_483_647)
        if schema.default is not None:
            spin_box.setValue(int(schema.default))
        spin_box.valueChanged.connect(lambda _: on_change())
        return _FieldEditor(
            spin_box,
            spin_box.value,
            lambda value: spin_box.setValue(int(cast("int", value))),
            level=schema.level,
            row_widget=_wrap_with_description(spin_box, schema.description),
        )

    if schema.type == "float":
        double_spin_box = QtWidgets.QDoubleSpinBox()
        double_spin_box.setRange(-1e12, 1e12)
        double_spin_box.setDecimals(6)
        if schema.unit is not None:
            double_spin_box.setSuffix(f" {schema.unit.value}")
        if schema.default is not None:
            double_spin_box.setValue(float(schema.default))
        double_spin_box.valueChanged.connect(lambda _: on_change())
        return _FieldEditor(
            double_spin_box,
            double_spin_box.value,
            lambda value: double_spin_box.setValue(float(cast("float", value))),
            level=schema.level,
            row_widget=_wrap_with_description(double_spin_box, schema.description),
        )

    if schema.type == "bool":
        check_box = QtWidgets.QCheckBox()
        if schema.default is not None:
            check_box.setChecked(bool(schema.default))
        check_box.toggled.connect(lambda _: on_change())
        return _FieldEditor(
            check_box,
            check_box.isChecked,
            lambda value: check_box.setChecked(bool(value)),
            level=schema.level,
            row_widget=_wrap_with_description(check_box, schema.description),
        )

    if schema.type == "enum":
        combo_box = QtWidgets.QComboBox()
        options = schema.options or []
        combo_box.addItems(options)
        if schema.default is not None and str(schema.default) in options:
            combo_box.setCurrentText(str(schema.default))
        combo_box.currentTextChanged.connect(lambda _: on_change())
        return _FieldEditor(
            combo_box,
            combo_box.currentText,
            lambda value: combo_box.setCurrentText(str(value)),
            level=schema.level,
            row_widget=_wrap_with_description(combo_box, schema.description),
        )

    if schema.type == "object" and schema.nested is not None:
        group_box = QtWidgets.QGroupBox(name)
        form_layout = QtWidgets.QFormLayout()
        group_box.setLayout(form_layout)
        children: Dict[str, _FieldEditor] = {}
        for child_name, child_schema in schema.nested.items():
            if child_schema.level == AccessLevel.HIDDEN:
                continue
            child_editor = _build_editor(child_name, child_schema, on_change)
            child_label = QtWidgets.QLabel(child_name)
            form_layout.addRow(child_label, child_editor.display_widget)
            child_editor.row_label = child_label
            children[child_name] = child_editor
        return _FieldEditor(
            group_box,
            lambda: _nested_get(children),
            lambda value: _nested_set(children, value),
            children=children,
            level=schema.level,
            row_widget=_wrap_with_description(group_box, schema.description),
        )

    # object without a nested schema (pydantic freeform dict), or any other schema type this
    # widget doesn't know how to render: a loud, visible placeholder rather than guessing --
    # mirrors config_schema.py's own loud-failure philosophy. Still round-trips whatever raw
    # value it was last given (see _FieldEditor docstring), it's just not editable here.
    raw_value: list[ConfigValue] = [cast("ConfigValue", schema.default)]

    def _get_raw() -> ConfigValue:
        return raw_value[0]

    def _set_raw(value: ConfigValue) -> None:
        raw_value[0] = value

    placeholder = QtWidgets.QLineEdit("(not editable here)")
    placeholder.setReadOnly(True)
    placeholder.setEnabled(False)
    placeholder.setToolTip(f"Field type {schema.type!r} has no schema-driven editor for this widget.")
    # always BASIC regardless of schema.level: this is a loud "unsupported type" flag, meant to
    # stay visible so a developer notices it, never swept into the expert-toggle's hide group
    return _FieldEditor(
        placeholder, _get_raw, _set_raw, row_widget=_wrap_with_description(placeholder, schema.description)
    )


class StructuredConfigWidget(BaseWidget):
    """Generic form for any module implementing IStructuredConfig, auto-built from its
    ConfigSchema -- see specs/plans/2026-08-28-structuredconfig-widget.md (pyobs-core repo) for
    the design this follows. No widget code per module: the field-type -> editor mapping in
    _build_editor() covers str/int/float/bool/enum plus arbitrarily nested objects.
    """

    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)

        self._schema: Optional[ConfigSchema] = None
        self._root: Optional[_FieldEditor] = None
        self._last_applied: Optional[Dict[str, ConfigValue]] = None
        # true while editors are being populated from a just-received state, so that doesn't
        # itself register as a user edit (which would otherwise re-enable Apply/Reset for a
        # change that came from the module, not from the operator)
        self._applying_state = False
        # every EXPERT-level editor across the whole (possibly nested) form, collected once in
        # _build_form; their rows (label + widget) are shown/hidden together by checkBoxAdvanced.
        # No password gate, unlike pyftscontrol's Expert Mode button -- operators here are
        # already authenticated via the comm layer, so it's just a visibility toggle, not access
        # control.
        self._expert_editors: List[_FieldEditor] = []

        outer_layout = QtWidgets.QVBoxLayout()
        self.setLayout(outer_layout)

        self.checkBoxAdvanced = QtWidgets.QCheckBox("Show advanced fields")
        self.checkBoxAdvanced.toggled.connect(self._on_advanced_toggled)
        outer_layout.addWidget(self.checkBoxAdvanced)

        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        self._form_container = QtWidgets.QWidget()
        self._form_layout = QtWidgets.QFormLayout()
        self._form_container.setLayout(self._form_layout)
        scroll_area.setWidget(self._form_container)
        outer_layout.addWidget(scroll_area)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        self.buttonReset = QtWidgets.QPushButton("Reset")
        self.buttonApply = QtWidgets.QPushButton("Apply")
        self.colorize_button(self.buttonApply, QtCore.Qt.GlobalColor.green)
        button_layout.addWidget(self.buttonReset)
        button_layout.addWidget(self.buttonApply)
        outer_layout.addLayout(button_layout)

        self.buttonApply.setEnabled(False)
        self.buttonReset.setEnabled(False)
        self.buttonApply.clicked.connect(self.apply_clicked)
        self.buttonReset.clicked.connect(self.reset_clicked)

        self.signal_update_gui.connect(self.update_gui)

    async def _init(self) -> None:
        await self._init_once("permitted", self._fetch_permitted_methods)
        await self._init_once("schema", self._init_schema)
        await self._init_once("state", self._subscribe_state)

    async def _init_schema(self) -> None:
        self._schema = await self.comm.get_capabilities(self.module, IStructuredConfig)
        if self._schema is not None:
            self._build_form(self._schema)

    async def _subscribe_state(self) -> None:
        await self.comm.subscribe_state(self.module, IStructuredConfig, self._on_state)

    def _build_form(self, schema: ConfigSchema) -> None:
        children: Dict[str, _FieldEditor] = {}
        for name, field_schema in schema.fields.items():
            if field_schema.level == AccessLevel.HIDDEN:
                continue
            editor = _build_editor(name, field_schema, self._on_editor_changed)
            label = QtWidgets.QLabel(name)
            self._form_layout.addRow(label, editor.display_widget)
            editor.row_label = label
            children[name] = editor
        self._root = _FieldEditor(
            self._form_container,
            lambda: _nested_get(children),
            lambda value: _nested_set(children, value),
            children=children,
        )
        self._expert_editors = _collect_by_level(self._root, AccessLevel.EXPERT)
        self._on_advanced_toggled(self.checkBoxAdvanced.isChecked())
        # a state may already have arrived (and been cached) before the form existed to receive
        # it -- apply it now instead of waiting for the next update
        if self._last_applied is not None:
            self.signal_update_gui.emit()

    def _on_advanced_toggled(self, checked: bool) -> None:
        for editor in self._expert_editors:
            editor.display_widget.setVisible(checked)
            if editor.row_label is not None:
                editor.row_label.setVisible(checked)

    def _on_state(self, state: ConfigAppliedState) -> None:
        self._last_applied = dict(state.config)
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.setEnabled(True)
        if self._root is not None and self._last_applied is not None:
            self._applying_state = True
            try:
                self._root.set_value(self._last_applied)
            finally:
                self._applying_state = False
        self._update_buttons()

    def _on_editor_changed(self) -> None:
        if not self._applying_state:
            self._update_buttons()

    def _is_dirty(self) -> bool:
        if self._root is None or self._last_applied is None:
            return False
        return self._root.get_value() != self._last_applied

    def _update_buttons(self) -> None:
        dirty = self._is_dirty()
        self.buttonApply.setEnabled(dirty and self.permitted("set_config"))
        self.buttonReset.setEnabled(dirty)

    @QtCore.Slot()  # type: ignore
    def apply_clicked(self) -> None:
        if self._root is None:
            return
        payload = _nested_get(self._root.children or {})
        self.run_background(self._apply_config, payload, disable=[self.buttonApply, self.buttonReset])

    async def _apply_config(self, payload: Dict[str, ConfigValue]) -> None:
        async with self.comm.proxy(self.module, IStructuredConfig) as proxy:
            await proxy.set_config(payload)

    @QtCore.Slot()  # type: ignore
    def reset_clicked(self) -> None:
        self.update_gui()


__all__ = ["StructuredConfigWidget"]
