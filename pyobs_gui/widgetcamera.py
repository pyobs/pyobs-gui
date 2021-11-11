import logging
import os
import threading
from typing import Any

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QMessageBox

from pyobs.events import ExposureStatusChangedEvent, NewImageEvent
from pyobs.interfaces.proxies import IAbortableProxy, IExposureTimeProxy, IImageTypeProxy, IImageFormatProxy, \
    IBinningProxy, IWindowProxy, IFiltersProxy, ICoolingProxy, ITemperaturesProxy, ICameraProxy
from pyobs.utils.enums import ImageType, ImageFormat, ExposureStatus
from pyobs.images import Image
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.basewidget import BaseWidget
from pyobs_gui.widgetcooling import WidgetCooling
from pyobs_gui.widgetfilter import WidgetFilter
from pyobs_gui.widgettemperatures import WidgetTemperatures
from pyobs_gui.widgetfitsheaders import WidgetFitsHeaders
from .qt.widgetcamera import Ui_WidgetCamera
from .widgetdatadisplay import WidgetDataDisplay

log = logging.getLogger(__name__)


class WidgetCamera(BaseWidget, Ui_WidgetCamera):
    signal_update_gui = pyqtSignal()
    signal_new_image = pyqtSignal(NewImageEvent, str)

    def __init__(self, **kwargs):
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
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

        # data display
        self.widgetDataDisplay = self.create_widget(WidgetDataDisplay, module=self.module)
        self.frameDataDisplay.layout().addWidget(self.widgetDataDisplay)

        # set exposure types
        image_types = sorted([it.name for it in ImageType])
        self.comboImageType.addItems(image_types)

        # before first update, disable mys
        self.setEnabled(False)

        # hide groups, if necessary
        self.groupWindowing.setVisible(isinstance(self.module, IWindowProxy))
        self.groupBinning.setVisible(isinstance(self.module, IBinningProxy))
        self.groupImageFormat.setVisible(isinstance(self.module, IImageFormatProxy))

        # and single controls
        self.labelImageType.setVisible(isinstance(self.module, IImageTypeProxy))
        self.comboImageType.setVisible(isinstance(self.module, IImageTypeProxy))
        self.labelExpTime.setVisible(isinstance(self.module, IExposureTimeProxy))
        self.spinExpTime.setVisible(isinstance(self.module, IExposureTimeProxy))
        self.comboExpTimeUnit.setVisible(isinstance(self.module, IExposureTimeProxy))
        self.butAbort.setVisible(isinstance(self.module, IAbortableProxy))

        # initial values
        self.comboImageType.setCurrentIndex(image_types.index('OBJECT'))

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

        # subscribe to events
        self.comm.register_event(ExposureStatusChangedEvent, self._on_exposure_status_changed)

        # fill sidebar
        self.add_to_sidebar(self.create_widget(WidgetFitsHeaders, module=self.module))
        if isinstance(self.module, IFiltersProxy):
            self.add_to_sidebar(self.create_widget(WidgetFilter, module=self.module))
        if isinstance(self.module, ICoolingProxy):
            self.add_to_sidebar(self.create_widget(WidgetCooling, module=self.module))
        if isinstance(self.module, ITemperaturesProxy):
            self.add_to_sidebar(self.create_widget(WidgetTemperatures, module=self.module))

    def _init(self):
        # get status
        if isinstance(self.module, ICameraProxy):
            self.exposure_status = ExposureStatus(self.module.get_exposure_status().wait())

        # get binnings
        if isinstance(self.module, IBinningProxy):
            # get binnings
            binnings = ['%dx%d' % tuple(binning) for binning in self.module.list_binnings().wait()]

            # set it
            self.comboBinning.clear()
            self.comboBinning.addItems(binnings)

            # set default value
            self.comboBinning.setCurrentIndex(0)

        # get image formats
        if isinstance(self.module, IImageFormatProxy):
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

    @pyqtSlot(name='on_butFullFrame_clicked')
    def set_full_frame(self):
        if isinstance(self.module, IWindowProxy):
            # get full frame
            left, top, width, height = self.module.get_full_frame().wait()

            # get binning
            binning = int(self.comboBinning.currentText()[0]) if isinstance(self.module, IBinningProxy) else 1

            # max values
            self.spinWindowLeft.setMaximum(int(width / binning))
            self.spinWindowTop.setMaximum(int(height / binning))
            self.spinWindowWidth.setMaximum(int(width / binning))
            self.spinWindowHeight.setMaximum(int(height / binning))

            # set it
            self.spinWindowLeft.setValue(left)
            self.spinWindowTop.setValue(top)
            self.spinWindowWidth.setValue(int(width / binning))
            self.spinWindowHeight.setValue(int(height / binning))

    @pyqtSlot(str, name='on_comboBinning_currentTextChanged')
    def binning_changed(self, binning):
        self.set_full_frame()

    @pyqtSlot(int, name='on_checkBroadcast_stateChanged')
    def broadcast_changed(self, state):
        if state == 0:
            r = QMessageBox.question(self, 'pyobs', 'When disabling the broadcast, new images will not processed (and '
                                                    'saved) within the pyobs network. Continue?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if r == QMessageBox.No:
                self.checkBroadcast.setChecked(True)

    @pyqtSlot(str, name='on_comboImageType_currentTextChanged')
    def image_type_changed(self, image_type):
        if image_type == 'BIAS':
            self.spinExpTime.setValue(0)
            self.spinExpTime.setEnabled(False)
        else:
            self.spinExpTime.setEnabled(True)

    @pyqtSlot(name='on_butExpose_clicked')
    def expose(self):
        # set binning
        if isinstance(self.module, IBinningProxy):
            binning = int(self.comboBinning.currentText()[0])
            try:
                self.module.set_binning(binning, binning).wait()
            except:
                log.exception('bla')
                QMessageBox.information(self, 'Error', 'Could not set binning.')
                return
        else:
            binning = 1

        # set window
        if isinstance(self.module, IWindowProxy):
            left, top = self.spinWindowLeft.value(), self.spinWindowTop.value()
            width, height = self.spinWindowWidth.value(), self.spinWindowHeight.value()
            try:
                self.module.set_window(left, top, width * binning, height * binning).wait()
            except:
                QMessageBox.information(self, 'Error', 'Could not set window.')
                return

        # set image format
        if isinstance(self.module, IImageFormatProxy):
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
            # set exposure time
            if isinstance(self.module, IExposureTimeProxy):
                # get exp_time
                exp_time = self.spinExpTime.value()

                # unit
                if self.comboExpTimeUnit.currentText() == 'ms':
                    exp_time /= 1e3
                elif self.comboExpTimeUnit.currentText() == 'µs':
                    exp_time /= 1e6

                # set it
                self.module.set_exposure_time(exp_time).wait()

            # set image type
            if isinstance(self.module, IImageTypeProxy):
                self.module.set_image_type(image_type)

            # expose
            broadcast = self.checkBroadcast.isChecked()
            self.widgetDataDisplay.grab_data(broadcast, image_type)

            # decrement number of exposures left
            self.exposures_left -= 1

            # signal GUI update
            self.signal_update_gui.emit()

    def plot(self):
        """Show image."""
        self.imageView.display(self.image)

    @pyqtSlot(name='on_butAbort_clicked')
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

        # set abort text
        if self.exposures_left > 1:
            self.butAbort.setText('Abort sequence')
        else:
            self.butAbort.setText('Abort exposure')

        # set progress
        msg = ''
        if self.exposure_status == ExposureStatus.IDLE:
            self.progressExposure.setValue(0)
            msg = 'IDLE'
        elif self.exposure_status == ExposureStatus.EXPOSING:
            self.progressExposure.setValue(int(self.exposure_progress))
            msg = 'EXPOSING %.1fs' % self.exposure_time_left
        elif self.exposure_status == ExposureStatus.READOUT:
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
