from unittest.mock import AsyncMock, patch

import pytest
from PySide6 import QtWidgets  # type: ignore

from pyobs.interfaces import ConfigAppliedState, ConfigFieldSchema, ConfigSchema
from pyobs.utils import exceptions as exc
from pyobs.utils.enums import AccessLevel, Unit
from pyobs_gui.structuredconfigwidget import StructuredConfigWidget, _build_editor, _nested_get

# -- shared fixtures -----------------------------------------------------------------------


def _sample_schema() -> ConfigSchema:
    return ConfigSchema(
        fields={
            "name": ConfigFieldSchema(type="str", default="foo"),
            "count": ConfigFieldSchema(type="int", default=3),
            "distance": ConfigFieldSchema(type="float", unit=Unit.ARCSEC, default=1.5),
            "enabled": ConfigFieldSchema(type="bool", default=True),
            "mode": ConfigFieldSchema(type="enum", options=["track", "park"], default="track"),
            "pointing": ConfigFieldSchema(
                type="object",
                nested={
                    "az": ConfigFieldSchema(type="float", default=0.0),
                    "alt": ConfigFieldSchema(type="float", default=90.0),
                },
            ),
            "extra": ConfigFieldSchema(type="object", nested=None, default={"raw": 1}),
        }
    )


def _sample_config() -> dict:
    return {
        "name": "bar",
        "count": 5,
        "distance": 2.5,
        "enabled": False,
        "mode": "park",
        "pointing": {"az": 10.0, "alt": 45.0},
        "extra": {"raw": 2},
    }


class _AsyncProxyCM:
    """Mimics Comm.proxy()'s async context manager, yielding a fixed proxy."""

    def __init__(self, value):
        self._value = value

    async def __aenter__(self):
        return self._value

    async def __aexit__(self, *exc_info):
        return False


class FakeComm:
    """Only implements what StructuredConfigWidget.apply_clicked()/_apply_config() touch."""

    def __init__(self, proxy_obj=None):
        self._proxy_obj = proxy_obj

    def proxy(self, module, interface):
        return _AsyncProxyCM(self._proxy_obj)


def make_widget() -> StructuredConfigWidget:
    widget = StructuredConfigWidget()
    widget.modules = ["module"]
    widget._build_form(_sample_schema())
    return widget


# -- _build_editor: schema type -> Qt editor mapping ----------------------------------------


def test_str_field_maps_to_line_edit() -> None:
    editor = _build_editor("name", ConfigFieldSchema(type="str", default="foo"), lambda: None)
    assert isinstance(editor.widget, QtWidgets.QLineEdit)
    assert editor.get_value() == "foo"
    editor.set_value("bar")
    assert editor.get_value() == "bar"


def test_int_field_maps_to_spin_box() -> None:
    editor = _build_editor("count", ConfigFieldSchema(type="int", default=3), lambda: None)
    assert isinstance(editor.widget, QtWidgets.QSpinBox)
    assert editor.get_value() == 3
    editor.set_value(7)
    assert editor.get_value() == 7


def test_float_field_maps_to_double_spin_box_with_unit_suffix() -> None:
    editor = _build_editor("distance", ConfigFieldSchema(type="float", unit=Unit.ARCSEC, default=1.5), lambda: None)
    assert isinstance(editor.widget, QtWidgets.QDoubleSpinBox)
    assert editor.widget.suffix() == " arcsec"
    assert editor.get_value() == 1.5


def test_bool_field_maps_to_check_box() -> None:
    editor = _build_editor("enabled", ConfigFieldSchema(type="bool", default=True), lambda: None)
    assert isinstance(editor.widget, QtWidgets.QCheckBox)
    assert editor.get_value() is True
    editor.set_value(False)
    assert editor.get_value() is False


def test_enum_field_maps_to_combo_box_with_options_and_default() -> None:
    schema = ConfigFieldSchema(type="enum", options=["track", "park", "slew"], default="park")
    editor = _build_editor("mode", schema, lambda: None)
    assert isinstance(editor.widget, QtWidgets.QComboBox)
    assert [editor.widget.itemText(i) for i in range(editor.widget.count())] == ["track", "park", "slew"]
    assert editor.get_value() == "park"


def test_nested_object_field_recurses_into_group_box() -> None:
    schema = ConfigFieldSchema(
        type="object",
        nested={
            "az": ConfigFieldSchema(type="float", default=1.0),
            "alt": ConfigFieldSchema(type="float", default=2.0),
        },
    )
    editor = _build_editor("pointing", schema, lambda: None)
    assert isinstance(editor.widget, QtWidgets.QGroupBox)
    assert editor.children is not None and set(editor.children) == {"az", "alt"}
    assert editor.get_value() == {"az": 1.0, "alt": 2.0}
    editor.set_value({"az": 5.0, "alt": 6.0})
    assert editor.get_value() == {"az": 5.0, "alt": 6.0}


def test_object_without_nested_schema_is_a_disabled_passthrough_placeholder() -> None:
    """No schema to render for a freeform/opaque object field -- flag it rather than guess
    (mirrors config_schema.py's loud-failure philosophy), but still round-trip whatever raw
    value it was last given so Apply never silently drops or nulls it out."""
    editor = _build_editor("extra", ConfigFieldSchema(type="object", nested=None, default={"raw": 1}), lambda: None)
    assert isinstance(editor.widget, QtWidgets.QLineEdit)
    assert editor.widget.isEnabled() is False
    assert editor.get_value() == {"raw": 1}
    editor.set_value({"raw": 99})
    assert editor.get_value() == {"raw": 99}


def test_unsupported_field_type_is_also_a_disabled_placeholder() -> None:
    """A schema type this widget doesn't know (e.g. a future list type) falls into the same
    loud placeholder as an opaque object, rather than crashing or silently misrendering."""
    editor = _build_editor("items", ConfigFieldSchema(type="list", default=[1, 2]), lambda: None)
    assert isinstance(editor.widget, QtWidgets.QLineEdit)
    assert editor.widget.isEnabled() is False
    assert editor.get_value() == [1, 2]


# -- _build_editor / _build_form: basic/expert level ----------------------------------------


def test_basic_field_starts_enabled() -> None:
    editor = _build_editor("count", ConfigFieldSchema(type="int", default=3, level=AccessLevel.BASIC), lambda: None)
    assert editor.widget.isEnabled() is True
    assert editor.level == AccessLevel.BASIC


def test_expert_field_starts_disabled() -> None:
    editor = _build_editor("count", ConfigFieldSchema(type="int", default=3, level=AccessLevel.EXPERT), lambda: None)
    assert editor.widget.isEnabled() is False
    assert editor.level == AccessLevel.EXPERT


def test_unsupported_type_placeholder_ignores_expert_level_for_toggle_grouping() -> None:
    """A permanently non-editable placeholder must never be swept into the expert-toggle's
    re-enable group, even if the underlying field is tagged EXPERT -- see the comment in
    _build_editor's fallback branch."""
    editor = _build_editor(
        "items", ConfigFieldSchema(type="list", default=[1, 2], level=AccessLevel.EXPERT), lambda: None
    )
    assert editor.level == AccessLevel.BASIC
    assert editor.widget.isEnabled() is False


def test_nested_object_skips_hidden_children_and_disables_whole_group_when_expert() -> None:
    schema = ConfigFieldSchema(
        type="object",
        level=AccessLevel.EXPERT,
        nested={
            "az": ConfigFieldSchema(type="float", default=1.0),
            "secret": ConfigFieldSchema(type="float", default=2.0, level=AccessLevel.HIDDEN),
        },
    )
    editor = _build_editor("pointing", schema, lambda: None)
    assert editor.children is not None and set(editor.children) == {"az"}
    assert editor.widget.isEnabled() is False


def _sample_schema_with_levels() -> ConfigSchema:
    return ConfigSchema(
        fields={
            "name": ConfigFieldSchema(type="str", default="foo", level=AccessLevel.BASIC),
            "gain": ConfigFieldSchema(type="int", default=1, level=AccessLevel.EXPERT),
            "secret": ConfigFieldSchema(type="int", default=0, level=AccessLevel.HIDDEN),
        }
    )


def test_build_form_skips_hidden_fields_entirely() -> None:
    widget = StructuredConfigWidget()
    widget._build_form(_sample_schema_with_levels())

    assert widget._form_layout.rowCount() == 2  # name + gain, not secret
    assert widget._root is not None and widget._root.children is not None
    assert set(widget._root.children) == {"name", "gain"}
    widget.close()


def test_advanced_checkbox_toggles_expert_fields_enabled() -> None:
    widget = StructuredConfigWidget()
    widget._build_form(_sample_schema_with_levels())
    assert widget._root is not None and widget._root.children is not None
    expert_widget = widget._root.children["gain"].widget

    assert expert_widget.isEnabled() is False  # starts locked

    widget.checkBoxAdvanced.setChecked(True)
    assert expert_widget.isEnabled() is True

    widget.checkBoxAdvanced.setChecked(False)
    assert expert_widget.isEnabled() is False
    widget.close()


# -- StructuredConfigWidget: state population, dirty tracking, apply/reset ------------------


def test_build_form_adds_one_row_per_field() -> None:
    widget = make_widget()
    assert widget._form_layout.rowCount() == len(_sample_schema().fields)
    widget.close()


def test_state_populates_editors_and_widget_is_not_dirty() -> None:
    widget = make_widget()

    widget._on_state(ConfigAppliedState(config=_sample_config()))

    assert widget._is_dirty() is False
    assert widget.buttonApply.isEnabled() is False
    assert widget.buttonReset.isEnabled() is False
    widget.close()


def test_editing_a_field_marks_widget_dirty_and_enables_buttons() -> None:
    widget = make_widget()
    widget._on_state(ConfigAppliedState(config=_sample_config()))
    assert widget._root is not None and widget._root.children is not None

    widget._root.children["count"].set_value(42)
    widget._on_editor_changed()

    assert widget._is_dirty() is True
    assert widget.buttonApply.isEnabled() is True
    assert widget.buttonReset.isEnabled() is True
    widget.close()


def test_apply_disabled_when_dirty_but_not_permitted() -> None:
    widget = make_widget()
    widget._on_state(ConfigAppliedState(config=_sample_config()))
    widget._permitted_methods = set()  # nothing permitted
    assert widget._root is not None and widget._root.children is not None

    widget._root.children["count"].set_value(42)
    widget._on_editor_changed()

    assert widget.buttonApply.isEnabled() is False
    assert widget.buttonReset.isEnabled() is True
    widget.close()


def test_reset_restores_last_applied_values() -> None:
    widget = make_widget()
    config = _sample_config()
    widget._on_state(ConfigAppliedState(config=config))
    assert widget._root is not None and widget._root.children is not None

    widget._root.children["count"].set_value(999)
    widget._on_editor_changed()
    assert widget._is_dirty() is True

    widget.reset_clicked()

    assert widget._is_dirty() is False
    assert _nested_get(widget._root.children) == config
    assert widget.buttonApply.isEnabled() is False
    assert widget.buttonReset.isEnabled() is False
    widget.close()


@pytest.mark.asyncio
async def test_apply_sends_assembled_payload(qapp) -> None:
    widget = make_widget()
    widget._on_state(ConfigAppliedState(config=_sample_config()))
    assert widget._root is not None and widget._root.children is not None
    widget._root.children["count"].set_value(42)

    set_config = AsyncMock()
    widget._comm = FakeComm(proxy_obj=AsyncMock(set_config=set_config))  # pyrefly: ignore [bad-assignment]

    expected = _sample_config()
    expected["count"] = 42
    await widget._apply_config(_nested_get(widget._root.children))

    set_config.assert_awaited_once_with(expected)
    widget.close()


@pytest.mark.asyncio
async def test_apply_failure_surfaces_through_show_remote_error(qapp) -> None:
    widget = make_widget()
    widget._on_state(ConfigAppliedState(config=_sample_config()))
    assert widget._root is not None and widget._root.children is not None

    set_config = AsyncMock(side_effect=exc.RemoteError("module unreachable"))
    widget._comm = FakeComm(proxy_obj=AsyncMock(set_config=set_config))  # pyrefly: ignore [bad-assignment]

    with patch("pyobs_gui.base.show_remote_error", new_callable=AsyncMock) as mock_show_error:
        await widget._background_task(widget._apply_config, _nested_get(widget._root.children))

    mock_show_error.assert_awaited_once()
    widget.close()
