from __future__ import annotations

import asyncio
import logging
from abc import ABC, ABCMeta
from collections.abc import Coroutine
from typing import (
    List,
    Dict,
    Tuple,
    Any,
    Union,
    TypeVar,
    Optional,
    Callable,
)

from PyQt5 import QtWidgets, QtGui, QtCore
from astroplan import Observer

from pyobs.comm import Comm, Proxy
from pyobs.interfaces import IModule
from pyobs.object import create_object
from pyobs.utils.enums import ModuleState
from pyobs.vfs import VirtualFileSystem
import pyobs.utils.exceptions as exc
from .utils import QAsyncMessageBox

log = logging.getLogger(__name__)

WidgetClass = TypeVar("WidgetClass")


class BaseWindow:
    def __init__(self) -> None:
        """Base class for MainWindow and all widgets."""
        self.modules: List[Proxy] = []
        self.comm: Optional[Comm] = None
        self.observer: Optional[Observer] = None
        self.vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None
        self._base_widgets: List[BaseWidget] = []

    @property
    def module(self) -> Optional[Proxy]:
        """Returns the first module in the list or None, if list is empty"""
        return self.modules[0] if len(self.modules) > 0 else None

    def module_by_name(self, name: str) -> Optional[Proxy]:
        """Return the module with the given name or None, if not exists.

        Args:
            name: Name of module to return.

        Returns:
            Module or None.
        """

        # loop all modules and check name
        for module in self.modules:
            if module.name == name:
                return module

        # nothing found
        return None

    def modules_by_interface(self, interface: Any) -> List[Proxy]:
        """Returns all modules that implement the given interface.

        Args:
            interface: Interface that modules must implement.

        Returns:
            List of modules.
        """
        return list(filter(lambda m: isinstance(m, interface), self.modules))

    def module_by_interface(self, interface: Any) -> Optional[Proxy]:
        """Returns first modules that implement the given interface, or None, if no exist.

        Args:
            interface: Interface that module must implement.

        Returns:
            Module or None.
        """
        modules = self.modules_by_interface(interface)
        return None if len(modules) == 0 else modules[0]

    def create_widget(self, config: Union[Dict[str, Any], type], **kwargs: Any) -> "BaseWidget":
        """Creates new widget.

        Args:
            config: Config to create widget from.

        Returns:
            New widget.
        """

        # create it
        if isinstance(config, dict):
            widget = create_object(config, **kwargs)
        elif isinstance(config, type):
            widget = config(**kwargs)
        else:
            raise ValueError("Wrong type.")

        # check and return widget
        if isinstance(widget, BaseWidget):
            self._base_widgets.append(widget)
            return widget
        else:
            raise ValueError("Invalid widget.")

    async def open(
        self,
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        # store
        self.modules = [] if modules is None else modules
        self.vfs = vfs
        self.comm = comm
        self.observer = observer

        """Open all widgets."""
        for widget in self._base_widgets:
            await self._open_child(widget)

    async def _open_child(self, widget: BaseWidget):
        await widget.open(modules=self.modules, vfs=self.vfs, comm=self.comm, observer=self.observer)


class BaseWidget(BaseWindow):
    _show_error = QtCore.pyqtSignal(str)
    _enable_buttons = QtCore.pyqtSignal(list, bool)

    def __init__(
        self,
        update_func: Optional[Callable[[], Any]] = None,
        update_interval: float = 1,
        *args: Any,
        **kwargs: Any,
    ):
        BaseWindow.__init__(self)

        # signals
        self._show_error.connect(self.show_error)
        self._enable_buttons.connect(self.enable_buttons)

        # update
        self._update_func = update_func
        self._update_interval = update_interval
        self._update_task: Optional[Any] = None

        # sidebar
        self.sidebar_widgets: List[BaseWidget] = []
        self.sidebar_layout: Optional[QtWidgets.QVBoxLayout] = None

        # button to extract to window
        self.extract_window_button: Optional[QtWidgets.QToolButton] = None
        self._windows: List[QtWidgets.QDialog] = []

        # has it been initialized?
        self._initialized = False

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self.extract_window_button:
            self.extract_window_button.move(self.width() - 20, 0)

    def show_extract_button(self, klass, title):
        # button to extract to window
        self.extract_window_button = QtWidgets.QToolButton(self)
        # self.extract_window_button.setText("X")
        self.extract_window_button.setIcon(QtGui.QIcon(":/resources/arrow-up-right-from-square-solid.svg"))
        self.colorize_button(self.extract_window_button, QtCore.Qt.darkCyan)
        self.extract_window_button.move(self.width() - 20, 0)
        self.extract_window_button.resize(20, 20)
        self.extract_window_button.raise_()

        # method for creating new window
        def create_window():
            # create dialog and add widget
            dialog = QtWidgets.QDialog()
            dialog.setWindowTitle(title)
            layout = QtWidgets.QVBoxLayout()
            dialog.setLayout(layout)
            widget = klass(dialog)
            layout.addWidget(widget)

            # open it
            asyncio.create_task(self._open_child(widget))

            # show dialog and store it
            dialog.show()
            self._windows.append(dialog)

        # connect
        self.extract_window_button.clicked.connect(create_window)

    async def add_to_sidebar(self, widget: BaseWidget) -> None:
        # if no layout exists on sidebar, create it
        if self.sidebar_layout is None:
            self.sidebar_layout = QtWidgets.QVBoxLayout()
            self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
            spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.sidebar_layout.addItem(spacer_item)
            self.widgetSidebar.setLayout(self.sidebar_layout)

        # open it
        await self._open_child(widget)

        # append widget
        self.sidebar_widgets.append(widget)
        self.sidebar_layout.insertWidget(len(self.sidebar_widgets) - 1, widget)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        # run in loop
        asyncio.create_task(self._showEvent(event))

    async def _showEvent(self, event: QtGui.QShowEvent) -> None:
        if self._initialized is False and hasattr(self, "_init"):
            await self._init()
            self._initialized = True

        if self._update_func:
            # start update task
            self._update_task = asyncio.create_task(self._update_loop())

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # run in loop
        asyncio.create_task(self._hide_event(event))

    async def _hide_event(self, event: QtGui.QHideEvent) -> None:
        # stop task
        if self._update_task is not None:
            self._update_task.cancel()
            try:
                await self._update_task
            except asyncio.CancelledError:
                pass
            finally:
                self._update_task = None

    async def _update_loop(self) -> None:
        while True:
            try:
                # get module state
                if isinstance(self.module, IModule):
                    state = await self.module.get_state()
                    self.setEnabled(state == ModuleState.READY)
                    if state != ModuleState.READY:
                        return

                # call update function
                if self._update_func is not None:
                    await self._update_func()

                # sleep a little
                await asyncio.sleep(1)

            except exc.PyObsError:
                # ignore these and sleep a little
                await asyncio.sleep(1)

    def run_background(self, method: Callable[..., Coroutine[Any, Any, None]], *args: Any, **kwargs: Any) -> None:
        asyncio.create_task(self._background_task(method, *args, **kwargs))

    async def _background_task(
        self, method: Callable[..., Coroutine[Any, Any, None]], *args: Any, disable: Any = None, **kwargs: Any
    ) -> None:
        # make disable an empty list or a list of widgets
        disable = [] if disable is None else [disable] if not hasattr(disable, "__iter__") else disable

        # disable widgets
        self._enable_buttons.emit(disable, False)

        # call method
        try:
            await method(*args, **kwargs)
        except exc.PyObsError as e:
            await self.show_error(e)
        except Exception as e:
            log.exception("An error occurred.")
            await QAsyncMessageBox.warning(self, "Error", str(e))
        finally:
            # enable widgets
            self._enable_buttons.emit(disable, True)

    async def show_error(self, exception: exc.PyObsError) -> None:
        err = str(exception)
        title, message = err.split(":") if ":" in err else ("Error", err)
        await QAsyncMessageBox.warning(self, title, message)

    def enable_buttons(self, widgets: List[QtWidgets.QWidget], enable: bool) -> None:
        for w in widgets:
            w.setEnabled(enable)

    def get_fits_headers(self, namespaces: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Tuple[Any, str]]:
        """Returns FITS header for the current status of this module.

        Args:
            namespaces: If given, only return FITS headers for the given namespaces.

        Returns:
            Dictionary containing FITS headers.
        """
        hdr = {}
        for widget in self.sidebar_widgets:
            for k, v in widget.get_fits_headers().items():
                hdr[k] = v
        return hdr

    def colorize_button(self, button: Any, background: Any, black_on_white: bool = True) -> None:
        # get palette
        pal = button.palette()

        # change active colors
        pal.setColor(QtGui.QPalette.Button, background)
        pal.setColor(
            QtGui.QPalette.ButtonText,
            QtCore.Qt.black if black_on_white else QtCore.Qt.white,
        )

        # change disabled colors
        pal.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, QtCore.Qt.gray)

        # set palette again
        button.setPalette(pal)
