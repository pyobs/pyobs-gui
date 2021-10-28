from __future__ import annotations
import threading
import logging
from typing import List, Dict, Tuple, Any, Union, TypeVar, Type, Optional, Callable, TYPE_CHECKING

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from astroplan import Observer

from pyobs.comm import Comm, Proxy
from pyobs.object import create_object
from pyobs.vfs import VirtualFileSystem
if TYPE_CHECKING:
    from pyobs.modules import Module


log = logging.getLogger(__name__)


WidgetClass = TypeVar('WidgetClass')


class BaseWidget(QtWidgets.QWidget):  # type: ignore
    _show_error = pyqtSignal(str)
    _enable_buttons = pyqtSignal(list, bool)

    def __init__(self, module: Optional[Proxy] = None, comm: Optional[Comm] = None,
                 observer: Optional[Observer] = None, vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
                 update_func: Optional[Callable[[], Any]] = None, update_interval: float = 1,
                 *args: Any, **kwargs: Any):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        # store
        self.module = module
        self.vfs = vfs
        self.comm = comm
        self.observer = observer

        # signals
        self._show_error.connect(self.show_error)
        self._enable_buttons.connect(self.enable_buttons)

        # update thread
        self._update_func = update_func
        self._update_interval = update_interval
        self._update_thread = threading.Thread()
        self._update_thread_event = threading.Event()

        # sidebar
        self.sidebar_widgets: List[BaseWidget] = []
        self.sidebar_layout = None

        # has it been initialized?
        self._initialized = False

    def create_widget(self, config: Union[Dict[str, Any], type], **kwargs: Any) -> BaseWidget:
        """Creates new widget.

        Args:
            config: Config to create widget from.

        Returns:
            New widget.
        """
        if isinstance(config, dict):
            widget = create_object(config, vfs=self.vfs, comm=self.comm, observer=self.observer, **kwargs)
        elif isinstance(config, type):
            widget = config(vfs=self.vfs, comm=self.comm, observer=self.observer, **kwargs)
        else:
            raise ValueError('Wrong type.')

        # check and return widget
        if isinstance(widget, BaseWidget):
            return widget
        else:
            raise ValueError('Invalid widget.')

    def add_to_sidebar(self, widget: BaseWidget) -> None:
        # if no layout exists on sidebar, create it
        if self.sidebar_layout is None:
            self.sidebar_layout = QtWidgets.QVBoxLayout()
            self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
            spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.sidebar_layout.addItem(spacer_item)
            self.widgetSidebar.setLayout(self.sidebar_layout)

        # append widget
        self.sidebar_widgets.append(widget)
        self.sidebar_layout.insertWidget(len(self.sidebar_widgets) - 1, widget)

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        if self._initialized is False and hasattr(self, '_init'):
            self._init()
            self._initialized = True

        if self._update_func:
            # create event for update thread to close
            self._update_thread_event = threading.Event()

            # start update thread
            self._update_thread = threading.Thread(target=self._update_loop_thread)
            self._update_thread.start()

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # stop thread
        if self._update_thread_event is not None:
            self._update_thread_event.set()

        # wait for it
        if self._update_thread.is_alive():
            self._update_thread.join()

    def _update_loop_thread(self) -> None:
        while not self._update_thread_event.is_set():
            try:
                # call update function
                self._update_func()
            except Exception as e:
                log.warning("Exception during GUIs update function: %s",
                            str(e))

            # sleep a little
            self._update_thread_event.wait(self._update_interval)

    def run_async(self, method: Any, *args: Any, **kwargs: Any) -> None:
        threading.Thread(target=self._async_thread, args=(method, *args), kwargs=kwargs).start()

    def _async_thread(self, method: Any, *args: Any, disable: Any = None, **kwargs: Any) -> None:
        # make disable an empty list or a list of widgets
        disable = [] if disable is None else [disable] if not hasattr(disable, '__iter__') else disable

        # disable widgets
        self._enable_buttons.emit(disable, False)

        # call method
        try:
            method(*args, **kwargs).wait()
        except Exception as e:
            log.exception("error")
            self._show_error.emit(str(e))
        finally:
            # enable widgets
            self._enable_buttons.emit(disable, True)

    def show_error(self, message: str) -> Any:
        QMessageBox.warning(self, 'Error', message)

    def enable_buttons(self, widgets: List[QtWidgets.QWidget], enable: bool) -> None:
        [w.setEnabled(enable) for w in widgets]

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
        pal.setColor(QtGui.QPalette.ButtonText, QtCore.Qt.black if black_on_white else QtCore.Qt.white)

        # change disabled colors
        pal.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Button, QtCore.Qt.gray)

        # set palette again
        button.setPalette(pal)
