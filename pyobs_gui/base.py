from __future__ import annotations

import asyncio
import contextlib
import logging
from typing import TYPE_CHECKING, Any, Callable, Type, TypeVar, overload

import pyobs.utils.exceptions as exc
from pyobs.interfaces import IModule
from pyobs.object import create_object
from pyobs.utils.enums import ModuleState
from PySide6 import QtCore, QtGui, QtWidgets  # type: ignore

from .utils import QAsyncMessageBox

if TYPE_CHECKING:
    from collections.abc import Coroutine

    from astroplan import Observer
    from pyobs.comm import Comm
    from pyobs.events import Event
    from pyobs.interfaces import FitsHeaderEntry
    from pyobs.vfs import VirtualFileSystem

log = logging.getLogger(__name__)

WidgetClass = TypeVar("WidgetClass", bound="BaseWidget")


async def show_remote_error(parent: QtWidgets.QWidget, exception: Exception) -> None:
    """Show a remote-call failure to the user.

    Single shared path for surfacing exceptions from remote method calls: `PyobsError`
    (domain errors like `MoveError`, and transport errors like `RemoteError`) shows a warning
    box titled with the exception class; any other `Exception` is logged and shown as a plain
    warning. Used by `BaseWidget._background_task()` (everything routed through
    `run_background()`) and by non-`BaseWidget` callers like `StatusItem`.
    """
    if isinstance(exception, exc.PyobsError):
        # PyobsError.__str__ already prefixes the class name ("<MoveError> msg"); the class name
        # is the dialog title, so show only the message itself
        await QAsyncMessageBox.warning(parent, type(exception).__name__, exception.message or str(exception))
    else:
        log.exception("An error occurred.")
        await QAsyncMessageBox.warning(parent, "Error", str(exception))


async def cancel_and_drain(task: asyncio.Task[Any]) -> None:
    """Cancel a task and await its unwind, swallowing the resulting CancelledError."""
    task.cancel()
    with contextlib.suppress(asyncio.CancelledError):
        await task


class BaseWindow:
    def __init__(self) -> None:
        """Base class for MainWindow and all widgets."""
        self.modules: list[str] = []
        self._comm: Comm | None = None
        self.observer: Observer | None = None
        self.vfs: VirtualFileSystem | dict[str, Any] | None = None
        self._base_widgets: list[BaseWidget] = []

    @property
    def comm(self) -> Comm:
        if self._comm is None:
            raise ValueError("No comm object.")
        return self._comm

    @property
    def module(self) -> str:
        """Returns the first module in the list or None, if list is empty"""
        return self.modules[0]

    def modules_by_interface(self, interface: Any) -> list[str]:
        """Returns all modules that implement the given interface.

        Args:
            interface: Interface that modules must implement.

        Returns:
            List of modules.
        """
        return list(filter(lambda m: isinstance(m, interface), self.modules))

    def module_by_interface(self, interface: Any) -> str | None:
        """Returns first modules that implement the given interface, or None, if no exist.

        Args:
            interface: Interface that module must implement.

        Returns:
            Module or None.
        """
        modules = self.modules_by_interface(interface)
        return None if len(modules) == 0 else modules[0]

    @overload
    def create_widget(self, config: type[WidgetClass], **kwargs: Any) -> WidgetClass: ...
    @overload
    def create_widget(self, config: dict[str, Any], **kwargs: Any) -> "BaseWidget": ...
    def create_widget(self, config: dict[str, Any] | type, **kwargs: Any) -> "BaseWidget":
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
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        # store
        self.modules = [] if modules is None else modules
        self.vfs = vfs
        self._comm = comm
        self.observer = observer

        """Open all widgets."""
        for widget in self._base_widgets:
            await self._open_child(widget)

    async def _open_child(self, widget: BaseWidget) -> None:
        await widget.open(modules=self.modules, vfs=self.vfs, comm=self.comm, observer=self.observer)


class BaseWidget(BaseWindow, QtWidgets.QWidget):  # type: ignore
    _enable_buttons = QtCore.Signal(list, bool)

    def __init__(
        self,
        update_func: Callable[[], Any] | None = None,
        update_interval: float = 1,
        *args: Any,
        **kwargs: Any,
    ):
        BaseWindow.__init__(self)
        QtWidgets.QWidget.__init__(self)

        # signals
        self._enable_buttons.connect(self.enable_buttons)

        # update
        self._update_func = update_func
        self._update_interval = update_interval
        self._update_task: Any | None = None

        # sidebar
        self.sidebar_widgets: list[BaseWidget] = []
        self.sidebar_layout: QtWidgets.QVBoxLayout | None = None

        # button to extract to window
        self.extract_window_button: QtWidgets.QToolButton | None = None
        self._windows: list[QtWidgets.QDialog] = []

        # has it been initialized?
        self._initialized = False

        # memoized one-shot init task -- two rapid show/hide/show cycles must not run _init()
        # twice concurrently (see _showEvent)
        self._init_task: asyncio.Task[Any] | None = None

        # keys of _init_once() sub-steps that already completed, so a retried _init() (see
        # _showEvent) skips steps that already ran instead of re-subscribing to comm state
        self._init_steps_done: set[str] = set()

        # methods this GUI is permitted to invoke on self.module; None until fetched or if the
        # fetch failed, meaning "treat everything as permitted"
        self._permitted_methods: set[str] | None = None

        # (event_class, handler) pairs registered via self.register_event(), so discard() can
        # unregister them all -- comm.register_event() has no automatic per-client teardown like
        # subscribe_state()/subscribe_presence() do, since a handler isn't inherently tied to one
        # remote module, so whoever registers it is responsible for unregistering it
        self._registered_event_handlers: list[tuple[type[Event], Callable[[Event, str], Any]]] = []

    def resizeEvent(self, a0: QtGui.QResizeEvent) -> None:
        if self.extract_window_button:
            self.extract_window_button.move(self.width() - 20, 0)

    def show_extract_button(self, klass: Type[Any], title: str) -> None:
        # button to extract to window
        self.extract_window_button = QtWidgets.QToolButton(self)
        # self.extract_window_button.setText("X")
        self.extract_window_button.setIcon(QtGui.QIcon(":/resources/arrow-up-right-from-square-solid.svg"))
        self.colorize_button(self.extract_window_button, QtCore.Qt.GlobalColor.darkCyan)
        self.extract_window_button.move(self.width() - 20, 0)
        self.extract_window_button.resize(20, 20)
        self.extract_window_button.raise_()

        # method for creating new window
        def create_window() -> None:
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
            spacer_item = QtWidgets.QSpacerItem(
                20, 40, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding
            )
            self.sidebar_layout.addItem(spacer_item)
            if hasattr(self, "widgetSidebar"):
                self.widgetSidebar.setLayout(self.sidebar_layout)

        # open it -- a failing sidebar widget is logged and dropped rather than left to propagate:
        # otherwise one flaky sidebar widget (e.g. a filter wheel briefly unreachable) would kill
        # the whole page it's attached to, including every already-open main widget/tab
        try:
            await self._open_child(widget)
        except asyncio.CancelledError:
            raise
        except Exception:
            log.exception("Failed to open sidebar widget %s; dropping it.", type(widget).__name__)
            await widget.discard()
            return

        # append widget
        self.sidebar_widgets.append(widget)
        self.sidebar_layout.insertWidget(len(self.sidebar_widgets) - 1, widget)

    async def register_event(self, event_class: type[Event], handler: Callable[[Event, str], Any]) -> None:
        """Register an event handler through comm, tracked so discard() can unregister it later.

        Widgets that are created/destroyed per connected client (see MAIN_WIDGETS in
        mainwindow.py) must use this instead of calling self.comm.register_event() directly,
        so their handler stops firing once the widget is discarded.
        """
        await self.comm.register_event(event_class, handler)
        self._registered_event_handlers.append((event_class, handler))

    async def discard(self) -> None:
        """Tear down everything this widget registered with comm, and recursively discard
        its sidebar widgets.

        Must be called (e.g. from mainwindow._client_disconnected) whenever a widget is
        removed from the UI -- otherwise a handler registered via register_event() lingers
        in Comm._event_handlers forever, keeping this widget alive and still reacting to
        events for as long as the app runs.
        """
        # cancel a still-in-flight one-time _init() first: comm's own disconnect-triggered
        # subscription cleanup (Comm._client_disconnected) runs before this method is called,
        # so a subscribe_state() call inside _init_task that resolves afterwards would leak a
        # subscription bound to this now-discarded widget -- the same stale-callback crash
        # class this method otherwise guards against
        if self._init_task is not None:
            await cancel_and_drain(self._init_task)
            self._init_task = None

        for event_class, handler in self._registered_event_handlers:
            await self.comm.unregister_event(event_class, handler)
        self._registered_event_handlers.clear()

        for widget in self.sidebar_widgets:
            await widget.discard()

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        # run in loop
        asyncio.create_task(self._showEvent(event))

    async def _showEvent(self, event: QtGui.QShowEvent) -> None:
        if self._initialized is False:
            if self._init_task is None:
                self._init_task = asyncio.create_task(self._run_init())
            try:
                await self._init_task
            except Exception:
                # transient init failure (e.g. a comm RPC hiccup): log, and allow a retry on
                # the next show instead of leaving the widget permanently marked initialized
                log.exception("Init of %s failed; will retry on next show.", type(self).__name__)
                self._init_task = None

        if self._update_func:
            # start update task
            self._update_task = asyncio.create_task(self._update_loop())

    async def _run_init(self) -> None:
        await self._init()
        self._initialized = True

    async def _init(self) -> None:
        """Default no-op init. Widgets with one-time subscription/state setup override this;
        _showEvent memoizes the call so it runs exactly once per widget lifetime."""

    async def _init_once(self, key: str, coro_func: Callable[..., Coroutine[Any, Any, None]], *args: Any) -> None:
        """Run one sub-step of _init() at most once across retries.

        _showEvent retries the whole _init() after a partial failure (e.g. one of several
        gathered comm.subscribe_state() calls raising while its siblings already subscribed).
        comm.subscribe_state() unconditionally appends to comm's subscription list with no
        deduplication, so a sub-step that already succeeded must not run again on retry --
        override _init() and wrap each independent, subscribing sub-step in this instead of
        calling it directly.
        """
        if key in self._init_steps_done:
            return
        await coro_func(*args)
        self._init_steps_done.add(key)

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
        consecutive_failures = 0
        while True:
            try:
                # get module state
                module = self.module
                client_state = self.comm.get_client_state(module)
                if client_state is not None:
                    state, _ = client_state
                    self.setEnabled(state == ModuleState.READY)
                    if state != ModuleState.READY:
                        return

                # call update function
                if self._update_func is not None:
                    await self._update_func()

                # sleep a little
                await asyncio.sleep(1)
                consecutive_failures = 0

            except (exc.PyobsError, IndexError) as e:
                # background polling failures must not pop a dialog per failed poll -- log the
                # first failure, then every 60th (~once a minute at the 1s poll interval)
                consecutive_failures += 1
                if consecutive_failures % 60 == 1:
                    log.warning("Update of %s failed: %s", self.module, e)
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
        except Exception as e:
            await show_remote_error(self, e)
        finally:
            # enable widgets
            self._enable_buttons.emit(disable, True)

    def enable_buttons(self, widgets: list[QtWidgets.QWidget], enable: bool) -> None:
        for w in widgets:
            w.setEnabled(enable)

    async def _fetch_permitted_methods(self) -> None:
        # leaves _permitted_methods at None on failure, so permitted() falls back to "everything
        # allowed" - an actual denial still surfaces via ForbiddenError in _background_task
        if not hasattr(IModule, "get_permitted_methods"):
            # pyobs-core older than the ACL feature (still within our supported version range)
            return
        try:
            async with self.comm.proxy(self.module, IModule) as proxy:
                self._permitted_methods = set(await proxy.get_permitted_methods())
        except exc.PyobsError:
            self._permitted_methods = None

    def permitted(self, method: str) -> bool:
        """Returns whether this GUI is permitted to invoke the given method on self.module."""
        return self._permitted_methods is None or method in self._permitted_methods

    def get_fits_headers(self, namespaces: list[str] | None = None, **kwargs: Any) -> dict[str, FitsHeaderEntry]:
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

    @staticmethod
    def colorize_button(button: Any, background: Any, black_on_white: bool = True) -> None:
        # get palette
        pal = button.palette()

        # change active colors
        pal.setColor(QtGui.QPalette.ColorRole.Button, background)
        pal.setColor(
            QtGui.QPalette.ColorRole.ButtonText,
            QtCore.Qt.GlobalColor.black if black_on_white else QtCore.Qt.GlobalColor.white,
        )

        # change disabled colors
        pal.setColor(QtGui.QPalette.ColorGroup.Disabled, QtGui.QPalette.ColorRole.Button, QtCore.Qt.GlobalColor.gray)

        # set palette again
        button.setPalette(pal)
