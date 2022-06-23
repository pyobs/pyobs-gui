import asyncio
import sys
from typing import List, Dict, Tuple, Any, Optional

import qasync
from qasync import QEventLoop  # type: ignore
from PyQt5 import QtWidgets

from pyobs.interfaces import IFitsHeaderBefore
from pyobs.modules import Module
from .mainwindow import MainWindow


class GUI(Module, IFitsHeaderBefore):
    __module__ = "pyobs_gui"

    app: Optional[QtWidgets.QApplication] = None

    def __init__(
        self,
        show_shell: bool = True,
        show_events: bool = True,
        show_status: bool = True,
        show_modules: Optional[List[str]] = None,
        widgets: Optional[List[Dict[str, Any]]] = None,
        sidebar: Optional[List[Dict[str, Any]]] = None,
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
        """

        # init module
        Module.__init__(self, *args, **kwargs)
        self._window: Optional[MainWindow] = None
        self._show_shell = show_shell
        self._show_events = show_events
        self._show_status = show_status
        self._show_modules = show_modules
        self._custom_widgets = widgets
        self._custom_sidebar_widgets = sidebar

    @staticmethod
    def new_event_loop() -> asyncio.AbstractEventLoop:
        GUI.app = QtWidgets.QApplication(sys.argv)
        return qasync.QEventLoop(GUI.app)

    async def open(self) -> None:
        """Open module."""
        await Module.open(self)

        # create and show window
        self._window = MainWindow(
            show_shell=self._show_shell,
            show_events=self._show_events,
            show_status=self._show_status,
            show_modules=self._show_modules,
            widgets=self._custom_widgets,
            sidebar=self._custom_sidebar_widgets,
        )
        await self._window.open(
            module=self,
            comm=self.comm,
            vfs=self.vfs,
            observer=self.observer,
        )
        self._window.show()

    async def get_fits_header_before(
        self, namespaces: Optional[List[str]] = None, **kwargs: Any
    ) -> Dict[str, Tuple[Any, str]]:
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
