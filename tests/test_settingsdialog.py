import asyncio
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pydantic import BaseModel
from pyobs.comm.local import LocalComm

from pyobs_gui.gui import GUI
from pyobs_gui.mainwindow import MainWindow
from pyobs_gui.settings import GuiSettings, NotificationSettings, SettingsStore, VfsSettings
from pyobs_gui.notifier import NotifierError
from pyobs_gui.settingsdialog import SettingsDialog

ROOTS = {
    "webcam": {"class": "pyobs.vfs.HttpFile", "download": "http://localhost:37077/", "token": "secret"},
    "cache": {"class": "pyobs.vfs.LocalFile", "root": "/tmp/pyobs-test/"},
}


def _dialog(
    settings: GuiSettings | None = None, on_apply: Any = None, modules: list[str] | None = None
) -> SettingsDialog:
    return SettingsDialog(settings or GuiSettings(), modules or [], on_apply or MagicMock())


def _leaves(model: type[BaseModel], prefix: str = "") -> list[str]:
    paths: list[str] = []
    for name, field in model.model_fields.items():
        sub = field.annotation
        if isinstance(sub, type) and issubclass(sub, BaseModel):
            paths.extend(_leaves(sub, f"{prefix}{name}."))
        else:
            paths.append(f"{prefix}{name}")
    return paths


# ── schema coverage ───────────────────────────────────────────────────────


def test_every_setting_has_a_widget_in_the_dialog() -> None:
    assert sorted(SettingsDialog.FIELD_WIDGETS) == sorted(_leaves(GuiSettings))
    dialog = _dialog()
    for attribute in SettingsDialog.FIELD_WIDGETS.values():
        assert hasattr(dialog, attribute), attribute


# ── load / collect ────────────────────────────────────────────────────────


def test_round_trip() -> None:
    settings = GuiSettings(
        notifications=NotificationSettings(
            enabled=False, min_log_level="CRITICAL", only_when_inactive=False, muted_modules=["weather"], rate_limit=2.5
        ),
        vfs=VfsSettings(roots=ROOTS),
    )
    assert _dialog(settings).collect() == settings


def test_defaults_round_trip() -> None:
    assert _dialog().collect() == GuiSettings()


def test_editing_roots_through_the_form() -> None:
    dialog = _dialog(GuiSettings(vfs=VfsSettings(roots=ROOTS)))

    # change the first root, add a second one, go back: nothing may be lost on the way
    dialog._roots_list.setCurrentRow(0)
    dialog._root_params.setPlainText("download: http://other/\n")
    dialog._add_root()
    dialog._root_name.setText("new")
    dialog._root_name_edited("new")
    dialog._root_class.setCurrentText("pyobs.vfs.LocalFile")
    dialog._root_params.setPlainText("root: /data/")
    dialog._roots_list.setCurrentRow(0)

    roots = dialog.collect().vfs.roots
    assert roots["webcam"] == {"class": "pyobs.vfs.HttpFile", "download": "http://other/"}
    assert roots["cache"] == ROOTS["cache"]
    assert roots["new"] == {"class": "pyobs.vfs.LocalFile", "root": "/data/"}


def test_removing_a_root() -> None:
    dialog = _dialog(GuiSettings(vfs=VfsSettings(roots=ROOTS)))
    dialog._roots_list.setCurrentRow(0)
    dialog._remove_root()
    assert list(dialog.collect().vfs.roots) == ["cache"]
    dialog._remove_root()
    dialog._remove_root()  # nothing selected any more
    assert dialog.collect().vfs.roots == {}


def test_muted_modules() -> None:
    dialog = _dialog(GuiSettings(notifications=NotificationSettings(muted_modules=["a"])), modules=["a", "b"])
    for name in ["b", "a", "  c  ", ""]:
        dialog._muted_add.setText(name)
        dialog._add_muted()
    assert dialog.collect().notifications.muted_modules == ["a", "b", "c"]

    dialog._notif_muted.item(0).setSelected(True)
    dialog._remove_muted()
    assert dialog.collect().notifications.muted_modules == ["b", "c"]


@pytest.mark.parametrize(
    "name, klass, params, message",
    [
        ("", "pyobs.vfs.HttpFile", "", "no name"),
        ("a/b", "pyobs.vfs.HttpFile", "", "no '/'"),
        ("a", "", "", "no class"),
        ("a", "pyobs.vfs.DoesNotExist", "", "cannot be loaded"),
        ("a", "pyobs.vfs.HttpFile", "key: [unclosed", "not valid YAML"),
        ("a", "pyobs.vfs.HttpFile", "- just\n- a list", "key: value"),
        ("a", "pyobs.vfs.HttpFile", "class: pyobs.vfs.LocalFile", "Class box"),
    ],
)
def test_invalid_root_is_reported(name: str, klass: str, params: str, message: str) -> None:
    dialog = _dialog()
    dialog._add_root()
    dialog._root_name.setText(name)
    dialog._root_class.setCurrentText(klass)
    dialog._root_params.setPlainText(params)
    with pytest.raises(ValueError, match=message):
        dialog.collect()


def test_duplicate_root_names_are_reported() -> None:
    dialog = _dialog(GuiSettings(vfs=VfsSettings(roots=ROOTS)))
    dialog._roots_list.setCurrentRow(1)
    dialog._root_name.setText("webcam")
    with pytest.raises(ValueError, match="more than once"):
        dialog.collect()


# ── buttons ───────────────────────────────────────────────────────────────


def test_apply_hands_over_the_settings_and_keeps_the_dialog_open() -> None:
    on_apply = MagicMock()
    dialog = _dialog(on_apply=on_apply)
    dialog._notif_enabled.setChecked(False)
    assert dialog._apply() is True
    on_apply.assert_called_once()
    assert on_apply.call_args.args[0].notifications.enabled is False
    assert dialog._error.isHidden()


def test_ok_closes_only_when_applying_worked() -> None:
    dialog = _dialog(on_apply=MagicMock(side_effect=RuntimeError("disk full")))
    dialog.show()
    dialog._ok()
    assert dialog.isVisible()
    assert "disk full" in dialog._error.text()

    dialog._on_apply = MagicMock()
    dialog._ok()
    assert not dialog.isVisible()


def test_invalid_input_is_shown_and_not_handed_over() -> None:
    on_apply = MagicMock()
    dialog = _dialog(on_apply=on_apply)
    dialog._add_root()  # unnamed
    assert dialog._apply() is False
    on_apply.assert_not_called()
    assert "no name" in dialog._error.text()


# ── standalone only ───────────────────────────────────────────────────────


def test_settings_button_only_with_a_handler() -> None:
    plain = MainWindow(show_shell=False, show_events=False, show_status=False)
    assert not hasattr(plain, "buttonSettings")

    handler = MagicMock()
    window = MainWindow(show_shell=False, show_events=False, show_status=False, on_settings=handler)
    window.buttonSettings.click()
    handler.assert_called_once()


def _gui(monkeypatch: pytest.MonkeyPatch, store: SettingsStore, **kwargs: Any) -> GUI:
    monkeypatch.setattr("pyobs_gui.gui.SettingsStore", lambda: store)
    gui = GUI(comm=LocalComm(name="gui"), **kwargs)
    return gui


def test_yaml_gui_has_no_settings_store(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    gui = _gui(monkeypatch, SettingsStore(tmp_path / "s.yaml"), notifications={"enabled": False})
    assert gui._store is None
    assert gui.settings.notifications.enabled is False
    with pytest.raises(RuntimeError, match="standalone"):
        gui.apply_settings(GuiSettings())


def test_standalone_gui_loads_saves_and_applies(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    store = SettingsStore(tmp_path / "s.yaml")
    store.set("acc", GuiSettings(notifications=NotificationSettings(enabled=False)))
    gui = _gui(monkeypatch, store, standalone=True, settings_key="acc")
    assert gui.settings.notifications.enabled is False

    spy = MagicMock(wraps=gui.vfs.set_roots)
    monkeypatch.setattr(gui.vfs, "set_roots", spy)
    emitted = MagicMock()
    from pyobs_gui.guisignals import gui_signals

    gui_signals.settings_changed.connect(emitted)
    try:
        new = GuiSettings(vfs=VfsSettings(roots=ROOTS))
        gui.apply_settings(new)
    finally:
        gui_signals.settings_changed.disconnect(emitted)

    assert store.get("acc") == new
    assert gui.settings == new
    spy.assert_called_once_with(ROOTS)
    assert gui.vfs.open_file("/cache/x", "r") is not None  # the root is really in effect
    emitted.assert_called_once()


def test_standalone_gui_starts_with_defaults_if_the_file_is_unreadable(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    path = tmp_path / "s.yaml"
    path.write_text("accounts: [unclosed")
    gui = _gui(monkeypatch, SettingsStore(path), standalone=True, settings_key="acc")
    assert gui.settings == GuiSettings()
    assert path.read_text() == "accounts: [unclosed"


# ── test notification ─────────────────────────────────────────────────────


async def _settle() -> None:
    for _ in range(5):
        await asyncio.sleep(0)


def _test_dialog(send_test: Any) -> SettingsDialog:
    return SettingsDialog(GuiSettings(), [], MagicMock(), send_test=send_test)


def test_no_test_button_without_a_way_to_send() -> None:
    assert not hasattr(_dialog(), "_test_button")


@pytest.mark.asyncio
async def test_clicking_sends_one_test_notification_and_reports_it() -> None:
    send = AsyncMock()
    dialog = _test_dialog(send)
    dialog.show()
    dialog._test_button.click()
    await _settle()
    send.assert_awaited_once()
    assert dialog._test_status.text().startswith("Sent.")
    assert not dialog._test_status.isHidden()
    assert dialog._test_button.isEnabled()
    dialog.close()


@pytest.mark.asyncio
async def test_a_failure_is_shown_in_the_dialog() -> None:
    dialog = _test_dialog(AsyncMock(side_effect=NotifierError("Notifications are not allowed for pyobs-gui.")))
    dialog._test_button.click()
    await _settle()
    assert dialog._test_status.text() == "Notifications are not allowed for pyobs-gui."
    assert "c0392b" in dialog._test_status.styleSheet()
    assert dialog._test_button.isEnabled()


@pytest.mark.asyncio
async def test_an_unexpected_error_is_shown_too() -> None:
    dialog = _test_dialog(AsyncMock(side_effect=RuntimeError("boom")))
    dialog._test_button.click()
    await _settle()
    assert "boom" in dialog._test_status.text()


@pytest.mark.asyncio
async def test_clicks_while_a_test_is_running_are_ignored() -> None:
    release = asyncio.Event()
    calls: list[int] = []

    async def slow() -> None:
        calls.append(1)
        await release.wait()

    dialog = _test_dialog(slow)
    dialog._test_button.click()
    await _settle()
    assert not dialog._test_button.isEnabled()
    dialog._test()  # what a second click would do
    await _settle()
    release.set()
    await _settle()
    assert calls == [1] and dialog._test_button.isEnabled()


@pytest.mark.asyncio
async def test_a_second_test_is_possible_after_the_first() -> None:
    send = AsyncMock()
    dialog = _test_dialog(send)
    dialog._test_button.click()
    await _settle()
    dialog._test_button.click()
    await _settle()
    assert send.await_count == 2


@pytest.mark.asyncio
async def test_nothing_is_sent_unless_the_button_is_clicked() -> None:
    send = AsyncMock()
    dialog = _test_dialog(send)
    dialog.show()
    dialog._apply()
    dialog.reject()
    await _settle()
    send.assert_not_awaited()


@pytest.mark.parametrize(
    "platform, expected",
    [("win32", "Focus Assist"), ("darwin", "System Settings"), ("linux", "Do Not Disturb")],
)
def test_hint_for_a_test_that_showed_nothing(platform: str, expected: str) -> None:
    from pyobs_gui.settingsdialog import no_notification_hint

    assert expected in no_notification_hint(platform)


def test_windows_hint_mentions_the_start_menu_entry() -> None:
    from pyobs_gui.settingsdialog import no_notification_hint

    assert "Start Menu" in no_notification_hint("win32")
