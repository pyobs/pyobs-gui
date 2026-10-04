"""What the GUI needs from a desktop notification backend -- see
specs/2026-10-04-desktop-notifications.md. Backends (one per platform where needed) implement this,
the rest of the GUI only knows the protocol."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from collections.abc import Callable


class Notifier(Protocol):
    async def send(self, title: str, message: str, critical: bool, on_clicked: Callable[[], None]) -> None:
        """Show a notification.

        Args:
            title: Short first line.
            message: Details.
            critical: Whether the platform should treat it as urgent.
            on_clicked: Called when the user clicks the notification. May be called from another
                thread, so it must only hand over to the Qt main thread.
        """
        ...


__all__ = ["Notifier"]
