import threading
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import aplpy

from pyobs.events import ExposureStatusChangedEvent, NewImageEvent
from pyobs.interfaces import ICamera, ICameraBinning, ICameraWindow, ICooling, IFilters
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.basewidget import BaseWidget
from pyobs_gui.widgetcooling import WidgetCooling
from pyobs_gui.widgetfilter import WidgetFilter
from .qt.widgetroof import Ui_WidgetRoof


class WidgetRoof(BaseWidget, Ui_WidgetRoof):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, environment, parent=None):
        BaseWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: IRoof
        self.comm = comm        # type: Comm
        self.environment = environment   # type: Environment

        # status
        self.motion_status = None
        self.percent_open = None

        # update thread
        self._update_thread = None
        self._update_thread_event = None

        # connect signals
        self.buttonOpen.clicked.connect(lambda: self.run_async(self.module.open_roof))
        self.buttonClose.clicked.connect(lambda: self.run_async(self.module.close_roof))
        self.buttonStop.clicked.connect(lambda: self.run_async(self.module.stop_roof))
        self.signal_update_gui.connect(self.update_gui)

        # initial values
        threading.Thread(target=self._init).start()

    def _init(self):
        # get status and update gui
        self.motion_status = self.module.get_motion_status()
        self.signal_update_gui.emit()

    def enter(self):
        BaseWidget.enter(self)

        # create event for update thread to close
        self._update_thread_event = threading.Event()

        # start update thread
        self._update_thread = threading.Thread(target=self._update)
        self._update_thread.start()

    def leave(self):
        BaseWidget.leave(self)

        # stop thread
        self._update_thread_event.set()
        self._update_thread.join()
        self._update_thread = None
        self._update_thread_event = None

    def _update(self):
        while not self._update_thread_event.is_set():
            try:
                # motion status
                self.motion_status = self.module.get_motion_status()

                # open status
                self.percent_open = self.module.get_percent_open()

                # signal GUI update
                self.signal_update_gui.emit()
            except:
                pass

            # sleep a little
            self._update_thread_event.wait(1)

    def update_gui(self):
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # set status
        if self.motion_status is not None:
            self.labelStatus.setText(self.motion_status.name)

        # open
        if self.percent_open is not None:
            if self.percent_open == 0:
                self.labelOpen.setText('CLOSED')
            elif self.percent_open == 0:
                self.labelOpen.setText('OPENED')
            else:
                self.labelOpen.setText(str(int(self.percent_open)) + '%')

    def open_roof(self):
        pass

    def close_roof(self):
        pass

    def stop_roof(self):
        pass
