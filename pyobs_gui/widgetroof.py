from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces.proxies import IDomeProxy
from pyobs_gui.basewidget import BaseWidget
from .qt.widgetroof import Ui_WidgetRoof


class WidgetRoof(BaseWidget, Ui_WidgetRoof):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs):
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)

        # status
        self.motion_status = None
        self.azimuth = None

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

        # azimuth
        if isinstance(self.module, IDomeProxy):
            _, self.azimuth = self.module.get_altaz().wait()

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
        if self.azimuth is None:
            self.labelAzimuth.setText('N/A')
        else:
            self.labelAzimuth.setText('%.1f°' % self.azimuth)
