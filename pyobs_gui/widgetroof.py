import threading
from PyQt5.QtCore import pyqtSignal
from astroplan import Observer

from pyobs_gui.basewidget import BaseWidget
from .qt.widgetroof import Ui_WidgetRoof


class WidgetRoof(BaseWidget, Ui_WidgetRoof):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, observer, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update)
        self.setupUi(self)
        self.module = module    # type: IRoof
        self.comm = comm        # type: Comm
        self.observer = observer   # type: Observer

        # status
        self.motion_status = None
        self.percent_open = None

        # connect signals
        self.buttonOpen.clicked.connect(lambda: self.run_async(self.module.init))
        self.buttonClose.clicked.connect(lambda: self.run_async(self.module.park))
        self.buttonStop.clicked.connect(lambda: self.run_async(self.module.stop_motion))
        self.signal_update_gui.connect(self.update_gui)

    def _init(self):
        # get status and update gui
        self.motion_status = self.module.get_motion_status().wait()
        self.signal_update_gui.emit()

    def _update(self):
        # motion status
        self.motion_status = self.module.get_motion_status().wait()

        # open status
        #self.percent_open = self.module.get_percent_open().wait()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self):
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # set status
        if self.motion_status is not None:
            self.labelStatus.setText(self.motion_status.value)

        # open
        if self.percent_open is not None:
            if self.percent_open == 0:
                self.labelOpen.setText('CLOSED')
            elif self.percent_open == 0:
                self.labelOpen.setText('OPENED')
            else:
                self.labelOpen.setText(str(int(self.percent_open)) + '%')
