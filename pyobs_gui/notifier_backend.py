"""`Notifier` backend on top of `desktop-notifier` -- see specs/2026-10-04-desktop-notifications.md.

Checked on KDE, GNOME (Wayland) and Windows 11, see the spike results there. Not checked on macOS.
"""

from __future__ import annotations

import logging
import sys
from typing import TYPE_CHECKING, Any

from PySide6 import QtCore  # type: ignore

from .notifier import NotifierError

if TYPE_CHECKING:
    from collections.abc import Callable

log = logging.getLogger(__name__)

# shown by the system, and on Windows the AppUserModelID (desktop-notifier uses it as the id)
APP_NAME = "pyobs-gui"


class _ClickRelay(QtCore.QObject):
    """The click callback of the library may come from another thread (on Windows, likely), the
    callbacks of this application must run on the main thread. A signal emitted from any thread
    is delivered to a slot of an object living in the main thread by the event loop."""

    clicked = QtCore.Signal(object)

    def __init__(self) -> None:
        super().__init__()
        self.clicked.connect(self._run)

    @QtCore.Slot(object)  # type: ignore[untyped-decorator]
    def _run(self, callback: Callable[[], None]) -> None:
        callback()


def _ensure_identity() -> None:
    """Windows needs a Start Menu shortcut with the AppUserModelID, other systems nothing. Without
    it Windows drops the toast silently, so a failure here is only a warning, the notification is
    still tried."""
    if sys.platform != "win32":
        return
    from .windows_identity import ensure_shortcut

    try:
        ensure_shortcut(APP_NAME)
    except Exception as e:
        log.warning("Notifications may not show on Windows: %s", e)


class DesktopNotifierBackend:
    def __init__(
        self,
        notifier_factory: Callable[[], Any] | None = None,
        ensure_identity: Callable[[], None] = _ensure_identity,
    ) -> None:
        """
        Args:
            notifier_factory: Builds the `desktop_notifier.DesktopNotifier`, for tests.
            ensure_identity: Called once before it is built, for tests.
        """
        self._factory = notifier_factory
        self._ensure_identity = ensure_identity
        self._notifier: Any = None
        self._authorised = False
        self._relay = _ClickRelay()

    def _get(self) -> Any:
        """The library object, built on first use (building it can fail on a system without a
        notification service)."""
        if self._notifier is None:
            self._ensure_identity()
            if self._factory is not None:
                self._notifier = self._factory()
            else:
                from desktop_notifier import DesktopNotifier

                self._notifier = DesktopNotifier(app_name=APP_NAME)
        return self._notifier

    async def ensure_authorisation(self) -> None:
        """Ask the system for permission if it wasn't given yet (macOS asks the user once).

        Raises:
            NotifierError: Not allowed, or the backend doesn't work.
        """
        if self._authorised:
            return
        try:
            notifier = self._get()
            allowed = await notifier.has_authorisation() or await notifier.request_authorisation()
        except Exception as e:
            raise NotifierError(f"Could not check the notification permission: {e}") from e
        if not allowed:
            raise NotifierError(
                "Notifications are not allowed for pyobs-gui. Check the notification settings of your system."
            )
        self._authorised = True

    async def send(self, title: str, message: str, critical: bool, on_clicked: Callable[[], None]) -> None:
        await self.ensure_authorisation()
        from desktop_notifier import Urgency

        try:
            await self._get().send(
                title=title,
                message=message,
                urgency=Urgency.Critical if critical else Urgency.Normal,
                on_clicked=lambda: self._relay.clicked.emit(on_clicked),
            )
        except Exception as e:
            raise NotifierError(f"Could not show the notification: {e}") from e


__all__ = ["APP_NAME", "DesktopNotifierBackend"]
