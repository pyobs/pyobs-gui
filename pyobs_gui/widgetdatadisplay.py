import logging
import os
import threading
from enum import Enum
from typing import Any, Optional, List

import numpy as np
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from astropy.io import fits
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from pyobs.events import NewImageEvent, NewSpectrumEvent, Event
from pyobs.interfaces import IImageGrabber, ISpectrograph
from pyobs.interfaces.proxies import IImageGrabberProxy, ISpectrographProxy
from pyobs.utils.enums import ImageType, ExposureStatus
from pyobs.images import Image
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.basewidget import BaseWidget
from qfitswidget import QFitsWidget
from .qt.widgetdatadisplay import Ui_WidgetDataDisplay

log = logging.getLogger(__name__)


class DownloadThread(QtCore.QThread):
    """Worker thread for downloading data."""

    """Signal emitted when the data is downloaded."""
    dataReady = pyqtSignal(fits.HDUList, str)

    def __init__(self, vfs: VirtualFileSystem, filename: str, autosave: Optional[str] = None,
                 *args: Any, **kwargs: Any):
        """Init a new worker thread.

        Args:
            vfs: VFS to use for download
            filename: File to download
            autosave: Path for autosave or None.
        """
        QtCore.QThread.__init__(self, *args, **kwargs)
        self.vfs = vfs
        self.filename = filename
        self.autosave = autosave

    def run(self) -> None:
        """Run method in thread."""

        # download data
        data = self.vfs.read_fits(self.filename)

        # auto save?
        if self.autosave is not None:
            # get path and check
            path = self.autosave
            if not os.path.exists(path):
                log.warning('Invalid path for auto-saving.')

            else:
                # save image
                filename = os.path.join(path, os.path.basename(self.filename.replace('.fits.gz', '.fits')))
                log.info('Saving image as %s...', filename)
                data.writeto(filename, overwrite=True)

        # update GUI
        self.dataReady.emit(data, self.filename)


class WidgetDataDisplay(BaseWidget, Ui_WidgetDataDisplay):
    signal_update_gui = pyqtSignal()
    signal_new_data = pyqtSignal(Event, str)

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # variables
        self.new_data = False
        self.data_filename: Optional[str] = None
        self.data: Optional[fits.HDUList] = None
        self.download_threads: List[DownloadThread] = []
        self.lock = threading.RLock()

        # before first update, disable mys
        self.setEnabled(False)

        # add image panel
        self.imageLayout = QtWidgets.QVBoxLayout(self.tabImage)
        if isinstance(self.module, IImageGrabberProxy):
            self.imageView = QFitsWidget()
            self.imageLayout.addWidget(self.imageView)
        elif isinstance(self.module, ISpectrographProxy):
            self.figure, self.ax = plt.subplots()
            self.canvas = FigureCanvas(self.figure)
            self.plotTools = NavigationToolbar2QT(self.canvas, self.tabImage)
            self.imageLayout.addWidget(self.plotTools)
            self.imageLayout.addWidget(self.canvas)
        else:
            raise ValueError('Unknown type')

        # set headers for fits header tab
        self.tableFitsHeader.setColumnCount(3)
        self.tableFitsHeader.setHorizontalHeaderLabels(['Key', 'Value', 'Comment'])

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.signal_new_data.connect(self._on_new_data)
        self.checkAutoSave.stateChanged.connect(lambda x: self.textAutoSavePath.setEnabled(x))

        # subscribe to events
        self.comm.register_event(NewImageEvent, self._on_new_data)
        self.comm.register_event(NewSpectrumEvent, self._on_new_data)

    def grab_data(self, broadcast: bool, image_type: ImageType = ImageType.OBJECT) -> None:
        """Grab data. Must be called from a thread."""

        # expose
        if isinstance(self.module, IImageGrabberProxy):
            filename = self.module.grab_image(broadcast=broadcast).wait()
        elif isinstance(self.module, ISpectrographProxy):
            filename = self.module.grab_spectrum(broadcast=broadcast).wait()
        else:
            raise ValueError('Unknown type')

        # if we're not broadcasting the filename, we need to signal it manually
        if not broadcast:
            if isinstance(self.module, IImageGrabberProxy):
                self.signal_new_data.emit(NewImageEvent(filename, image_type), self.module.name)
            elif isinstance(self.module, ISpectrographProxy):
                self.signal_new_data.emit(NewSpectrumEvent(filename), self.module.name)
            else:
                raise ValueError('Unknown type')

        # signal GUI update
        self.signal_update_gui.emit()

    def plot(self) -> None:
        """Show data."""
        if isinstance(self.module, IImageGrabberProxy):
            self.imageView.display(self.data[0])
        elif isinstance(self.module, ISpectrographProxy):
            self._plot_spectrum()

    def _plot_spectrum(self) -> None:
        """Plot spectrum."""
        hdr = self.data[0].header
        data = self.data[0].data

        # build wavelength array
        wave = np.arange(hdr['CRVAL1'], hdr['CRVAL1'] + hdr['CDELT1'] * hdr['NAXIS1'], hdr['CDELT1'])

        # plot it
        self.figure.delaxes(self.ax)
        self.ax = self.figure.add_subplot(111)
        self.ax.plot(wave, data)
        self.canvas.draw()

    def update_gui(self) -> None:
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # trigger image update
        if self.new_data:
            # set filename
            self.tabWidget.setTabText(0, os.path.basename(self.data_filename))

            # plot image
            self.plot()

            # set fits headers
            self.show_fits_headers()

            # reset
            self.new_data = False

    def show_fits_headers(self) -> None:
        # get all header cards
        headers = {}
        for card in self.data[0].header.cards:
            headers[card.keyword] = (card.value, card.comment)

        # prepare table
        self.tableFitsHeader.setRowCount(len(headers))

        # set headers
        for i, key in enumerate(sorted(headers.keys())):
            self.tableFitsHeader.setItem(i, 0, QtWidgets.QTableWidgetItem(key))
            self.tableFitsHeader.setItem(i, 1, QtWidgets.QTableWidgetItem(str(headers[key][0])))
            self.tableFitsHeader.setItem(i, 2, QtWidgets.QTableWidgetItem(headers[key][1]))

        # adjust column widths
        self.tableFitsHeader.resizeColumnToContents(0)
        self.tableFitsHeader.resizeColumnToContents(1)

    def _on_new_data(self, event: Event, sender: str) -> bool:
        """Called when new image is ready.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name:
            return False

        # don't update?
        if not self.checkAutoUpdate.isChecked():
            return False

        # autosave?
        autosave = self.textAutoSavePath.text() if self.checkAutoSave.isChecked() else None

        # create thread for download
        thread = DownloadThread(self.vfs, event.filename, autosave)
        thread.dataReady.connect(self._data_downloaded)
        thread.start()

        # add thread and finish
        self.download_threads.append(thread)
        return True

    def _data_downloaded(self, data: fits.HDUList, filename: str) -> None:
        """Called, when data is downloaded.
        """

        # store image and filename
        self.data = data
        self.data_filename = filename
        self.new_data = True

        # find finished threads and delete them
        finished_threads = [t for t in self.download_threads if not t.isRunning()]
        for t in finished_threads:
            self.download_threads.remove(t)

        # show image
        self.update_gui()

    @pyqtSlot(name='on_butAutoSave_clicked')
    def select_autosave_path(self) -> None:
        """Select path for auto-saving."""

        # ask for path
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")

        # set it
        if path:
            self.textAutoSavePath.setText(path)
        else:
            self.textAutoSavePath.clear()

    @pyqtSlot(name='on_butSaveTo_clicked')
    def save_data(self) -> None:
        """Save image."""

        # no image?
        if self.data is None:
            return

        # get initial filename
        init_filename = os.path.basename(self.data_filename).replace('.fits.gz', '.fits')

        # ask for filename
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save image", init_filename,
                                                            "FITS Files (*.fits *.fits.gz)")

        # save
        if filename:
            self.data.writeto(filename, overwrite=True)
