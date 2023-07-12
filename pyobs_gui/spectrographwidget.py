import asyncio
import logging
from typing import Optional, Any, Union, Dict, List
from PyQt5 import QtCore, QtWidgets
from astroplan import Observer
from astropy.io import fits

from pyobs.comm import Proxy, Comm
from pyobs.events import ExposureStatusChangedEvent, Event
from pyobs.interfaces import IAbortable, ISpectrograph, IExposureTime
from pyobs.utils.enums import ExposureStatus
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .datadisplaywidget import DataDisplayWidget

from .qt.spectrographwidget_ui import Ui_SpectrographWidget


log = logging.getLogger(__name__)


class SpectrographWidget(QtWidgets.QWidget, BaseWidget, Ui_SpectrographWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, **kwargs: Any) -> None:
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)

        # variables
        self.new_spectrum = False
        self.spectrum_filename: Optional[str] = None
        self.spectrum: Optional[fits.PrimaryHDU] = None
        self.status = None
        self.exposure_status = ExposureStatus.IDLE

        # data display
        # self.widgetDataDisplay = self.create_widget(DataDisplayWidget, module=self.module)
        # self.framePlot.layout().addWidget(self.widgetDataDisplay)

        # before first update, disable myself
        self.setEnabled(False)

        # hide single controls
        self.butAbort.setVisible(isinstance(self.module, IAbortable))

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def open(
        self,
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)
        await self.datadisplay.open(modules=modules, comm=comm, observer=observer, vfs=vfs)

        # subscribe to events
        await self.comm.register_event(ExposureStatusChangedEvent, self._on_exposure_status_changed)

    async def _init(self) -> None:
        # get status
        if isinstance(self.module, ISpectrograph):
            self.exposure_status = ExposureStatus(await self.module.get_exposure_status())

        # update GUI
        self.signal_update_gui.emit()

    @QtCore.pyqtSlot(name="on_butExpose_clicked")
    def grab_spectrum(self) -> None:
        if not isinstance(self.module, ISpectrograph):
            return

        # expose
        broadcast = self.checkBroadcast.isChecked()
        asyncio.create_task(self.datadisplay.grab_data(broadcast))

        # signal GUI update
        self.signal_update_gui.emit()

    @QtCore.pyqtSlot(name="on_butAbort_clicked")
    def abort(self) -> None:
        """Abort exposure."""
        if isinstance(self, ISpectrograph):
            asyncio.create_task(self.module.abort())

    async def _update(self) -> None:
        # are we exposing?
        if self.exposure_status == ExposureStatus.EXPOSING:
            # get camera status
            if isinstance(self.module, IExposureTime):
                self.exposure_time_left = await self.module.get_exposure_time_left()
            if isinstance(self.module, ISpectrograph):
                self.exposure_progress = await self.module.get_exposure_progress()

        else:
            # reset
            self.exposure_time_left = 0
            self.exposure_progress = 0

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # enable/disable buttons
        self.butExpose.setEnabled(self.exposure_status == ExposureStatus.IDLE)
        self.butAbort.setEnabled(self.exposure_status != ExposureStatus.IDLE)

        # set progress
        msg = ""
        if self.exposure_status == ExposureStatus.IDLE:
            self.progressExposure.setValue(0)
            msg = "IDLE"
        elif self.exposure_status == ExposureStatus.EXPOSING:
            # self.progressExposure.setValue(int(self.exposure_progress))
            # msg = 'EXPOSING %.1fs' % self.exposure_time_left
            msg = ""
        elif self.exposure_status == ExposureStatus.READOUT:
            self.progressExposure.setValue(100)
            msg = "READOUT"

        # set message
        self.labelStatus.setText(msg)

        # trigger image update
        if self.new_spectrum:
            # set filename
            # self.tabWidget.setTabText(0, os.path.basename(self.spectrum_filename))

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
