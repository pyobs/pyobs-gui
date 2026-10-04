"""Connects `NotificationPolicy` to the live system: presence and log events in, notifications out.

See specs/2026-10-04-desktop-notifications.md. The policy decides, this class feeds it (presence of
every connected module, log events), schedules its timer, sends what comes out through a `Notifier`
and handles clicks.
"""

from __future__ import annotations

import asyncio
import logging
import time
from functools import partial
from typing import TYPE_CHECKING, Any

from pyobs.events import Event, LogEvent, ModuleClosedEvent, ModuleOpenedEvent
from PySide6 import QtCore, QtGui  # type: ignore

from .guisignals import gui_signals
from .notifications import Notice, NotificationPolicy
from .notifier import NotifierError

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable, Iterable

    from pyobs.comm import Comm
    from pyobs.utils.enums import ModuleState

    from .notifier import Notifier
    from .settings import NotificationSettings

log = logging.getLogger(__name__)


def _application_is_active() -> bool:
    return QtGui.QGuiApplication.applicationState() == QtCore.Qt.ApplicationState.ApplicationActive


class NotificationManager(QtCore.QObject):
    # presence callbacks may arrive on another thread, this brings them to the main one
    _presence = QtCore.Signal(str, object, str)

    def __init__(
        self,
        comm: Comm,
        settings: Callable[[], NotificationSettings],
        notifier: Notifier,
        bring_to_front: Callable[[str | None], None],
        authorise: Callable[[], Awaitable[None]] | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """
        Args:
            comm: Connection to watch.
            settings: Current notification settings, read whenever something happens.
            notifier: Shows the notifications.
            bring_to_front: Called with the module of a clicked notification, None if a click
                should only raise the window.
            authorise: Asks the system for permission to notify, called when notifications are
                (or get) enabled, so a permission prompt doesn't first appear in the middle of
                an incident.
            clock: Seconds, only differences matter.
        """
        super().__init__()
        self._comm = comm
        self._settings = settings
        self._notifier = notifier
        self._bring_to_front = bring_to_front
        self._authorise = authorise
        self._clock = clock
        self._policy = NotificationPolicy(
            settings=settings,
            own_name=comm.name or "",
            clock=clock,
            app_active=_application_is_active,
        )

        self._callbacks: dict[str, Callable[[ModuleState, str], None]] = {}
        self._tasks: set[asyncio.Task[Any]] = set()
        self._started = False

        self._timer = QtCore.QTimer(self)
        self._timer.setSingleShot(True)
        self._timer.timeout.connect(self._on_timer)
        self._presence.connect(self._on_presence)

    # ── lifecycle ────────────────────────────────────────────────────────────

    async def start(self, modules: Iterable[str]) -> None:
        """Watch `modules`, which are the ones connected now, and everything that comes later."""
        modules = list(modules)
        self._started = True
        self._handle(self._policy.start(modules))
        await self._comm.register_event(LogEvent, self._on_log_event)
        await self._comm.register_event(ModuleOpenedEvent, self._on_module_opened)
        await self._comm.register_event(ModuleClosedEvent, self._on_module_closed)
        await asyncio.gather(*(self._subscribe(m) for m in modules))
        gui_signals.settings_changed.connect(self._on_settings_changed)
        self._request_authorisation()

    async def close(self) -> None:
        """Stop watching. Must be awaited before the comm is closed."""
        if not self._started:
            return
        self._started = False
        self._timer.stop()
        gui_signals.settings_changed.disconnect(self._on_settings_changed)
        await self._comm.unregister_event(LogEvent, self._on_log_event)
        await self._comm.unregister_event(ModuleOpenedEvent, self._on_module_opened)
        await self._comm.unregister_event(ModuleClosedEvent, self._on_module_closed)
        for module in list(self._callbacks):
            await self._unsubscribe(module)
        for task in list(self._tasks):
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)

    # ── modules ──────────────────────────────────────────────────────────────

    async def _subscribe(self, module: str) -> None:
        if module in self._callbacks:
            return
        callback = partial(self._presence_from_comm, module)
        self._callbacks[module] = callback
        await self._comm.subscribe_presence(module, callback)

    async def _unsubscribe(self, module: str) -> None:
        callback = self._callbacks.pop(module, None)
        if callback is not None:
            await self._comm.unsubscribe_presence(module, callback)

    def _presence_from_comm(self, module: str, state: ModuleState, error: str) -> None:
        self._presence.emit(module, state, error)

    @QtCore.Slot(str, object, str)  # type: ignore[untyped-decorator]
    def _on_presence(self, module: str, state: ModuleState, error: str) -> None:
        if self._started:
            self._handle(self._policy.module_state(module, state, error))

    async def _on_module_opened(self, event: Event, sender: str) -> bool:
        await self._subscribe(sender)
        return True

    async def _on_module_closed(self, event: Event, sender: str) -> bool:
        await self._unsubscribe(sender)
        self._handle(self._policy.module_closed(sender))
        return True

    async def _on_log_event(self, event: Event, sender: str) -> bool:
        if isinstance(event, LogEvent):
            self._handle(self._policy.log(sender, event.level, event.message))
        return True

    # ── notices ──────────────────────────────────────────────────────────────

    def _handle(self, notices: list[Notice]) -> None:
        """Send what the policy returned, and set the timer for what it still has pending."""
        for notice in notices:
            task = asyncio.ensure_future(
                self._notifier.send(
                    notice.title, notice.message, notice.critical, partial(self._bring_to_front, notice.module)
                )
            )
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
        self._reschedule()

    def _reschedule(self) -> None:
        deadline = self._policy.next_deadline()
        if deadline is None:
            self._timer.stop()
        else:
            # a little late rather than early, so the policy finds the deadline passed
            self._timer.start(max(1, int((deadline - self._clock()) * 1000) + 20))

    def _on_timer(self) -> None:
        if self._started:
            self._handle(self._policy.tick())

    # ── permission ───────────────────────────────────────────────────────────

    def _on_settings_changed(self) -> None:
        self._request_authorisation()

    def _request_authorisation(self) -> None:
        if self._authorise is None or not self._settings().enabled:
            return
        task = asyncio.ensure_future(self._authorise_quietly(self._authorise))
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)

    @staticmethod
    async def _authorise_quietly(authorise: Callable[[], Awaitable[None]]) -> None:
        try:
            await authorise()
        except NotifierError as e:
            # warning, not error: a log event of that level could itself trigger a notification
            log.warning("Desktop notifications are not available: %s", e)


__all__ = ["NotificationManager"]
