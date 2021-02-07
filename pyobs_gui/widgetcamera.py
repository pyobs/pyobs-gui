import logging
import os
import threading
from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox

from pyobs.events import ExposureStatusChangedEvent, NewImageEvent
from pyobs.interfaces import ICamera, ICameraBinning, ICameraWindow, ICooling, IFilters, ITemperatures, \
    ICameraExposureTime, IImageType, IImageFormat
from pyobs.utils.enums import ImageType, ImageFormat
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.basewidget import BaseWidget
from pyobs_gui.widgetcooling import WidgetCooling
from pyobs_gui.widgetfilter import WidgetFilter
from pyobs_gui.widgettemperatures import WidgetTemperatures
from pyobs_gui.widgetfitsheaders import WidgetFitsHeaders
from qfitswidget import QFitsWidget
from .qt.widgetcamera import Ui_WidgetCamera


log = logging.getLogger(__name__)


class WidgetCamera(BaseWidget, Ui_WidgetCamera):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, vfs, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update)
        self.setupUi(self)
        self.module = module    # type: ICamera
        self.comm = comm        # type: Comm
        self.vfs = vfs          # type: VirtualFileSystem

        # variables
        self.new_image = False
        self.image_filename = None
        self.image = None
        self.status = None
        self.exposure_status = ICamera.ExposureStatus.IDLE
        self.exposures_left = 0
        self.exposure_time_left = 0
        self.exposure_progress = 0

        # set exposure types
        image_types = ['OBJECT', 'BIAS', 'DARK']
        self.comboImageType.addItems(image_types)

        # before first update, disable mys
        self.setEnabled(False)

        # hide groups, if necessary
        self.groupWindowing.setVisible(isinstance(self.module, ICameraWindow))
        self.groupBinning.setVisible(isinstance(self.module, ICameraBinning))
        self.groupImageFormat.setVisible(isinstance(self.module, IImageFormat))

        # add image panel
        self.imageLayout = QtWidgets.QVBoxLayout(self.tabImage)
        self.imageView = QFitsWidget()
        self.imageLayout.addWidget(self.imageView)

        # set headers for fits header tab
        self.tableFitsHeader.setColumnCount(3)
        self.tableFitsHeader.setHorizontalHeaderLabels(['Key', 'Value', 'Comment'])

        # connect signals
        self.butFullFrame.clicked.connect(self.set_full_frame)
        self.comboBinning.currentTextChanged.connect(self.binning_changed)
        self.comboImageType.currentTextChanged.connect(self.image_type_changed)
        self.butExpose.clicked.connect(self.expose)
        self.butAbort.clicked.connect(self.abort)
        self.signal_update_gui.connect(self.update_gui)
        self.butAutoSave.clicked.connect(self.select_autosave_path)
        self.butSaveTo.clicked.connect(self.save_image)
        self.checkAutoSave.stateChanged.connect(lambda x: self.textAutoSavePath.setEnabled(x))

        # initial values
        self.comboImageType.setCurrentIndex(image_types.index('OBJECT'))

        # subscribe to events
        self.comm.register_event(ExposureStatusChangedEvent, self._on_exposure_status_changed)
        self.comm.register_event(NewImageEvent, self._on_new_image)

        # fill sidebar
        self.add_to_sidebar(WidgetFitsHeaders(module, comm))
        if isinstance(self.module, IFilters):
            self.add_to_sidebar(WidgetFilter(module, comm))
        if isinstance(self.module, ICooling):
            self.add_to_sidebar(WidgetCooling(module, comm))
        if isinstance(self.module, ITemperatures):
            self.add_to_sidebar(WidgetTemperatures(module, comm))

    def _init(self):
        # get status
        self.exposure_status = ICamera.ExposureStatus(self.module.get_exposure_status().wait())

        # get binnings
        if isinstance(self.module, ICameraBinning):
            # get binnings
            binnings = ['%dx%d' % (b, b) for b in self.module.list_binnings().wait()]

            # set it
            self.comboBinning.clear()
            self.comboBinning.addItems(binnings)

            # set default value
            self.comboBinning.setCurrentIndex(0)

        # get image formats
        if isinstance(self.module, IImageFormat):
            # get formats
            image_formats = [ImageFormat(f) for f in self.module.list_image_formats().wait()]

            # set it
            self.comboImageFormat.clear()
            self.comboImageFormat.addItems([f.name for f in image_formats])

            # find default value
            if ImageFormat.INT16 in image_formats:
                self.comboImageFormat.setCurrentText('INT16')
            elif ImageFormat.INT8 in image_formats:
                self.comboImageFormat.setCurrentText('INT8')
            else:
                self.comboImageFormat.setCurrentIndex(0)

        # set full frame
        self.set_full_frame()

        # update GUI
        self.signal_update_gui.emit()

    def set_full_frame(self):
        if isinstance(self.module, ICameraWindow):
            # get full frame
            left, top, width, height = self.module.get_full_frame().wait()

            # get binning
            binning = int(self.comboBinning.currentText()[0]) if isinstance(self.module, ICameraBinning) else 1

            # set it
            self.spinWindowLeft.setValue(left)
            self.spinWindowTop.setValue(top)
            self.spinWindowWidth.setValue(width / binning)
            self.spinWindowHeight.setValue(height / binning)

            # max values
            self.spinWindowLeft.setMaximum(width / binning)
            self.spinWindowTop.setMaximum(height / binning)
            self.spinWindowWidth.setMaximum(width / binning)
            self.spinWindowHeight.setMaximum(height / binning)

    def binning_changed(self, binning):
        self.set_full_frame()

    def image_type_changed(self, image_type):
        if image_type == 'BIAS':
            self.spinExpTime.setValue(0)
            self.spinExpTime.setEnabled(False)
        else:
            self.spinExpTime.setEnabled(True)

    def expose(self):
        # set binning
        if isinstance(self.module, ICameraBinning):
            binning = int(self.comboBinning.currentText()[0])
            print(binning)
            try:
                self.module.set_binning(binning, binning).wait()
            except:
                log.exception('bla')
                QMessageBox.information(self, 'Error', 'Could not set binning.')
                return
        else:
            binning = 1

        # set window
        if isinstance(self.module, ICameraWindow):
            left, top = self.spinWindowLeft.value(), self.spinWindowTop.value()
            width, height = self.spinWindowWidth.value(), self.spinWindowHeight.value()
            try:
                self.module.set_window(left, top, width * binning, height * binning).wait()
            except:
                QMessageBox.information(self, 'Error', 'Could not set window.')
                return

        # set image format
        if isinstance(self.module, IImageFormat):
            image_format = ImageFormat[self.comboImageFormat.currentText()]
            self.module.set_image_format(image_format)

        # set initial image count
        self.exposures_left = self.spinCount.value()

        # start exposures
        threading.Thread(target=self._expose_thread_func).start()

    def _expose_thread_func(self):
        # get image type
        image_type = ImageType(self.comboImageType.currentText().lower())

        # do exposure(s)
        while self.exposures_left > 0:
            # set exposure time and expose
            if isinstance(self.module, ICameraExposureTime):
                self.module.set_exposure_time(self.spinExpTime.value()).wait()
            if isinstance(self.module, IImageType):
                self.module.set_image_type(image_type)
            self.module.expose().wait()

            # decrement number of exposures left
            self.exposures_left -= 1

            # signal GUI update
            self.signal_update_gui.emit()

    def plot(self):
        """Show image."""
        self.imageView.display(self.image)
        
    def abort(self):
        """Abort exposure."""

        # do we have a running exposure?
        if self.exposures_left == 0:
            return

        # got exposures left?
        if self.exposures_left > 1:
            # abort sequence
            self.exposures_left = 0
        else:
            self.module.abort().wait()

    def _update(self):
        # are we exposing?
        if self.exposure_status == ICamera.ExposureStatus.EXPOSING:
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
        self.butExpose.setEnabled(self.exposure_status == ICamera.ExposureStatus.IDLE)
        self.butAbort.setEnabled(self.exposure_status != ICamera.ExposureStatus.IDLE)

        # set abort text
        if self.exposures_left > 1:
            self.butAbort.setText('Abort sequence')
        else:
            self.butAbort.setText('Abort exposure')

        # set progress
        msg = ''
        if self.exposure_status == ICamera.ExposureStatus.IDLE:
            self.progressExposure.setValue(0)
            msg = 'IDLE'
        elif self.exposure_status == ICamera.ExposureStatus.EXPOSING:
            self.progressExposure.setValue(self.exposure_progress)
            msg = 'EXPOSING %.1fs' % self.exposure_time_left
        elif self.exposure_status == ICamera.ExposureStatus.READOUT:
            self.progressExposure.setValue(100)
            msg = 'READOUT'

        # set message
        self.labelStatus.setText(msg)

        # exposures left
        if self.exposures_left > 0:
            self.labelExposuresLeft.setText('%d exposure(s) left' % self.exposures_left)
        else:
            self.labelExposuresLeft.setText('')

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

    def _on_exposure_status_changed(self, event: ExposureStatusChangedEvent, sender: str):
        """Called when exposure status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name:
            return

        # store new status
        self.exposure_status = event.current

        # trigger GUI update
        self.signal_update_gui.emit()

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

        # download image
        self.image = self.vfs.read_image(event.filename)
        self.image_filename = event.filename
        self.new_image = True

        # auto save?
        if self.checkAutoSave.isChecked():
            # get path and check
            path = self.textAutoSavePath.text()
            if not os.path.exists(path):
                log.warning('Invalid path for auto-saving.')

            else:
                # save image
                filename = os.path.join(path, os.path.basename(self.image_filename.replace('.fits.gz', '.fits')))
                log.info('Saving image as %s...', filename)
                self.image.writeto(filename, overwrite=True)

        # update GUI
        self.signal_update_gui.emit()

    def select_autosave_path(self):
        """Select path for auto-saving."""

        # ask for path
        path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory")

        # set it
        if path:
            self.textAutoSavePath.setText(path)
        else:
            self.textAutoSavePath.clear()

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
