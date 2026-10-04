"""What the GUI needs from a desktop notification backend -- see
specs/2026-10-04-desktop-notifications.md. Backends (one per platform where needed) implement this,
the rest of the GUI only knows the protocol."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable

log = logging.getLogger(__name__)


class NotifierError(Exception):
    """A notification could not be shown. The message is meant for the user."""


class Notifier(Protocol):
    async def send(self, title: str, message: str, critical: bool, on_clicked: Callable[[], None]) -> None:
        """Show a notification.

        Args:
            title: Short first line.
            message: Details.
            critical: Whether the platform should treat it as urgent.
            on_clicked: Called on the Qt main thread when the user clicks the notification.

        Raises:
            NotifierError: The notification could not be shown.
        """
        ...


class GuardedNotifier:
    """For the notifications the application sends by itself: a failing backend must not break
    the event handling, and must not flood the log either. The first failure is logged at
    `WARNING` (never `ERROR`, a log event of that level could itself trigger a notification),
    further ones are not until a notification went through again."""

    def __init__(self, inner: Notifier) -> None:
        self._inner = inner
        self._failing = False

    async def send(self, title: str, message: str, critical: bool, on_clicked: Callable[[], None]) -> None:
        try:
            await self._inner.send(title, message, critical, on_clicked)
        except Exception as e:
            if not self._failing:
                log.warning("Desktop notifications do not work: %s (not logged again until one succeeds)", e)
            self._failing = True
        else:
            self._failing = False


__all__ = ["GuardedNotifier", "Notifier", "NotifierError"]
