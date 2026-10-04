import logging
import threading
from typing import Any
from unittest.mock import MagicMock

import pytest
from desktop_notifier import Urgency
from PySide6 import QtCore

from pyobs_gui.notifier import GuardedNotifier, NotifierError
from pyobs_gui.notifier_backend import APP_NAME, DesktopNotifierBackend


class FakeDesktopNotifier:
    """The parts of `desktop_notifier.DesktopNotifier` the backend uses."""

    def __init__(self, authorised: bool = True, grants: bool = True, fail: Exception | None = None) -> None:
        self.authorised = authorised
        self.grants = grants
        self.fail = fail
        self.sent: list[dict[str, Any]] = []
        self.has_calls = 0
        self.request_calls = 0

    async def has_authorisation(self) -> bool:
        self.has_calls += 1
        return self.authorised

    async def request_authorisation(self) -> bool:
        self.request_calls += 1
        self.authorised = self.grants
        return self.grants

    async def send(self, **kwargs: Any) -> str:
        if self.fail is not None:
            raise self.fail
        self.sent.append(kwargs)
        return "id"


def _backend(fake: FakeDesktopNotifier, identity: Any = None) -> tuple[DesktopNotifierBackend, MagicMock]:
    identity = identity or MagicMock()
    return DesktopNotifierBackend(notifier_factory=lambda: fake, ensure_identity=identity), identity


# ── sending ───────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_send_passes_title_message_and_urgency() -> None:
    fake = FakeDesktopNotifier()
    backend, _ = _backend(fake)
    await backend.send("cam: ERROR", "no filter wheel", True, lambda: None)
    await backend.send("cam: ERROR", "again", False, lambda: None)
    assert [(s["title"], s["message"], s["urgency"]) for s in fake.sent] == [
        ("cam: ERROR", "no filter wheel", Urgency.Critical),
        ("cam: ERROR", "again", Urgency.Normal),
    ]


@pytest.mark.asyncio
async def test_notifier_is_built_once_and_the_identity_is_ensured_before_that() -> None:
    order: list[str] = []
    fake = FakeDesktopNotifier()
    backend = DesktopNotifierBackend(
        notifier_factory=lambda: (order.append("built"), fake)[1],
        ensure_identity=lambda: order.append("identity"),
    )
    await backend.send("a", "b", False, lambda: None)
    await backend.send("a", "b", False, lambda: None)
    assert order == ["identity", "built"]


@pytest.mark.asyncio
async def test_nothing_is_built_before_the_first_use() -> None:
    factory = MagicMock()
    DesktopNotifierBackend(notifier_factory=factory, ensure_identity=MagicMock())
    factory.assert_not_called()


@pytest.mark.asyncio
async def test_a_failing_send_is_reported_to_the_caller() -> None:
    backend, _ = _backend(FakeDesktopNotifier(fail=RuntimeError("no dbus")))
    with pytest.raises(NotifierError, match="no dbus"):
        await backend.send("a", "b", False, lambda: None)


@pytest.mark.asyncio
async def test_a_notifier_that_cannot_be_built_is_reported_to_the_caller() -> None:
    def factory() -> Any:
        raise RuntimeError("no service")

    backend = DesktopNotifierBackend(notifier_factory=factory, ensure_identity=MagicMock())
    with pytest.raises(NotifierError, match="no service"):
        await backend.send("a", "b", False, lambda: None)


# ── authorisation ─────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_authorisation_is_asked_for_when_missing_and_remembered() -> None:
    fake = FakeDesktopNotifier(authorised=False, grants=True)
    backend, _ = _backend(fake)
    await backend.send("a", "b", False, lambda: None)
    await backend.send("a", "b", False, lambda: None)
    assert (fake.request_calls, fake.has_calls, len(fake.sent)) == (1, 1, 2)


@pytest.mark.asyncio
async def test_a_refusal_is_reported_and_asked_again_next_time() -> None:
    fake = FakeDesktopNotifier(authorised=False, grants=False)
    backend, _ = _backend(fake)
    for _ in range(2):
        with pytest.raises(NotifierError, match="not allowed"):
            await backend.send("a", "b", False, lambda: None)
    assert fake.sent == [] and fake.request_calls == 2


@pytest.mark.asyncio
async def test_already_authorised_is_not_asked_for() -> None:
    fake = FakeDesktopNotifier(authorised=True)
    backend, _ = _backend(fake)
    await backend.ensure_authorisation()
    assert fake.request_calls == 0


# ── click ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_click_from_another_thread_runs_on_the_main_thread() -> None:
    fake = FakeDesktopNotifier()
    backend, _ = _backend(fake)
    ran_on: list[int] = []
    await backend.send("a", "b", False, lambda: ran_on.append(threading.get_ident()))

    worker = threading.Thread(target=fake.sent[0]["on_clicked"])
    worker.start()
    worker.join()
    assert ran_on == []  # not run on the worker thread, waiting for the event loop
    QtCore.QCoreApplication.processEvents()
    assert ran_on == [threading.get_ident()]


@pytest.mark.asyncio
async def test_click_from_the_main_thread_runs_the_callback() -> None:
    fake = FakeDesktopNotifier()
    backend, _ = _backend(fake)
    clicked = MagicMock()
    await backend.send("a", "b", False, clicked)
    fake.sent[0]["on_clicked"]()
    QtCore.QCoreApplication.processEvents()
    clicked.assert_called_once_with()


# ── guard ─────────────────────────────────────────────────────────────────


class _Failing:
    def __init__(self) -> None:
        self.fail = True
        self.calls = 0

    async def send(self, title: str, message: str, critical: bool, on_clicked: Any) -> None:
        self.calls += 1
        if self.fail:
            raise NotifierError("no service")


@pytest.mark.asyncio
async def test_guard_logs_a_failure_once_at_warning_and_never_raises(caplog: pytest.LogCaptureFixture) -> None:
    inner = _Failing()
    guard = GuardedNotifier(inner)
    with caplog.at_level(logging.DEBUG, logger="pyobs_gui.notifier"):
        for _ in range(3):
            await guard.send("a", "b", False, lambda: None)
    assert inner.calls == 3
    assert [(r.levelno, "no service" in r.getMessage()) for r in caplog.records] == [(logging.WARNING, True)]


@pytest.mark.asyncio
async def test_guard_logs_again_after_it_worked_in_between(caplog: pytest.LogCaptureFixture) -> None:
    inner = _Failing()
    guard = GuardedNotifier(inner)
    with caplog.at_level(logging.DEBUG, logger="pyobs_gui.notifier"):
        await guard.send("a", "b", False, lambda: None)
        inner.fail = False
        await guard.send("a", "b", False, lambda: None)
        inner.fail = True
        await guard.send("a", "b", False, lambda: None)
    assert len(caplog.records) == 2


@pytest.mark.asyncio
async def test_guard_passes_everything_on() -> None:
    fake = FakeDesktopNotifier()
    backend, _ = _backend(fake)
    guard = GuardedNotifier(backend)
    await guard.send("t", "m", True, lambda: None)
    assert (fake.sent[0]["title"], fake.sent[0]["message"], fake.sent[0]["urgency"]) == ("t", "m", Urgency.Critical)


def test_app_name_is_what_windows_uses_as_the_id() -> None:
    assert APP_NAME == "pyobs-gui"
