import threading
import logging

from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox


log = logging.getLogger(__name__)


class BaseWidget(QtWidgets.QWidget):
    _show_error = pyqtSignal(str)
    _enable_buttons = pyqtSignal(list, bool)

    def __init__(self, update_func=None, update_interval: float = 1, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)

        # signals
        self._show_error.connect(self.show_error)
        self._enable_buttons.connect(self.enable_buttons)

        # update thread
        self._update_func = update_func
        self._update_interval = update_interval
        self._update_thread = None
        self._update_thread_event = None

        # sidebar
        self.sidebar_widgets = []
        self.sidebar_layout = None

    def add_to_sidebar(self, widget):
        # if no layout exists on sidebar, create it
        if self.sidebar_layout is None:
            self.sidebar_layout = QtWidgets.QVBoxLayout(self)
            self.sidebar_layout.setContentsMargins(0, 0, 0, 0)
            spacer_item = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
            self.sidebar_layout.addItem(spacer_item)
            self.widgetSidebar.setLayout(self.sidebar_layout)

        # append widget
        self.sidebar_widgets.append(widget)
        self.sidebar_layout.insertWidget(0, widget)

    def enter(self):
        # sidebar
        for sb in self.sidebar_widgets:
            sb.enter()

        if self._update_func:
            # create event for update thread to close
            self._update_thread_event = threading.Event()

            # start update thread
            self._update_thread = threading.Thread(target=self._update_loop_thread)
            self._update_thread.start()

    def leave(self):
        # sidebar
        for sb in self.sidebar_widgets:
            sb.leave()

        if self._update_func:
            # stop thread
            self._update_thread_event.set()
            self._update_thread.join()
            self._update_thread = None
            self._update_thread_event = None

    def _update_loop_thread(self):
        while not self._update_thread_event.is_set():
            try:
                # call update function
                self._update_func()
            except:
                pass

            # sleep a little
            self._update_thread_event.wait(1)

    def run_async(self, method, *args, **kwargs):
        threading.Thread(target=self._async_thread, args=(method, *args), kwargs=kwargs).start()

    def _async_thread(self, method, *args,  disable=None, **kwargs):
        # make disable an empty list or a list of widgets
        disable = [] if disable is None else [disable] if not hasattr(disable, '__iter__') else disable

        # disable widgets
        self._enable_buttons.emit(disable, False)

        # call method
        try:
            method(*args, **kwargs)
        except Exception as e:
            log.exception("error")
            self._show_error.emit(str(e))
        finally:
            # enable widgets
            self._enable_buttons.emit(disable, True)

    def show_error(self, message):
        QMessageBox.warning(self, 'Error', message)

    def enable_buttons(self, widgets, enable):
        [w.setEnabled(enable) for w in widgets]
