import asyncio
import logging
import os
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
from pyobs.utils.enums import ImageType
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.basewidget import BaseWidget
from qfitswidget import QFitsWidget
from .qt.widgetdatadisplay import Ui_WidgetDataDisplay

log = logging.getLogger(__name__)


class WidgetDataDisplay(BaseWidget, Ui_WidgetDataDisplay):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # variables
        self.new_data = False
        self.data_filename: Optional[str] = None
        self.data: Optional[fits.HDUList] = None

        # before first update, disable mys
        self.setEnabled(False)

        # add image panel
        self.imageLayout = QtWidgets.QVBoxLayout(self.tabImage)
        if isinstance(self.module, IImageGrabber):
            self.imageView = QFitsWidget()
            self.imageLayout.addWidget(self.imageView)
        elif isinstance(self.module, ISpectrograph):
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
        self.checkAutoSave.stateChanged.connect(lambda x: self.textAutoSavePath.setEnabled(x))

    async def open(self):
        """Open widget."""
        await BaseWidget.open(self)

        # subscribe to events
        await self.comm.register_event(NewImageEvent, self._on_new_data)
        await self.comm.register_event(NewSpectrumEvent, self._on_new_data)

    async def grab_data(self, broadcast: bool, image_type: ImageType = ImageType.OBJECT) -> None:
        """Grab data. Must be called from a thread."""

        # expose
        if isinstance(self.module, IImageGrabber):
            filename = await self.module.grab_image(broadcast=broadcast)
        elif isinstance(self.module, ISpectrograph):
            filename = await self.module.grab_spectrum(broadcast=broadcast)
        else:
            raise ValueError('Unknown type')

        # if we're not broadcasting the filename, we need to signal it manually
        if not broadcast:
            if isinstance(self.module, IImageGrabber):
                await self._on_new_data(NewImageEvent(filename, image_type), self.module.name)
            elif isinstance(self.module, ISpectrograph):
                await self._on_new_data(NewSpectrumEvent(filename), self.module.name)
            else:
                raise ValueError('Unknown type')

        # signal GUI update
        self.signal_update_gui.emit()

    def plot(self) -> None:
        """Show data."""
        if isinstance(self.module, IImageGrabber):
            self.imageView.display(self.data[0])
        elif isinstance(self.module, ISpectrograph):
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

    async def _on_new_data(self, event: Event, sender: str) -> bool:
        """Called when new image is ready.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name:
            return False

        # wrong type
        if not isinstance(event, NewImageEvent) and not isinstance(event, NewSpectrumEvent):
            return False

        # don't update?
        if not self.checkAutoUpdate.isChecked():
            return False

        # autosave?
        autosave = self.textAutoSavePath.text() if self.checkAutoSave.isChecked() else None

        # download data
        data = await self.vfs.read_fits(event.filename)

        # auto save?
        if autosave is not None:
            # get path and check
            if not os.path.exists(autosave):
                log.warning('Invalid path for auto-saving.')

            else:
                # save image
                filename = os.path.join(autosave, os.path.basename(event.filename.replace('.fits.gz', '.fits')))
                log.info('Saving image as %s...', filename)
                data.writeto(filename, overwrite=True)

        # store image and filename
        self.data = data
        self.data_filename = event.filename
        self.new_data = True

        # show image
        self.update_gui()

        # finish
        return True

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
