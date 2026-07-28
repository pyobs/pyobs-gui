import asyncio
import logging
import sys
from typing import Any, cast, TYPE_CHECKING
from PySide6 import QtWidgets  # type: ignore
import qasync  # type: ignore

if TYPE_CHECKING:
    from .mainwindow import MainWindow

from pyobs.interfaces import FitsHeaderEntry, IFitsHeaderBefore
from pyobs.modules import Module

from .utils import QAsyncMessageBox

log = logging.getLogger(__name__)


class GUI(Module, IFitsHeaderBefore):
    __module__ = "pyobs_gui"

    app: QtWidgets.QApplication | None = None

    def __init__(
        self,
        show_shell: bool = True,
        show_events: bool = True,
        show_status: bool = True,
        show_modules: list[str] | None = None,
        widgets: list[dict[str, Any]] | None = None,
        sidebar: list[dict[str, Any]] | None = None,
        standalone: bool = False,
        *args: Any,
        **kwargs: Any,
    ):
        """Inits a new GUI.

        Args:
            show_shell: Whether to show the shell page.
            show_events: Whether to show the events page.
            show_modules: If not empty, show only listed modules.
            widgets: List of custom widgets.
            sidebar: List of custom sidebar widgets.
            standalone: Whether this GUI was built by the interactive login window
                (pyobs_gui.login.login_and_build_gui) rather than a YAML-configured Comm. When
                True, MainWindow's bottom-left button reads "Log out" and reconnects via the
                login window instead of quitting the whole app.
        """

        # init module
        Module.__init__(self, *args, **kwargs)
        self._window: MainWindow | None = None
        self._show_shell = show_shell
        self._show_events = show_events
        self._show_status = show_status
        self._show_modules = show_modules
        self._custom_widgets = widgets
        self._custom_sidebar_widgets = sidebar
        self._standalone = standalone
        self._logging_out = False

    @staticmethod
    def new_event_loop() -> asyncio.AbstractEventLoop:
        GUI.app = QtWidgets.QApplication(sys.argv)
        # standalone/login mode briefly has zero visible top-level windows while the login
        # dialog closes and the (old or new) MainWindow hasn't opened yet -- Qt's default
        # "quit when the last window closes" would tear down the whole event loop right there,
        # so this app manages its own lifetime exclusively through Module.quit() instead.
        GUI.app.setQuitOnLastWindowClosed(False)
        return cast("asyncio.AbstractEventLoop", qasync.QEventLoop(GUI.app))

    async def open(self) -> None:
        """Open module."""
        from .mainwindow import MainWindow

        await Module.open(self)

        # create and show window
        self._window = MainWindow(
            show_shell=self._show_shell,
            show_events=self._show_events,
            show_status=self._show_status,
            show_modules=self._show_modules,
            widgets=self._custom_widgets,
            sidebar=self._custom_sidebar_widgets,
            on_logout=self._request_logout if self._standalone else None,
        )
        await self._window.open(
            module=self,
            comm=self.comm,
            vfs=self.vfs,
            observer=self._observer,
        )
        self._window.show()

    def _request_logout(self) -> None:
        """Wired to MainWindow's "Log out" button (standalone mode only). Closes the current
        window/session immediately -- like a real logout, not a "maybe" -- then schedules the
        async part (closing the comm, showing the login window again) as a background task,
        since Qt click handlers are synchronous.
        """
        if self._logging_out:
            return  # already logging out -- ignore a repeat click
        self._logging_out = True

        if self._window is not None:
            self._window.close_for_logout()
            self._window.deleteLater()
            self._window = None

        asyncio.create_task(self._logout())

    async def _logout(self) -> None:
        """Closes the current comm, then shows the login window and reconnects with whatever it
        resolves to -- all within the same running Application/event loop, so Ctrl+C and the
        eventual real "Quit" still reach this exact module instance (see
        specs/plans/gui-login-window.md for why a brand new GUI() instance would leave
        Application's own bookkeeping stale instead).

        By the time this runs, MainWindow._request_logout() has already closed the old window --
        there's no session left to fall back to, so any failure here (the user closes the login
        window without connecting, or the reconnect itself fails) is reported via an error dialog
        and the app then quits cleanly, rather than limping on with no window and no comm.
        """
        old_comm = self._comm
        if old_comm is not None:
            await old_comm.close()

        from .login import show_login_and_connect

        try:
            new_comm = await show_login_and_connect()
        except asyncio.CancelledError:
            log.info("Login window closed without connecting; nothing left to do but quit.")
            self.quit()
            return
        except Exception as e:
            log.exception("Could not build a new connection.")
            await QAsyncMessageBox.critical(None, "Log out", f"Could not reconnect: {e}\n\nClosing the app.")
            self.quit()
            return
        finally:
            self._logging_out = False

        self._comm = new_comm
        try:
            await self.startup()
        except Exception as e:
            log.exception("Reconnecting with the new account failed.")
            await QAsyncMessageBox.critical(None, "Log out", f"Could not reconnect: {e}\n\nClosing the app.")
            self.quit()

    async def get_fits_header_before(
        self, namespaces: list[str] | None = None, **kwargs: Any
    ) -> dict[str, FitsHeaderEntry]:
        """Returns FITS header for the current status of this module.

        Args:
            namespaces: If given, only return FITS headers for the given namespaces.

        Returns:
            Dictionary containing FITS headers.
        """
        if self._window is not None:
            return self._window.get_fits_headers(namespaces)
        else:
            return {}
