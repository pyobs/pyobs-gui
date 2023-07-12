import asyncio
import logging
import os
from typing import Any, Optional, Union, Dict, List
from PyQt5 import QtWidgets, QtCore
from astroplan import Observer

from pyobs.comm import Proxy, Comm
from pyobs.events import ExposureStatusChangedEvent, NewImageEvent, Event
from pyobs.interfaces import (
    IAbortable,
    IExposureTime,
    IImageType,
    IImageFormat,
    IBinning,
    IWindow,
    IFilters,
    ICooling,
    ITemperatures,
    ICamera,
    IGain,
)
from pyobs.utils.enums import ImageType, ImageFormat, ExposureStatus
from pyobs.vfs import VirtualFileSystem
from .base import BaseWidget
from .coolingwidget import CoolingWidget
from .filterwidget import FilterWidget
from .temperatureswidget import TemperaturesWidget
from .fitsheaderswidget import FitsHeadersWidget
from .qt.camerawidget_ui import Ui_CameraWidget

log = logging.getLogger(__name__)


class CameraWidget(QtWidgets.QWidget, BaseWidget, Ui_CameraWidget):
    signal_update_gui = QtCore.pyqtSignal()
    signal_new_image = QtCore.pyqtSignal(NewImageEvent, str)

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)

        # variables
        self.new_image = False
        self.image_filename = None
        self.image = None
        self.status = None
        self.exposure_status = ExposureStatus.IDLE
        self.exposures_left = 0
        self.exposure_time_left = 0.0
        self.exposure_progress = 0.0

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

        # set exposure types
        image_types = sorted([it.name for it in ImageType])
        self.comboImageType.addItems(image_types)

        # before first update, disable mys
        self.setEnabled(False)

        # hide groups, if necessary
        self.groupWindowing.setVisible(isinstance(self.module, IWindow))
        self.groupBinning.setVisible(isinstance(self.module, IBinning))
        self.groupImageFormat.setVisible(isinstance(self.module, IImageFormat))
        self.groupExpTime.setVisible(isinstance(self.module, IExposureTime))
        self.groupGain.setVisible(isinstance(self.module, IGain))

        # and single controls
        self.labelImageType.setVisible(isinstance(self.module, IImageType))
        self.comboImageType.setVisible(isinstance(self.module, IImageType))
        self.butAbort.setVisible(isinstance(self.module, IAbortable))

        # initial values
        self.comboImageType.setCurrentIndex(image_types.index("OBJECT"))

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

        # subscribe to events
        await self.comm.register_event(ExposureStatusChangedEvent, self._on_exposure_status_changed)

        # fill sidebar
        await self.add_to_sidebar(self.create_widget(FitsHeadersWidget, module=self.module))
        if isinstance(self.module, IFilters):
            await self.add_to_sidebar(self.create_widget(FilterWidget, module=self.module))
        if isinstance(self.module, ICooling):
            await self.add_to_sidebar(self.create_widget(CoolingWidget, module=self.module))
        if isinstance(self.module, ITemperatures):
            await self.add_to_sidebar(self.create_widget(TemperaturesWidget, module=self.module))

    async def _init(self) -> None:
        # get status
        if isinstance(self.module, ICamera):
            self.exposure_status = ExposureStatus(await self.module.get_exposure_status())

        # get binnings
        if isinstance(self.module, IBinning):
            # get binnings
            binnings = ["%dx%d" % tuple(binning) for binning in await self.module.list_binnings()]

            # set it
            self.comboBinning.clear()
            self.comboBinning.addItems(binnings)

            # set default value
            self.comboBinning.setCurrentIndex(0)

        # get image formats
        if isinstance(self.module, IImageFormat):
            # get formats
            image_formats = [ImageFormat(f) for f in await self.module.list_image_formats()]

            # set it
            self.comboImageFormat.clear()
            self.comboImageFormat.addItems([f.name for f in image_formats])

            # find default value
            if ImageFormat.INT16 in image_formats:
                self.comboImageFormat.setCurrentText("INT16")
            elif ImageFormat.INT8 in image_formats:
                self.comboImageFormat.setCurrentText("INT8")
            else:
                self.comboImageFormat.setCurrentIndex(0)

        # set full frame
        await self.set_full_frame()

        # update GUI
        self.signal_update_gui.emit()

    @QtCore.pyqtSlot(name="on_butFullFrame_clicked")
    def _set_full_frame(self) -> None:
        asyncio.create_task(self.set_full_frame())

    async def set_full_frame(self) -> None:
        if isinstance(self.module, IWindow):
            # get full frame
            left, top, width, height = await self.module.get_full_frame()

            # get binning
            binning = int(self.comboBinning.currentText()[0]) if isinstance(self.module, IBinning) else 1

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

    @QtCore.pyqtSlot(str, name="on_comboBinning_currentTextChanged")
    def binning_changed(self, binning: str) -> None:
        self.on_butFullFrame_clicked()

    @QtCore.pyqtSlot(int, name="on_checkBroadcast_stateChanged")
    def broadcast_changed(self, state: int) -> None:
        if state == 0:
            r = QtWidgets.QMessageBox.question(
                self,
                "pyobs",
                "When disabling the broadcast, new images will not processed (and "
                "saved) within the pyobs network. Continue?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
                QtWidgets.QMessageBox.No,
            )
            if r == QtWidgets.QMessageBox.No:
                self.checkBroadcast.setChecked(True)

    @QtCore.pyqtSlot(str, name="on_comboImageType_currentTextChanged")
    def image_type_changed(self, image_type: str) -> None:
        if image_type == "BIAS":
            self.spinExpTime.setValue(0)
            self.spinExpTime.setEnabled(False)
        else:
            self.spinExpTime.setEnabled(True)

    @QtCore.pyqtSlot(name="on_butExpose_clicked")
    def _expose(self) -> None:
        asyncio.create_task(self.expose())

    async def expose(self) -> None:
        # set binning
        if isinstance(self.module, IBinning):
            binning = int(self.comboBinning.currentText()[0])
            try:
                await self.module.set_binning(binning, binning)
            except:
                log.exception("bla")
                QtWidgets.QMessageBox.information(self, "Error", "Could not set binning.")
                return
        else:
            binning = 1

        # set window
        if isinstance(self.module, IWindow):
            left, top = self.spinWindowLeft.value(), self.spinWindowTop.value()
            width, height = self.spinWindowWidth.value(), self.spinWindowHeight.value()
            try:
                await self.module.set_window(left, top, width * binning, height * binning)
            except:
                QtWidgets.QMessageBox.information(self, "Error", "Could not set window.")
                return

        # set image format
        if isinstance(self.module, IImageFormat):
            image_format = ImageFormat[self.comboImageFormat.currentText()]
            await self.module.set_image_format(image_format)

        # set exposure time
        if isinstance(self.module, IExposureTime):
            # get exp_time
            exp_time = self.spinExpTime.value()

            # unit
            if self.comboExpTimeUnit.currentText() == "ms":
                exp_time /= 1e3
            elif self.comboExpTimeUnit.currentText() == "µs":
                exp_time /= 1e6

            # set it
            await self.module.set_exposure_time(exp_time)

        # set image type
        image_type = ImageType.OBJECT
        if isinstance(self.module, IImageType):
            image_type = ImageType(self.comboImageType.currentText().lower())
            await self.module.set_image_type(image_type)

        # set gain
        if isinstance(self.module, IGain):
            await self.module.set_gain(self.spinGain.value())

        # set initial image count
        self.exposures_left = self.spinCount.value()

        # do exposure(s)
        while self.exposures_left > 0:
            # expose
            broadcast = self.checkBroadcast.isChecked()
            await self.datadisplay.grab_data(broadcast, image_type)

            # decrement number of exposures left
            self.exposures_left -= 1

            # signal GUI update
            self.signal_update_gui.emit()

    def plot(self) -> None:
        """Show image."""
        self.imageView.display(self.image)

    @QtCore.pyqtSlot(name="on_butAbort_clicked")
    def _abort(self) -> None:
        asyncio.create_task(self.abort())

    async def abort(self) -> None:
        """Abort exposure."""

        # do we have a running exposure?
        if self.exposures_left == 0:
            return

        # got exposures left?
        if self.exposures_left > 1:
            # abort sequence
            self.exposures_left = 0
        else:
            if isinstance(self.module, ICamera):
                await self.module.abort()

    async def _update(self) -> None:
        # are we exposing?
        if self.exposure_status == ExposureStatus.EXPOSING:
            # get camera status
            if isinstance(self.module, IExposureTime):
                self.exposure_time_left = await self.module.get_exposure_time_left()
            if isinstance(self.module, ICamera):
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

        # set abort text
        if self.exposures_left > 1:
            self.butAbort.setText("Abort sequence")
        else:
            self.butAbort.setText("Abort exposure")

        # set progress
        msg = ""
        if self.exposure_status == ExposureStatus.IDLE:
            self.progressExposure.setValue(0)
            msg = "IDLE"
        elif self.exposure_status == ExposureStatus.EXPOSING:
            self.progressExposure.setValue(int(self.exposure_progress))
            msg = "EXPOSING %.1fs" % self.exposure_time_left
        elif self.exposure_status == ExposureStatus.READOUT:
            self.progressExposure.setValue(100)
            msg = "READOUT"

        # set message
        self.labelStatus.setText(msg)

        # exposures left
        if self.exposures_left > 0:
            self.labelExposuresLeft.setText("%d exposure(s) left" % self.exposures_left)
        else:
            self.labelExposuresLeft.setText("")

        # trigger image update
        if self.new_image and self.image_filename is not None:
            # set filename
            self.tabWidget.setTabText(0, os.path.basename(self.image_filename))

            # plot image
            self.plot()

            # set fits headers
            self.show_fits_headers()

            # reset
            self.new_image = False

    def show_fits_headers(self) -> None:
        # check
        if self.image is None:
            return

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

    async def _on_exposure_status_changed(self, event: Event, sender: str) -> bool:
        """Called when exposure status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if self.module is None or sender != self.module.name or not isinstance(event, ExposureStatusChangedEvent):
            return False

        # store new status
        self.exposure_status = event.current

        # trigger GUI update
        self.signal_update_gui.emit()
        return True
