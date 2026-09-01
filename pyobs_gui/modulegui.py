from __future__ import annotations

import sys
from typing import Any, cast, TYPE_CHECKING
import qasync  # type: ignore
from qasync import QEventLoop  # noqa: F401
from PySide6 import QtWidgets, QtGui  # type: ignore

from pyobs.interfaces import FitsHeaderEntry, IFitsHeaderBefore
from pyobs.modules import Module
from .base import BaseWindow
from .mainwindow import ModulePage, collect_main_widgets, open_module_page

if TYPE_CHECKING:
    import asyncio


class ModuleWindow(QtWidgets.QMainWindow, BaseWindow):  # type: ignore
    def __init__(self, gui_module: ModuleGUI, **kwargs: Any):
        QtWidgets.QMainWindow.__init__(self)
        BaseWindow.__init__(self)
        self.gui_module = gui_module

    async def open(self, module: Module | None = None, **kwargs: Any) -> None:  # type: ignore
        """Open module."""

        # set up comm/vfs/observer/modules first -- _base_widgets is still empty at this point
        # (no widget has been created yet), so this loop is a no-op; the main widget(s) below
        # are opened explicitly via open_module_page() instead, since that also needs D5's
        # per-tab failure handling and the sidebar-fill steps, which the generic _base_widgets
        # auto-open loop doesn't provide
        modules = [module.name] if module is not None else []
        await BaseWindow.open(self, modules=modules, **kwargs)

        # what do we have? (same registry-driven matching as MainWindow, D1/D2; ModuleWindow has
        # no custom-config surface, so `custom` is always empty -- parity here means the
        # multi-widget/sidebar behavior, not config, same as today)
        if module is not None:
            main_choices, sidebar_preferred_choices = collect_main_widgets(module, self.create_widget)
            if main_choices:
                page = self.create_widget(ModulePage, choices=main_choices, sidebar_preferred=sidebar_preferred_choices)
                self.setCentralWidget(page)
                # raise on total failure so it propagates the same way a failing widget.open()
                # did in the old single-widget code, instead of silently leaving an empty page
                if not await open_module_page(
                    page, module.name, self.comm, self.observer, self.vfs, self.create_widget
                ):
                    raise RuntimeError(f"All main widgets failed to open for {module.name}")

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        self.gui_module.quit()


class ModuleGUI(Module, IFitsHeaderBefore):
    __module__ = "pyobs_gui"

    app: QtWidgets.QApplication | None = None

    def __init__(
        self,
        module: dict[str, Any],
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
        self._window: ModuleWindow | None = None
        self._module = self.add_child_object(module, Module, own_comm=False)

    @staticmethod
    def new_event_loop() -> asyncio.AbstractEventLoop:
        ModuleGUI.app = QtWidgets.QApplication(sys.argv)
        return cast("asyncio.AbstractEventLoop", qasync.QEventLoop(ModuleGUI.app))

    async def open(self) -> None:
        """Open module."""
        await Module.open(self)

        # open module
        await self._module.open()

        # create new mainwindow
        self._window = ModuleWindow(self)
        await self._window.open(
            module=self._module,
            comm=self._comm,
            vfs=self._vfs,
            observer=self._observer,
        )
        self._window.show()

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
            return self._window.get_fits_headers(namespaces)  # pyrefly: ignore [missing-attribute]
        else:
            return {}
