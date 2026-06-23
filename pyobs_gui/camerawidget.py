import logging
from typing import Any
import qasync  # type: ignore
from PySide6 import QtWidgets, QtCore  # type: ignore
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


class CameraWidget(BaseWidget, Ui_CameraWidget):
    signal_update_gui = QtCore.Signal()
    signal_new_image = QtCore.Signal(NewImageEvent, str)

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)  # type: ignore

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
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
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
        self.groupWindowing.setVisible(await self.comm.has_proxy(self.module, IWindow))
        self.groupBinning.setVisible(await self.comm.has_proxy(self.module, IBinning))
        self.groupImageFormat.setVisible(await self.comm.has_proxy(self.module, IImageFormat))
        self.groupExpTime.setVisible(await self.comm.has_proxy(self.module, IExposureTime))
        self.groupGain.setVisible(await self.comm.has_proxy(self.module, IGain))

        # and single controls
        self.labelImageType.setVisible(await self.comm.has_proxy(self.module, IImageType))
        self.comboImageType.setVisible(await self.comm.has_proxy(self.module, IImageType))
        self.butAbort.setVisible(await self.comm.has_proxy(self.module, IAbortable))

        # initial values
        self.comboImageType.setCurrentIndex(image_types.index("OBJECT"))

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butFullFrame.clicked.connect(self.set_full_frame)
        self.comboBinning.currentTextChanged.connect(self.set_full_frame)
        self.checkBroadcast.stateChanged.connect(self.broadcast_changed)
        self.comboImageType.currentTextChanged.connect(self.image_type_changed)
        self.butExpose.clicked.connect(self.expose)
        self.butAbort.clicked.connect(self.abort)

        # subscribe to events
        await self.comm.register_event(ExposureStatusChangedEvent, self._on_exposure_status_changed)

        # fill sidebar
        await self.add_to_sidebar(self.create_widget(FitsHeadersWidget, module=self.module))
        if await self.comm.has_proxy(self.module, IFilters):
            await self.add_to_sidebar(self.create_widget(FilterWidget, module=self.module))
        if await self.comm.has_proxy(self.module, ICooling):
            await self.add_to_sidebar(self.create_widget(CoolingWidget, module=self.module))
        if await self.comm.has_proxy(self.module, ITemperatures):
            await self.add_to_sidebar(self.create_widget(TemperaturesWidget, module=self.module))

    async def _init(self) -> None:
        # get status
        async with self.comm.proxy(self.module, ICamera) as proxy:
            self.exposure_status = ExposureStatus(await proxy.get_exposure_status())

        # get binnings
        async with self.comm.safe_proxy(self.module, IBinning) as proxy:
            if proxy is not None:
                # get binnings
                # binnings = [f"{binning.x}x{binning.y}" for binning in await proxy.list_binnings()]
                binnings = ["%dx%d" % tuple(binning) for binning in await proxy.list_binnings()]

                # set it
                self.comboBinning.clear()
                self.comboBinning.addItems(binnings)

                # set default value
                self.comboBinning.setCurrentIndex(0)

        # get image formats
        async with self.comm.safe_proxy(self.module, IImageFormat) as proxy:
            if proxy is not None:
                # get formats
                image_formats = [ImageFormat(f) for f in await proxy.list_image_formats()]

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

        # gain
        async with self.comm.safe_proxy(self.module, IGain) as proxy:
            if proxy is not None:
                self.spinGain.setValue(await proxy.get_gain())
                self.spinGainOffset.setValue(await proxy.get_offset())

        # set full frame
        if await self.comm.has_proxy(self.module, IWindow):
            await self.set_full_frame()

        # update GUI
        self.signal_update_gui.emit()

    @qasync.asyncSlot()  # type: ignore
    async def set_full_frame(self) -> None:
        async with self.comm.safe_proxy(self.module, IWindow) as proxy:
            if proxy is not None:
                # get full frame
                left, top, width, height = await proxy.get_full_frame()

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

    @QtCore.Slot(int)  # type: ignore
    def broadcast_changed(self, state: int) -> None:
        if state == 0:
            r = QtWidgets.QMessageBox.question(
                self,
                "pyobs",
                "When disabling the broadcast, new images will not processed (and "
                "saved) within the pyobs network. Continue?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No,
            )
            if r == QtWidgets.QMessageBox.StandardButton.No:
                self.checkBroadcast.setChecked(True)

    @QtCore.Slot(str)  # type: ignore
    def image_type_changed(self, image_type: str) -> None:
        if image_type == "BIAS":
            self.spinExpTime.setValue(0)
            self.spinExpTime.setEnabled(False)
        else:
            self.spinExpTime.setEnabled(True)

    @qasync.asyncSlot()  # type: ignore
    async def expose(self) -> None:
        # set binning
        async with self.comm.safe_proxy(self.module, IBinning) as proxy:
            if proxy is not None:
                binning = int(self.comboBinning.currentText()[0])
                try:
                    await proxy.set_binning(binning, binning)
                except:
                    log.exception("bla")
                    QtWidgets.QMessageBox.information(self, "Error", "Could not set binning.")
                    return
            else:
                binning = 1

        # set window
        async with self.comm.safe_proxy(self.module, IWindow) as proxy:
            if proxy is not None:
                left, top = self.spinWindowLeft.value(), self.spinWindowTop.value()
                width, height = self.spinWindowWidth.value(), self.spinWindowHeight.value()
                try:
                    await proxy.set_window(left, top, width * binning, height * binning)
                except:
                    QtWidgets.QMessageBox.information(self, "Error", "Could not set window.")
                    return

        # set image format
        async with self.comm.safe_proxy(self.module, IImageFormat) as proxy:
            if proxy is not None:
                image_format = ImageFormat[self.comboImageFormat.currentText()]
                await proxy.set_image_format(image_format)

        # set exposure time
        async with self.comm.safe_proxy(self.module, IExposureTime) as proxy:
            if proxy is not None:
                # get exp_time
                exp_time = self.spinExpTime.value()

                # unit
                if self.comboExpTimeUnit.currentText() == "ms":
                    exp_time /= 1e3
                elif self.comboExpTimeUnit.currentText() == "µs":
                    exp_time /= 1e6

                # set it
                await proxy.set_exposure_time(exp_time)

        # set image type
        image_type = ImageType.OBJECT
        async with self.comm.safe_proxy(self.module, IImageType) as proxy:
            if proxy is not None:
                image_type = ImageType(self.comboImageType.currentText().lower())
                await proxy.set_image_type(image_type)

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

    @qasync.asyncSlot()  # type: ignore
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
            async with self.comm.safe_proxy(self.module, IAbortable) as proxy:
                if proxy is not None:
                    await proxy.abort()

    async def _update(self) -> None:
        module = self.module
        # are we exposing?
        if self.exposure_status == ExposureStatus.EXPOSING:
            # get camera status
            if isinstance(module, IExposureTime):
                self.exposure_time_left = await module.get_exposure_time_left()
            if isinstance(module, ICamera):
                self.exposure_progress = await module.get_exposure_progress()

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

    async def _on_exposure_status_changed(self, event: Event, sender: str) -> bool:
        """Called when exposure status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module or not isinstance(event, ExposureStatusChangedEvent):
            return False

        # store new status
        self.exposure_status = event.current

        # trigger GUI update
        self.signal_update_gui.emit()
        return True

    @qasync.asyncSlot()  # type: ignore
    async def set_gain(self) -> None:
        try:
            value = float(self.textGain.text())
        except ValueError:
            value = 0.0
        new_value, ok = QtWidgets.QInputDialog.getDouble(self, "Set camera gain", "New value", value, 0.0, 10000.0, 2)
        if ok:
            async with self.comm.proxy(self.module, IGain) as proxy:
                await proxy.set_gain(new_value)

    @qasync.asyncSlot()  # type: ignore
    async def set_offset(self) -> None:
        try:
            value = float(self.textOffset.text())
        except ValueError:
            value = 0.0
        new_value, ok = QtWidgets.QInputDialog.getDouble(
            self, "Set camera gain offset", "New value", value, 0.0, 60000.0, 2
        )
        if ok:
            async with self.comm.proxy(self.module, IGain) as proxy:
                await proxy.set_offset(new_value)
