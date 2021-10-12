import logging
import os
import threading
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot

from pyobs.comm import Comm
from pyobs.events import  NewImageEvent
from pyobs.interfaces import IImageGrabber
from pyobs.utils.enums import ImageType, ExposureStatus
from pyobs.images import Image
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.basewidget import BaseWidget
from qfitswidget import QFitsWidget
from .qt.widgetimagegrabber import Ui_WidgetImageGrabber

log = logging.getLogger(__name__)


class DownloadThread(QtCore.QThread):
    """Worker thread for downloading images."""

    """Signal emitted when the image is downloaded."""
    imageReady = pyqtSignal(Image, str)

    def __init__(self, vfs: VirtualFileSystem, filename: str, autosave: str = None, *args, **kwargs):
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

    def run(self):
        """Run method in thread."""

        # download image
        image = self.vfs.read_image(self.filename)

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
                image.writeto(filename, overwrite=True)

        # update GUI
        self.imageReady.emit(image, self.filename)


class WidgetImageGrabber(BaseWidget, Ui_WidgetImageGrabber):
    signal_update_gui = pyqtSignal()
    signal_new_image = pyqtSignal(NewImageEvent, str)

    def __init__(self, **kwargs):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # variables
        self.new_image = False
        self.image_filename = None
        self.image = None
        self.status = None
        self.exposure_status = ExposureStatus.IDLE
        self.exposures_left = 0
        self.exposure_time_left = 0
        self.exposure_progress = 0
        self.download_threads = []
        self.lock = threading.RLock()

        # before first update, disable mys
        self.setEnabled(False)

        # add image panel
        self.imageLayout = QtWidgets.QVBoxLayout(self.tabImage)
        self.imageView = QFitsWidget()
        self.imageLayout.addWidget(self.imageView)

        # set headers for fits header tab
        self.tableFitsHeader.setColumnCount(3)
        self.tableFitsHeader.setHorizontalHeaderLabels(['Key', 'Value', 'Comment'])

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.signal_new_image.connect(self._on_new_image)
        self.checkAutoSave.stateChanged.connect(lambda x: self.textAutoSavePath.setEnabled(x))

        # subscribe to events
        self.comm.register_event(NewImageEvent, self._on_new_image)

    def grab_image(self, broadcast: bool, image_type: ImageType):
        """Grab image. Must be called from a thread."""

        # expose
        filename = self.module.grab_image(broadcast=broadcast).wait()

        # decrement number of exposures left
        self.exposures_left -= 1

        # if we're not broadcasting the filename, we need to signal it manually
        if not broadcast:
            ev = NewImageEvent(filename, image_type)
            self.signal_new_image.emit(ev, self.module.name)

        # signal GUI update
        self.signal_update_gui.emit()

    def plot(self):
        """Show image."""
        self.imageView.display(self.image)

    def update_gui(self):
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # trigger image update
        if self.new_image:
            # set filename
            self.tabWidget.setTabText(0, os.path.basename(self.image_filename))

            # plot image
            self.plot()

            # set fits headers
            self.show_fits_headers()

            # reset
            self.new_image = False

    def show_fits_headers(self):
        # get all header cards
        headers = {}
        for card in self.image.header.cards:
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

    def _on_new_image(self, event: NewImageEvent, sender: str):
        """Called when new image is ready.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name:
            return

        # don't update?
        if not self.checkAutoUpdate.isChecked():
            return

        # autosave?
        autosave = self.textAutoSavePath.text() if self.checkAutoSave.isChecked() else None

        # create thread for download
        thread = DownloadThread(self.vfs, event.filename, autosave)
        thread.imageReady.connect(self._image_downloaded)
        thread.start()

        self.download_threads.append(thread)

    def _image_downloaded(self, image, filename):
        """Called, when image is downloaded.
        """

        # store image and filename
        self.image = image
        self.image_filename = filename
        self.new_image = True

        # find finished threads and delete them
        finished_threads = [t for t in self.download_threads if not t.isRunning()]
        for t in finished_threads:
            self.download_threads.remove(t)

        # show image
        self.update_gui()

    @pyqtSlot(name='on_butAutoSave_clicked')
    def select_autosave_path(self):
        """Select path for auto-saving."""

        # ask for path
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")

        # set it
        if path:
            self.textAutoSavePath.setText(path)
        else:
            self.textAutoSavePath.clear()

    @pyqtSlot(name='on_butSaveTo_clicked')
    def save_image(self):
        """Save image."""

        # no image?
        if self.image is None:
            return

        # get initial filename
        init_filename = os.path.basename(self.image_filename).replace('.fits.gz', '.fits')

        # ask for filename
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save image", init_filename,
                                                            "FITS Files (*.fits *.fits.gz)")

        # save
        if filename:
            self.image.writeto(filename, overwrite=True)
