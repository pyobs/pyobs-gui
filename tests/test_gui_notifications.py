"""GUI starts, stops and restarts its notification manager."""

from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from pyobs.comm.local import LocalComm

import pyobs_gui.gui as gui_module
from pyobs_gui.gui import GUI


class FakeManager:
    instances: list["FakeManager"] = []

    def __init__(self, **kwargs: Any) -> None:
        self.kwargs = kwargs
        self.started_with: Any = None
        self.closed = 0
        self.fail_start = False
        FakeManager.instances.append(self)

    async def start(self, modules: Any) -> None:
        if self.fail_start:
            raise RuntimeError("no service")
        self.started_with = list(modules)

    async def close(self) -> None:
        self.closed += 1


@pytest.fixture
def gui(monkeypatch: pytest.MonkeyPatch) -> GUI:
    FakeManager.instances = []
    monkeypatch.setattr(gui_module, "NotificationManager", FakeManager)
    monkeypatch.setattr(gui_module, "DesktopNotifierBackend", MagicMock())
    g = GUI(comm=LocalComm(name="gui"), notifications={})
    g._window = MagicMock()
    return g


@pytest.mark.asyncio
async def test_manager_is_started_with_the_connected_modules_and_the_current_settings(gui: GUI) -> None:
    await gui._start_notifications()
    (manager,) = FakeManager.instances
    assert gui._notifications is manager
    assert manager.started_with == list(gui.comm.clients)
    assert manager.kwargs["settings"]() is gui.settings.notifications
    gui.settings.notifications = gui.settings.notifications.model_copy(update={"rate_limit": 3})
    assert manager.kwargs["settings"]().rate_limit == 3  # read live, not captured


@pytest.mark.asyncio
async def test_a_click_raises_the_current_window(gui: GUI) -> None:
    window = MagicMock()
    gui._window = window
    await gui._start_notifications()
    FakeManager.instances[0].kwargs["bring_to_front"]("cam")
    window.bring_to_front.assert_called_once_with("cam")
    gui._window = None
    FakeManager.instances[0].kwargs["bring_to_front"]("cam")  # no window: nothing to do


@pytest.mark.asyncio
async def test_a_manager_that_cannot_start_does_not_stop_the_gui(
    gui: GUI, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setattr(FakeManager, "start", AsyncMock(side_effect=RuntimeError("no service")))
    await gui._start_notifications()
    assert gui._notifications is None
    assert [r.levelname for r in caplog.records] == ["WARNING"]


@pytest.mark.asyncio
async def test_close_stops_the_manager_once(gui: GUI) -> None:
    await gui._start_notifications()
    (manager,) = FakeManager.instances
    await gui._close_notifications()
    await gui._close_notifications()
    assert manager.closed == 1 and gui._notifications is None


@pytest.mark.asyncio
async def test_a_manager_that_fails_to_stop_is_only_a_warning(gui: GUI, caplog: pytest.LogCaptureFixture) -> None:
    await gui._start_notifications()
    FakeManager.instances[0].close = AsyncMock(side_effect=RuntimeError("comm gone"))  # type: ignore[method-assign]
    await gui._close_notifications()
    assert gui._notifications is None
    assert [r.levelname for r in caplog.records] == ["WARNING"]


@pytest.mark.asyncio
async def test_module_close_stops_the_manager_before_the_comm(gui: GUI) -> None:
    await gui._start_notifications()
    (manager,) = FakeManager.instances
    await gui.close()
    assert manager.closed == 1


@pytest.mark.asyncio
async def test_logout_stops_the_manager_before_the_comm_is_closed(gui: GUI, monkeypatch: pytest.MonkeyPatch) -> None:
    import asyncio

    await gui._start_notifications()
    (manager,) = FakeManager.instances
    order: list[str] = []
    manager.close = AsyncMock(side_effect=lambda: order.append("manager"))  # type: ignore[method-assign]
    comm = MagicMock()
    comm.close = AsyncMock(side_effect=lambda: order.append("comm"))
    gui._comm = comm
    monkeypatch.setattr("pyobs_gui.login.show_login_and_connect", AsyncMock(side_effect=asyncio.CancelledError))
    monkeypatch.setattr(gui, "quit", MagicMock(), raising=False)

    old_window = MagicMock()
    old_window.discard_all_widgets = AsyncMock()
    await gui._logout(old_window)

    assert order == ["manager", "comm"]
    assert gui._notifications is None


# ── test button of the settings dialog ────────────────────────────────────


@pytest.mark.asyncio
async def test_the_test_notification_goes_through_the_backend_and_a_click_raises_the_window(
    gui: GUI, monkeypatch: pytest.MonkeyPatch
) -> None:
    backend = MagicMock()
    backend.send = AsyncMock()
    monkeypatch.setattr(gui_module, "DesktopNotifierBackend", MagicMock(return_value=backend))
    window = MagicMock()
    gui._window = window

    await gui._send_test_notification()

    title, message, critical, on_clicked = backend.send.call_args.args
    assert (title, critical) == ("pyobs-gui", False) and message
    on_clicked()
    window.bring_to_front.assert_called_once_with(None)


@pytest.mark.asyncio
async def test_a_problem_with_the_test_notification_reaches_the_dialog(
    gui: GUI, monkeypatch: pytest.MonkeyPatch
) -> None:
    from pyobs_gui.notifier import NotifierError

    backend = MagicMock()
    backend.send = AsyncMock(side_effect=NotifierError("not allowed"))
    monkeypatch.setattr(gui_module, "DesktopNotifierBackend", MagicMock(return_value=backend))
    with pytest.raises(NotifierError, match="not allowed"):
        await gui._send_test_notification()


@pytest.mark.asyncio
async def test_notifications_and_the_test_button_share_one_backend(gui: GUI, monkeypatch: pytest.MonkeyPatch) -> None:
    backend = MagicMock()
    backend.send = AsyncMock()
    factory = MagicMock(return_value=backend)
    monkeypatch.setattr(gui_module, "DesktopNotifierBackend", factory)
    await gui._start_notifications()
    await gui._send_test_notification()
    factory.assert_called_once_with()


def test_the_settings_dialog_gets_the_test_button(gui: GUI, monkeypatch: pytest.MonkeyPatch) -> None:
    dialog_class = MagicMock()
    monkeypatch.setattr(gui_module, "SettingsDialog", dialog_class)
    gui._open_settings()
    assert dialog_class.call_args.kwargs["send_test"] == gui._send_test_notification
