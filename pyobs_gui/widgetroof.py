from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import IDome
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
        self.buttonOpen.clicked.connect(lambda: self.run_background(self.module.init))
        self.buttonClose.clicked.connect(lambda: self.run_background(self.module.park))
        self.buttonStop.clicked.connect(lambda: self.run_background(self.module.stop_motion))
        self.signal_update_gui.connect(self.update_gui)

    async def _init(self):
        # get status and update gui
        self.motion_status = await self.module.get_motion_status()
        self.signal_update_gui.emit()

    async def _update(self):
        # motion status
        self.motion_status = await self.module.get_motion_status()

        # azimuth
        if isinstance(self.module, IDome):
            _, self.azimuth = await self.module.get_altaz()

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
