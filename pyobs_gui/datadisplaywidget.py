import logging
import os
from typing import Any, Optional, cast, Union, Dict, List
import numpy as np
from PyQt5 import QtWidgets, QtCore
from astroplan import Observer
from astropy.io import fits
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from pyobs.comm import Proxy, Comm
from pyobs.modules import Module
from qfitswidget import QFitsWidget

from pyobs.events import NewImageEvent, NewSpectrumEvent, Event
from pyobs.interfaces import IData, ISpectrograph
from pyobs.utils.enums import ImageType
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .qt.datadisplaywidget_ui import Ui_DataDisplayWidget

log = logging.getLogger(__name__)


class DataDisplayWidget(QtWidgets.QWidget, BaseWidget, Ui_DataDisplayWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, parent, **kwargs: Any):
        QtWidgets.QWidget.__init__(self, parent)
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # variables
        self.new_data = False
        self.data_filename: Optional[str] = None
        self.data: Optional[fits.HDUList] = None
        self.imageLayout: Optional[QtWidgets.QVBoxLayout] = None
        self.imageView: Optional[QFitsWidget] = None
        self.figure = None
        self.ax = None
        self.canvas = None
        self.plotTools = None

        # before first update, disable mys
        self.setEnabled(False)

        # set headers for fits header tab
        self.tableFitsHeader.setColumnCount(3)
        self.tableFitsHeader.setHorizontalHeaderLabels(["Key", "Value", "Comment"])

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.checkAutoSave.stateChanged.connect(lambda x: self.textAutoSavePath.setEnabled(x))

    async def open(
        self,
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

        # add image panel
        self.imageLayout = QtWidgets.QVBoxLayout(self.tabImage)
        if isinstance(self.module, ISpectrograph):
            self.figure, self.ax = plt.subplots()
            self.canvas = FigureCanvas(self.figure)
            self.plotTools = NavigationToolbar2QT(self.canvas, self.tabImage)
            self.imageLayout.addWidget(self.plotTools)
            self.imageLayout.addWidget(self.canvas)
        elif isinstance(self.module, IData):
            self.imageView = QFitsWidget()
            self.imageLayout.addWidget(self.imageView)
        else:
            raise ValueError("Unknown type")

        # subscribe to events
        if self.comm is not None:
            await self.comm.register_event(NewImageEvent, self._on_new_data)
            await self.comm.register_event(NewSpectrumEvent, self._on_new_data)

    async def grab_data(self, broadcast: bool, image_type: ImageType = ImageType.OBJECT) -> None:
        """Grab data."""
        if self.module is None:
            return

        # expose
        if isinstance(self.module, IData):
            filename = await self.module.grab_data(broadcast=broadcast)
        else:
            raise ValueError("Unknown type")

        # if we're not broadcasting the filename, we need to signal it manually
        if not broadcast:
            if isinstance(self.module, ISpectrograph):
                await self._on_new_data(NewSpectrumEvent(filename), cast(Proxy, self.module).name)
            elif isinstance(self.module, IData):
                await self._on_new_data(NewImageEvent(filename, image_type), cast(Proxy, self.module).name)
            else:
                raise ValueError("Unknown type")

        # signal GUI update
        self.signal_update_gui.emit()

    def plot(self) -> None:
        """Show data."""
        if self.data is None:
            return

        if isinstance(self.module, ISpectrograph):
            self._plot_spectrum()
        elif isinstance(self.module, IData):
            self.imageView.display(self.data[0])

    def _plot_spectrum(self) -> None:
        """Plot spectrum."""
        if self.data is None:
            return

        # get shortcuts
        hdr = self.data[0].header
        data = self.data[0].data

        # build wavelength array
        wave = np.arange(hdr["CRVAL1"], hdr["CRVAL1"] + hdr["CDELT1"] * hdr["NAXIS1"], hdr["CDELT1"])

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
        if self.new_data and self.data_filename is not None:
            # set filename
            self.tabWidget.setTabText(0, os.path.basename(self.data_filename))

            # plot image
            self.plot()

            # set fits headers
            self.show_fits_headers()

            # reset
            self.new_data = False

    def show_fits_headers(self) -> None:
        if self.data is None:
            return

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
                log.warning("Invalid path for auto-saving.")

            else:
                # save image
                filename = os.path.join(
                    autosave,
                    os.path.basename(event.filename.replace(".fits.gz", ".fits")),
                )
                log.info("Saving image as %s...", filename)
                data.writeto(filename, overwrite=True)

        # store image and filename
        self.data = data
        self.data_filename = event.filename
        self.new_data = True

        # show image
        self.update_gui()

        # finish
        return True

    @QtCore.pyqtSlot(name="on_butAutoSave_clicked")
    def select_autosave_path(self) -> None:
        """Select path for auto-saving."""

        # ask for path
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")

        # set it
        if path:
            self.textAutoSavePath.setText(path)
        else:
            self.textAutoSavePath.clear()

    @QtCore.pyqtSlot(name="on_butSaveTo_clicked")
    def save_data(self) -> None:
        """Save image."""

        # no image?
        if self.data is None or self.data_filename is None:
            return

        # get initial filename
        init_filename = os.path.basename(self.data_filename).replace(".fits.gz", ".fits")

        # ask for filename
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(
            self, "Save image", init_filename, "FITS Files (*.fits *.fits.gz)"
        )

        # save
        if filename:
            self.data.writeto(filename, overwrite=True)
