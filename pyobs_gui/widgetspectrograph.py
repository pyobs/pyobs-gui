import logging
import threading
from typing import Any, List, Optional
import numpy as np
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from astropy.io import fits
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

from pyobs.events import ExposureStatusChangedEvent, Event
from pyobs.interfaces.proxies import IAbortableProxy, ISpectrographProxy
from pyobs.utils.enums import ExposureStatus
from pyobs.images import Image
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.basewidget import BaseWidget

from .qt.widgetspectrograph import Ui_WidgetSpectrograph


log = logging.getLogger(__name__)


class DownloadThread(QtCore.QThread):  # type: ignore
    """Worker thread for downloading images."""

    """Signal emitted when the spectrum is downloaded."""
    spectrumReady = pyqtSignal(Image, str)

    def __init__(self, vfs: VirtualFileSystem, filename: str, *args: Any, **kwargs: Any):
        """Init a new worker thread.

        Args:
            vfs: VFS to use for download
            filename: File to download
        """
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.vfs = vfs
        self.filename = filename

    def run(self) -> None:
        """Run method in thread."""

        # download spectrum
        spectrum = self.vfs.read_fits(self.filename)

        # update GUI
        self.spectrumReady.emit(spectrum, self.filename)


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
        self.download_threads: List[DownloadThread] = []

        # figure
        self.figure, self.ax = plt.subplots()

        # image grabber
        layout = self.framePlot.layout()
        self.canvas = FigureCanvas(self.figure)
        self.plotTools = NavigationToolbar2QT(self.canvas, self.framePlot)
        layout.addWidget(self.plotTools)
        layout.addWidget(self.canvas)

        # before first update, disable myself
        self.setEnabled(False)

        # hide single controls
        self.butAbort.setVisible(isinstance(self.module, IAbortableProxy))

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

        # subscribe to events
        self.comm.register_event(ExposureStatusChangedEvent, self._on_exposure_status_changed)

    def _init(self) -> None:
        # get status
        if isinstance(self.module, ISpectrographProxy):
            self.exposure_status = ExposureStatus(self.module.get_exposure_status().wait())

        # update GUI
        self.signal_update_gui.emit()

    @pyqtSlot(name='on_butExpose_clicked')
    def expose(self) -> None:
        # start exposures
        threading.Thread(target=self._expose_thread_func).start()

    def _expose_thread_func(self) -> None:
        if not isinstance(self.module, ISpectrographProxy):
            return

        # expose
        broadcast = self.checkBroadcast.isChecked()
        self.spectrum_filename = self.module.grab_spectrum(broadcast).wait()

        # download it
        self.new_spectrum = True
        self.spectrum = self.vfs.read_fits(self.spectrum_filename)

        # signal GUI update
        self.signal_update_gui.emit()

    def plot(self) -> None:
        """Show image."""

        # get header and data
        hdr = self.spectrum[0].header
        data = self.spectrum[0].data

        # build wavelength array
        wave = np.arange(hdr['CRVAL1'], hdr['CRVAL1'] + hdr['CDELT1'] * hdr['NAXIS1'], hdr['CDELT1'])

        # plot it
        self.figure.delaxes(self.ax)
        self.ax = self.figure.add_subplot(111)
        self.ax.plot(wave, data)
        self.canvas.draw()

    @pyqtSlot(name='on_butAbort_clicked')
    def abort(self) -> None:
        """Abort exposure."""
        if isinstance(self, ISpectrographProxy):
            self.module.abort().wait()

    def _update(self) -> None:
        # are we exposing?
        if self.exposure_status == ExposureStatus.EXPOSING:
            # get camera status
            exposure_time_left = self.module.get_exposure_time_left()
            exposure_progress = self.module.get_exposure_progress()

            # fetch results
            self.exposure_time_left = exposure_time_left.wait()
            self.exposure_progress = exposure_progress.wait()

        else:
            # reset
            self.exposure_time_left = 0
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

    def _on_exposure_status_changed(self, event: Event, sender: str) -> bool:
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
