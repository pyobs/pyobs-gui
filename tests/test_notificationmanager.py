import asyncio
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
import pytest_asyncio
from pyobs.events import LogEvent, ModuleClosedEvent, ModuleOpenedEvent
from pyobs.utils.enums import ModuleState

from pyobs_gui.guisignals import gui_signals
from pyobs_gui.notificationmanager import NotificationManager
from pyobs_gui.notifier import NotifierError
from pyobs_gui.settings import NotificationSettings

ERROR = ModuleState.ERROR
READY = ModuleState.READY


class FakeComm:
    name = "gui"

    def __init__(self) -> None:
        self.presence: dict[str, Any] = {}
        self.events: dict[type, Any] = {}
        self.subscribe_calls: list[str] = []

    async def subscribe_presence(self, module: str, callback: Any) -> None:
        self.subscribe_calls.append(module)
        self.presence[module] = callback

    async def unsubscribe_presence(self, module: str, callback: Any) -> None:
        assert self.presence.get(module) == callback
        del self.presence[module]

    async def register_event(self, event_class: type, handler: Any) -> None:
        self.events[event_class] = handler

    async def unregister_event(self, event_class: type, handler: Any) -> None:
        assert self.events.pop(event_class) == handler


class FakeNotifier:
    def __init__(self) -> None:
        self.sent: list[tuple[str, str, bool, Any]] = []

    async def send(self, title: str, message: str, critical: bool, on_clicked: Any) -> None:
        self.sent.append((title, message, critical, on_clicked))


class Env:
    def __init__(self, settings: NotificationSettings, authorise: Any = None) -> None:
        self.settings = settings
        self.comm = FakeComm()
        self.notifier = FakeNotifier()
        self.front = MagicMock()
        self.now = 1000.0
        self.manager = NotificationManager(
            comm=self.comm,  # type: ignore[arg-type]
            settings=lambda: self.settings,
            notifier=self.notifier,
            bring_to_front=self.front,
            authorise=authorise,
            clock=lambda: self.now,
        )

    async def settle(self) -> None:
        for _ in range(5):
            await asyncio.sleep(0)

    async def presence(self, module: str, state: ModuleState, error: str = "") -> None:
        self.comm.presence[module](state, error)
        await self.settle()

    async def event(self, event: Any, sender: str) -> None:
        await self.comm.events[type(event)](event, sender)
        await self.settle()


def _log(level: str, message: str = "boom") -> LogEvent:
    return LogEvent("2026-10-04 12:00:00", level, "x.py", "f", 1, message)


@pytest_asyncio.fixture
async def env() -> AsyncIterator[Env]:
    e = Env(NotificationSettings(rate_limit=0))
    yield e
    await e.manager.close()


# ── watching modules ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_start_subscribes_to_every_module_and_watches_events(env: Env) -> None:
    await env.manager.start(["a", "b"])
    assert sorted(env.comm.presence) == ["a", "b"]
    assert set(env.comm.events) == {LogEvent, ModuleOpenedEvent, ModuleClosedEvent}


@pytest.mark.asyncio
async def test_a_module_going_into_error_is_notified_and_a_click_selects_it(env: Env) -> None:
    await env.manager.start(["cam"])
    await env.presence("cam", READY)
    await env.presence("cam", ERROR, "no filter wheel")
    assert [(t, m, c) for t, m, c, _ in env.notifier.sent] == [("cam: ERROR", "no filter wheel", True)]
    env.notifier.sent[0][3]()
    env.front.assert_called_once_with("cam")


@pytest.mark.asyncio
async def test_a_log_error_is_notified_and_a_click_only_raises(env: Env) -> None:
    await env.manager.start([])
    await env.event(_log("ERROR", "boom"), "cam")
    assert [(t, m) for t, m, _, _ in env.notifier.sent] == [("cam: ERROR", "boom")]
    env.notifier.sent[0][3]()
    env.front.assert_called_once_with(None)


@pytest.mark.asyncio
async def test_log_below_error_and_own_log_events_are_ignored(env: Env) -> None:
    await env.manager.start([])
    await env.event(_log("WARNING"), "cam")
    await env.event(_log("CRITICAL", "own problem"), "gui")
    assert env.notifier.sent == []


@pytest.mark.asyncio
async def test_a_module_that_opens_later_is_watched_once(env: Env) -> None:
    await env.manager.start(["a"])
    await env.event(ModuleOpenedEvent(), "late")
    await env.event(ModuleOpenedEvent(), "late")
    await env.event(ModuleOpenedEvent(), "a")  # already watched from the start
    assert env.comm.subscribe_calls == ["a", "late"]
    await env.presence("late", ERROR, "x")
    assert [t for t, *_ in env.notifier.sent] == ["late: ERROR"]


@pytest.mark.asyncio
async def test_a_module_that_closes_is_not_watched_any_more(env: Env) -> None:
    await env.manager.start(["a"])
    await env.event(ModuleClosedEvent(), "a")
    assert "a" not in env.comm.presence


@pytest.mark.asyncio
async def test_startup_errors_come_as_one_summary_after_the_timeout(env: Env) -> None:
    await env.manager.start(["a", "b", "c"])
    await env.presence("a", ERROR, "x")
    await env.presence("b", ERROR, "y")
    assert env.notifier.sent == []
    assert env.manager._timer.isActive()

    env.now += 4  # "c" never reports
    env.manager._on_timer()
    await env.settle()
    assert [(t, m) for t, m, _, _ in env.notifier.sent] == [("2 modules in ERROR", "a, b")]
    assert not env.manager._timer.isActive()


@pytest.mark.asyncio
async def test_trailing_notice_is_sent_when_the_timer_fires() -> None:
    env = Env(NotificationSettings(rate_limit=10))
    await env.manager.start([])
    await env.event(_log("ERROR", "1"), "cam")
    await env.event(_log("ERROR", "2"), "cam")
    assert len(env.notifier.sent) == 1
    assert env.manager._timer.isActive()
    env.now += 11
    env.manager._on_timer()
    await env.settle()
    assert [t for t, *_ in env.notifier.sent] == ["cam: ERROR", "cam: 1 more"]
    await env.manager.close()


@pytest.mark.asyncio
async def test_disabled_notifies_nothing() -> None:
    env = Env(NotificationSettings(enabled=False))
    await env.manager.start(["cam"])
    await env.presence("cam", ERROR, "x")
    await env.event(_log("CRITICAL"), "cam")
    assert env.notifier.sent == []
    await env.manager.close()


@pytest.mark.asyncio
async def test_presence_from_another_thread_is_handled_on_the_main_thread(env: Env) -> None:
    import threading

    from PySide6 import QtCore

    await env.manager.start(["cam"])
    worker = threading.Thread(target=env.comm.presence["cam"], args=(ERROR, "x"))
    worker.start()
    worker.join()
    assert env.notifier.sent == []
    QtCore.QCoreApplication.processEvents()
    await env.settle()
    assert len(env.notifier.sent) == 1


# ── closing ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_close_unsubscribes_everything_and_stops_reacting() -> None:
    env = Env(NotificationSettings(rate_limit=10))
    await env.manager.start(["a", "b"])
    await env.event(_log("ERROR", "1"), "x")
    await env.event(_log("ERROR", "2"), "x")
    await env.manager.close()
    assert env.comm.presence == {} and env.comm.events == {}
    assert not env.manager._timer.isActive()
    gui_signals.settings_changed.emit()  # must not reach the closed manager
    await env.manager.close()  # harmless twice


# ── permission ────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_permission_is_asked_for_at_start_when_enabled() -> None:
    authorise = AsyncMock()
    env = Env(NotificationSettings(), authorise=authorise)
    await env.manager.start([])
    await env.settle()
    authorise.assert_awaited_once()
    await env.manager.close()


@pytest.mark.asyncio
async def test_permission_is_not_asked_for_when_disabled_but_when_enabled_later() -> None:
    authorise = AsyncMock()
    env = Env(NotificationSettings(enabled=False), authorise=authorise)
    await env.manager.start([])
    await env.settle()
    authorise.assert_not_awaited()

    env.settings = NotificationSettings(enabled=True)
    gui_signals.settings_changed.emit()
    await env.settle()
    authorise.assert_awaited_once()
    await env.manager.close()


@pytest.mark.asyncio
async def test_a_refused_permission_is_only_a_warning(caplog: pytest.LogCaptureFixture) -> None:
    env = Env(NotificationSettings(), authorise=AsyncMock(side_effect=NotifierError("not allowed")))
    await env.manager.start([])
    await env.settle()
    assert [r.levelname for r in caplog.records if "not available" in r.getMessage()] == ["WARNING"]
    await env.manager.close()


# ── MainWindow ────────────────────────────────────────────────────────────


def test_bring_to_front_shows_the_window_asks_for_attention_and_selects_the_module(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from PySide6 import QtWidgets

    from pyobs_gui.mainwindow import MainWindow

    alert = MagicMock()
    monkeypatch.setattr(QtWidgets.QApplication, "alert", alert)
    window = MainWindow(show_shell=False, show_events=False, show_status=False)
    window.listPages.addItem("dome")
    window.listPages.addItem("cam")
    window.listPages.setCurrentRow(0)

    window.bring_to_front("cam")
    assert window.isVisible()
    assert window.listPages.currentItem().text() == "cam"
    alert.assert_called_once_with(window)

    # a log event only raises: the selection stays
    window.listPages.setCurrentRow(0)
    window.bring_to_front(None)
    assert window.listPages.currentItem().text() == "dome"

    # a module without a page is not an error
    window.bring_to_front("hidden")
    assert window.listPages.currentItem().text() == "dome"
    window.hide()
