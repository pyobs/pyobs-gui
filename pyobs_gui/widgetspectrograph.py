import asyncio
import logging
from typing import Optional
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from astropy.io import fits

from pyobs.events import ExposureStatusChangedEvent, Event
from pyobs.interfaces import IAbortable, ISpectrograph
from pyobs.utils.enums import ExposureStatus
from pyobs_gui.basewidget import BaseWidget
from .widgetdatadisplay import WidgetDataDisplay

from .qt.widgetspectrograph import Ui_WidgetSpectrograph


log = logging.getLogger(__name__)


class WidgetSpectrograph(BaseWidget, Ui_WidgetSpectrograph):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs) -> None:
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)

        # variables
        self.new_spectrum = False
        self.spectrum_filename: Optional[str] = None
        self.spectrum: Optional[fits.PrimaryHDU] = None
        self.status = None
        self.exposure_status = ExposureStatus.IDLE

        # data display
        self.widgetDataDisplay = self.create_widget(WidgetDataDisplay, module=self.module)
        self.framePlot.layout().addWidget(self.widgetDataDisplay)

        # before first update, disable myself
        self.setEnabled(False)

        # hide single controls
        self.butAbort.setVisible(isinstance(self.module, IAbortable))

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def open(self):
        """Open widget."""
        await BaseWidget.open(self)

        # subscribe to events
        await self.comm.register_event(ExposureStatusChangedEvent, self._on_exposure_status_changed)

    async def _init(self) -> None:
        # get status
        if isinstance(self.module, ISpectrograph):
            self.exposure_status = ExposureStatus(await self.module.get_exposure_status())

        # update GUI
        self.signal_update_gui.emit()

    @pyqtSlot(name='on_butExpose_clicked')
    def grab_spectrum(self):
        if not isinstance(self.module, ISpectrograph):
            return

        # expose
        broadcast = self.checkBroadcast.isChecked()
        asyncio.create_task(self.widgetDataDisplay.grab_data(broadcast))

        # signal GUI update
        self.signal_update_gui.emit()

    @pyqtSlot(name='on_butAbort_clicked')
    def abort(self):
        """Abort exposure."""
        if isinstance(self, ISpectrograph):
            asyncio.create_task(self.module.abort())

    async def _update(self) -> None:
        # are we exposing?
        if self.exposure_status == ExposureStatus.EXPOSING:
            # get camera status
            #self.exposure_time_left = await self.module.get_exposure_time_left()
            self.exposure_progress = await self.module.get_exposure_progress()

        else:
            # reset
            #self.exposure_time_left = 0
            self.exposure_progress = 0

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self):
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # enable/disable buttons
        self.butExpose.setEnabled(self.exposure_status == ExposureStatus.IDLE)
        self.butAbort.setEnabled(self.exposure_status != ExposureStatus.IDLE)

        # set progress
        msg = ''
        if self.exposure_status == ExposureStatus.IDLE:
            self.progressExposure.setValue(0)
            msg = 'IDLE'
        elif self.exposure_status == ExposureStatus.EXPOSING:
            #self.progressExposure.setValue(int(self.exposure_progress))
            #msg = 'EXPOSING %.1fs' % self.exposure_time_left
            msg = ''
        elif self.exposure_status == ExposureStatus.READOUT:
            self.progressExposure.setValue(100)
            msg = 'READOUT'

        # set message
        self.labelStatus.setText(msg)

        # trigger image update
        if self.new_spectrum:
            # set filename
            #self.tabWidget.setTabText(0, os.path.basename(self.spectrum_filename))

            # plot image
            self.plot()

            # reset
            self.new_spectrum = False

    async def _on_exposure_status_changed(self, event: Event, sender: str) -> bool:
        """Called when exposure status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name or not isinstance(event, ExposureStatusChangedEvent):
            return False

        # store new status
        self.exposure_status = event.current

        # trigger GUI update
        self.signal_update_gui.emit()
        return True
