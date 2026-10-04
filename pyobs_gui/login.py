"""Async factory for pyobs.application.Application's module_factory contract -- see
specs/plans/gui-interactive-login.md and specs/plans/gui-login-window.md.

Shows LoginWindow, waits for Connect, then builds an XmppComm + GUI from the result. Runs inside
the already-running event loop (see Application._main()), so it can await anything it needs to
before the module/comm connection exists at all.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from pyobs.comm.xmpp import XmppComm

from .gui import GUI
from .loginwindow import ConnectionRequest, LoginWindow

log = logging.getLogger(__name__)


def settings_key(request: ConnectionRequest) -> str:
    """Key of the settings in the settings file: the saved account id, or for a connection that
    wasn't saved the bare JID (so its settings persist too)."""
    return request.account_id or "jid:" + request.jid.split("/")[0]


async def show_login_and_connect() -> tuple[XmppComm, str]:
    """Shows the login window, waits for the user to click Connect (or raises
    asyncio.CancelledError if they close the window instead -- see LoginWindow.closeEvent), then
    returns a fresh XmppComm built from the result, together with the key of its settings (see
    `settings_key`).

    Used both for the initial standalone startup (login_and_build_gui) and for GUI's "Log out"
    flow (GUI._logout), which shows this same window again without tearing down the running
    Application/event loop.
    """
    window = LoginWindow()
    window.show()
    try:
        request = await window.wait_for_connect()
    except asyncio.CancelledError:
        log.info("Login window closed without connecting.")
        raise
    finally:
        window.close()

    log.info("Connecting as %s...", request.jid)
    comm = XmppComm(
        jid=request.jid,
        password=request.password,
        server=request.server,
        use_tls=request.use_tls,
        ignore_cert_errors=request.insecure_skip_tls,
    )
    return comm, settings_key(request)


async def login_and_build_gui(**gui_kwargs: Any) -> GUI:
    """Shows the login window, waits for the user to click Connect (or cancels if they close the
    window instead -- see LoginWindow.closeEvent), then returns a GUI built from the result.

    Args:
        gui_kwargs: Passed through to GUI(...) (show_shell, show_events, widgets, etc.) --
            everything except `comm`, which is built here from the login window's result.
    """
    comm, key = await show_login_and_connect()
    return GUI(comm=comm, standalone=True, settings_key=key, **gui_kwargs)


__all__ = ["login_and_build_gui", "settings_key", "show_login_and_connect"]
