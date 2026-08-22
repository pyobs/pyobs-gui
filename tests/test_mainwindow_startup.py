import asyncio
from typing import Any

import pytest
from PySide6 import QtGui

from pyobs.events import Event
from pyobs.interfaces import IMotion, IPointingAltAz, IPointingRaDec, IOffsetsAltAz, IOffsetsRaDec
from pyobs_gui.base import BaseWidget
from pyobs_gui.mainwindow import MainWindow
from pyobs_gui.telescopewidget import TelescopeWidget


class _FakeComm:
    """Minimal comm for MainWindow startup tests: a client list, no-op event registration, and
    empty interface/autonomous/weather lookups."""

    def __init__(self, clients: list[str] | None = None):
        self.clients: list[str] = [] if clients is None else clients

    async def clients_with_interface(self, interface: Any) -> list[str]:
        return []

    async def register_event(self, event_class: Any, handler: Any) -> None:
        pass

    async def unregister_event(self, event_class: Any, handler: Any) -> None:
        pass


class _NoOpComm:
    """Comm surface ShellWidget.open()/CommandModel.init() touch: empty client list, no-op
    events."""

    clients: list[str] = []

    async def get_interfaces(self, client: str) -> list[Any]:
        return []

    async def register_event(self, event_class: Any, handler: Any) -> None:
        pass


class _BlockingSubscribeComm:
    """Records subscribe_state() calls and blocks until release -- proves asyncio.gather()
    starts all subscriptions before any of them completes."""

    def __init__(self):
        self.calls: list[Any] = []
        self.release = asyncio.Event()

    async def subscribe_state(self, module: str, interface: Any, callback: Any) -> None:
        self.calls.append(interface)
        await self.release.wait()


class _SlowOpenWidget(BaseWidget):
    """BaseWidget whose open() blocks until release is set -- for exercising the placeholder /
    background-open / swap machinery without any real comm traffic."""

    def __init__(self):
        super().__init__()
        self.release = asyncio.Event()
        self.opened = False
        self.discarded = False
        self._init_calls = 0

    # pyrefly: ignore [bad-override]
    async def open(self, **kwargs: Any) -> None:
        self.opened = True
        await self.release.wait()

    async def _init(self) -> None:
        self._init_calls += 1
        await asyncio.sleep(0.01)

    async def discard(self) -> None:
        self.discarded = True
        await super().discard()


class _FailingOpenWidget(_SlowOpenWidget):
    # pyrefly: ignore [bad-override]
    async def open(self, **kwargs: Any) -> None:
        raise RuntimeError("boom")


class _SlowInitWidget(BaseWidget):
    def __init__(self):
        super().__init__()
        self._init_calls = 0

    async def _init(self) -> None:
        self._init_calls += 1
        await asyncio.sleep(0.01)


class _FlakyInitWidget(BaseWidget):
    """_init() raises on its first call, succeeds afterwards -- covers the retry-on-failure
    semantics of BaseWidget._showEvent."""

    def __init__(self):
        super().__init__()
        self._init_calls = 0
        self._fail_first = True

    async def _init(self) -> None:
        self._init_calls += 1
        if self._fail_first:
            self._fail_first = False
            raise RuntimeError("boom")


def _make_window(clients: list[str] | None = None) -> MainWindow:
    window = MainWindow(show_shell=False, show_events=False, show_status=False)
    window._comm = _FakeComm(clients=clients)  # pyrefly: ignore [bad-assignment]
    return window


@pytest.mark.asyncio
async def test_add_client_placeholder_swaps_when_open_finishes(qapp) -> None:
    """The nav item, registry entry, and a clickable "Loading…" page exist the moment
    _add_client returns; once open() finishes the real widget replaces the placeholder and,
    if the page was current, becomes current (and _init fires)."""
    window = _make_window()
    window.show()  # so the real widget's showEvent -> _init fires once it becomes current
    try:
        widget = _SlowOpenWidget()
        client = "telescope"

        await window._add_client(client, QtGui.QIcon(), widget)

        item = window.listPages.item(0)
        assert item is not None and item.text() == client
        assert window._widgets[client] is widget
        assert client in window._pending_opens
        placeholder = window._pages[client]
        assert placeholder is not widget

        # clicking the nav row switches to the placeholder instantly -- the click is not dropped
        window._change_page(0)
        assert window.stackedWidget.currentWidget() is placeholder

        # finish the open: same stackedWidget index, real widget current, _init ran
        task = window._pending_opens[client]
        widget.release.set()
        await task

        assert window._pages[client] is widget
        assert window.stackedWidget.currentWidget() is widget
        await asyncio.sleep(0.05)  # let the showEvent -> _init task run
        assert widget._init_calls == 1
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_open_failure_removes_client(qapp) -> None:
    """A failing open() must tear the client down (nav item, placeholder, registry) instead of
    leaving a permanent "Loading…" page."""
    window = _make_window()
    try:
        widget = _FailingOpenWidget()
        client = "camera"

        await window._add_client(client, QtGui.QIcon(), widget)
        task = window._pending_opens[client]
        await task  # open() raises -> _fail_open tears the client down

        assert client not in window._widgets
        assert client not in window._pages
        assert widget.discarded
        assert window.stackedWidget.count() == 0  # no "Loading…" page left behind
        assert window.listPages.count() == 0
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_disconnect_mid_open_tears_down_without_ghost(qapp) -> None:
    """Disconnecting while open() is still in flight cancels the pending open (and awaits it)
    before discarding, and removes the placeholder from the stack -- no ghost page."""
    window = _make_window()
    try:
        widget = _SlowOpenWidget()
        client = "telescope"

        await window._add_client(client, QtGui.QIcon(), widget)
        window._change_page(0)  # placeholder is the current page

        assert await window._client_disconnected(Event(), client)

        assert client not in window._widgets
        assert client not in window._pages
        assert widget.discarded
        assert not widget.release.is_set()  # open() was cancelled, never completed
        assert window.stackedWidget.count() == 0  # placeholder removed from the stack
        assert window.listPages.count() == 0
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_discard_all_widgets_drains_pending_opens(qapp) -> None:
    """discard_all_widgets() (logout path) must cancel and drain in-flight open tasks before
    discarding widgets, so no background task mutates the stack during teardown."""
    window = _make_window()
    try:
        widget = _SlowOpenWidget()
        await window._add_client("telescope", QtGui.QIcon(), widget)

        await window.discard_all_widgets()

        assert window._pending_opens == {}
        assert widget.discarded
        assert not widget.release.is_set()  # open was cancelled, never completed
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_init_clients_runs_in_parallel(qapp, monkeypatch) -> None:
    """_init_clients must start every client's connect before any of them completes (event
    ordering, not wall-clock)."""
    window = _make_window(clients=["camera", "telescope"])
    try:
        started: list[str] = []
        release = asyncio.Event()

        async def fake_connected(event: Event, client: str) -> bool:
            started.append(client)
            await release.wait()
            return True

        monkeypatch.setattr(window, "_client_connected", fake_connected)

        task = asyncio.create_task(window._init_clients())
        for _ in range(100):
            if len(started) == 2:
                break
            await asyncio.sleep(0.01)
        assert started == ["camera", "telescope"]  # both in flight before either completes

        release.set()
        await task
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_telescope_init_subscribes_all_interfaces_in_parallel(qapp) -> None:
    """TelescopeWidget._init must fire all five subscribe_state calls concurrently (all in
    flight before any completes)."""
    widget = TelescopeWidget(module="telescope")
    widget.modules = ["telescope"]
    widget._interfaces = [IMotion, IPointingRaDec, IPointingAltAz, IOffsetsRaDec, IOffsetsAltAz]
    comm = _BlockingSubscribeComm()
    widget._comm = comm  # pyrefly: ignore [bad-assignment]
    try:
        task = asyncio.create_task(widget._init())
        for _ in range(100):
            if len(comm.calls) == 5:
                break
            await asyncio.sleep(0.01)
        assert len(comm.calls) == 5
        assert comm.calls[0] is IMotion

        comm.release.set()
        await task
    finally:
        widget.deleteLater()


@pytest.mark.asyncio
async def test_show_event_runs_init_once_under_concurrent_shows(qapp) -> None:
    """Two rapid show events must not run _init() twice (memoized init task)."""
    widget = _SlowInitWidget()
    try:
        event = QtGui.QShowEvent()
        await asyncio.gather(widget._showEvent(event), widget._showEvent(event))
        assert widget._init_calls == 1
    finally:
        widget.deleteLater()


@pytest.mark.asyncio
async def test_show_event_retries_init_after_failure(qapp) -> None:
    """A failing _init() leaves the widget un-initialized so the next show retries -- it must
    not be permanently marked initialized."""
    widget = _FlakyInitWidget()
    try:
        event = QtGui.QShowEvent()
        await widget._showEvent(event)  # fails; logged, task cleared
        assert widget._initialized is False
        assert widget._init_task is None

        await widget._showEvent(event)  # retries and succeeds
        assert widget._initialized is True
        assert widget._init_calls == 2
    finally:
        widget.deleteLater()


@pytest.mark.asyncio
async def test_shell_rebuild_gated_on_visibility_and_lazy_on_show(qapp) -> None:
    """The Shell command model must not rebuild while the page is hidden (only marked stale);
    showing the page triggers the lazy rebuild."""
    from pyobs_gui.shellwidget import ShellWidget

    shell = ShellWidget()
    try:
        await shell.open(comm=_NoOpComm(), observer=None, vfs=None)  # pyrefly: ignore [bad-argument-type]

        assert not shell.isVisible()
        await shell.update_client_list()
        assert shell._model_stale is True  # skipped, not rebuilt

        shell.show()
        await asyncio.sleep(0.05)  # let the showEvent-triggered rebuild run
        assert shell._model_stale is False
    finally:
        shell.deleteLater()
