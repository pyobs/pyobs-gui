from __future__ import annotations
import asyncio
import sys
from typing import List, Dict, Tuple, Any, Optional

import qasync
from qasync import QEventLoop  # type: ignore
from PyQt5 import QtWidgets, QtGui

from pyobs.interfaces import IFitsHeaderBefore
from pyobs.modules import Module
from .base import BaseWindow
from .mainwindow import MainWindow, DEFAULT_WIDGETS


class ModuleWindow(QtWidgets.QMainWindow, BaseWindow):
    def __init__(self, gui_module: ModuleGUI, **kwargs: Any):
        QtWidgets.QMainWindow.__init__(self)
        BaseWindow.__init__(self)
        self.gui_module = gui_module

    async def open(self, module: Optional[Module] = None, **kwargs: Any) -> None:
        """Open module."""

        # what do we have?
        widget, icon = None, None
        for interface, klass in DEFAULT_WIDGETS.items():
            if isinstance(module, interface):
                widget = self.create_widget(klass)
                self.setCentralWidget(widget)
                break

        # open widgets
        await BaseWindow.open(self, modules=[module], **kwargs)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.gui_module.quit()


class ModuleGUI(Module, IFitsHeaderBefore):
    __module__ = "pyobs_gui"

    app: Optional[QtWidgets.QApplication] = None

    def __init__(
        self,
        module: Dict[str, Any],
        *args: Any,
        **kwargs: Any,
    ):
        """Inits a new module GUI.

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
        self._module = self.add_child_object(module, Module, own_comm=False)

    @staticmethod
    def new_event_loop() -> asyncio.AbstractEventLoop:
        ModuleGUI.app = QtWidgets.QApplication(sys.argv)
        return qasync.QEventLoop(ModuleGUI.app)

    async def open(self) -> None:
        """Open module."""
        await Module.open(self)

        # open module
        await self._module.open()

        # create new mainwindow
        self._window = ModuleWindow(self)
        await self._window.open(
            module=self._module,
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
