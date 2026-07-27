import logging
from typing import Any
import qasync  # type: ignore
from PySide6 import QtWidgets, QtCore  # type: ignore
from astroplan import Observer

from pyobs.comm import Comm
from pyobs.events import NewImageEvent
from pyobs.interfaces import (
    IAbortable,
    IExposureTime,
    ExposureTimeState,
    IImageType,
    ImageTypeState,
    IImageFormat,
    ImageFormatState,
    IBinning,
    BinningState,
    IWindow,
    IFilters,
    ICooling,
    ITemperatures,
    IGain,
    GainState,
    IExposure,
    ExposureState,
    IDataSequence,
    DataSequenceState,
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
        BaseWidget.__init__(self, **kwargs)
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

        # before first update, disable myself
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

        # fill sidebar
        await self.add_to_sidebar(self.create_widget(FitsHeadersWidget, module=self.module))
        if await self.comm.has_proxy(self.module, IFilters):
            await self.add_to_sidebar(self.create_widget(FilterWidget, module=self.module))
        if await self.comm.has_proxy(self.module, ICooling):
            await self.add_to_sidebar(self.create_widget(CoolingWidget, module=self.module))
        if await self.comm.has_proxy(self.module, ITemperatures):
            await self.add_to_sidebar(self.create_widget(TemperaturesWidget, module=self.module))

    async def _init(self) -> None:
        # window
        window_caps = await self.comm.get_capabilities(self.module, IWindow)
        if window_caps is not None:
            self.spinWindowLeft.setMaximum(int(window_caps.full_frame_width))
            self.spinWindowTop.setMaximum(int(window_caps.full_frame_height))
            self.spinWindowWidth.setMaximum(int(window_caps.full_frame_width))
            self.spinWindowHeight.setMaximum(int(window_caps.full_frame_height))
        async with self.comm.safe_proxy(self.module, IWindow) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IWindow)
                if state is not None:
                    self.spinWindowLeft.setValue(state.x)
                    self.spinWindowTop.setValue(state.y)
                    self.spinWindowWidth.setValue(state.width)
                    self.spinWindowHeight.setValue(state.height)
                elif window_caps is not None:
                    self.spinWindowLeft.setValue(window_caps.full_frame_x)
                    self.spinWindowTop.setValue(window_caps.full_frame_y)
                    self.spinWindowWidth.setValue(window_caps.full_frame_width)
                    self.spinWindowHeight.setValue(window_caps.full_frame_height)

        # binning
        binning_caps = await self.comm.get_capabilities(self.module, IBinning)
        if binning_caps is not None:
            binnings = [f"{b.x}x{b.y}" for b in binning_caps.binnings]
            self.comboBinning.clear()
            self.comboBinning.addItems(binnings)
        async with self.comm.safe_proxy(self.module, IBinning) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IBinning)
                if state is not None:
                    self.comboBinning.setCurrentText(f"{state.x}x{state.y}")
        await self.comm.subscribe_state(self.module, IBinning, self._update_binning)

        # gain
        async with self.comm.safe_proxy(self.module, IGain) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IGain)
                if state is not None:
                    self.spinGain.setValue(state.gain)
                    self.spinGainOffset.setValue(state.offset)
        await self.comm.subscribe_state(self.module, IGain, self._update_gain)

        # image format
        image_format_caps = await self.comm.get_capabilities(self.module, IImageFormat)
        if image_format_caps is not None:
            image_formats = [ImageFormat(f) for f in image_format_caps.image_formats]
            self.comboImageFormat.clear()
            self.comboImageFormat.addItems([f.name for f in image_formats])
        async with self.comm.safe_proxy(self.module, IImageFormat) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IImageFormat)
                if state is not None:
                    self.comboImageFormat.setCurrentText(state.image_format.name)
        await self.comm.subscribe_state(self.module, IImageFormat, self._update_image_format)

        # image type
        async with self.comm.safe_proxy(self.module, IImageType) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IImageType)
                if state is not None:
                    self.comboImageType.setCurrentText(state.image_type.name)
        await self.comm.subscribe_state(self.module, IImageType, self._update_image_type)

        # exposure (status, progress, time left)
        async with self.comm.safe_proxy(self.module, IExposure) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IExposure)
                if state is not None:
                    self.exposure_status = state.status
                    self.exposure_progress = state.progress
                    self.exposure_time_left = state.exposure_time_left
        await self.comm.subscribe_state(self.module, IExposure, self._update_exposure)

        # exposure time
        async with self.comm.safe_proxy(self.module, IExposureTime) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IExposureTime)
                if state is not None:
                    self.spinExpTime.setValue(state.exposure_time)
        await self.comm.subscribe_state(self.module, IExposureTime, self._update_exposure_time)

        # data sequence
        if await self.comm.has_proxy(self.module, IDataSequence):
            await self.comm.subscribe_state(self.module, IDataSequence, self._update_sequence)

        # update GUI
        self.signal_update_gui.emit()

    def _update_binning(self, state: BinningState):
        self.comboBinning.setCurrentText(f"{state.x}x{state.y}")

    def _update_gain(self, state: GainState):
        self.spinGain.setValue(state.gain)
        self.spinGainOffset.setValue(state.offset)

    def _update_image_format(self, state: ImageFormatState):
        self.comboImageFormat.setCurrentText(state.image_format.name)

    def _update_image_type(self, state: ImageTypeState):
        self.comboImageType.setCurrentText(state.image_type.name)

    def _update_exposure(self, state: ExposureState):
        self.exposure_status = state.status
        self.exposure_progress = state.progress
        self.exposure_time_left = state.exposure_time_left
        self.update_gui()

    def _update_exposure_time(self, state: ExposureTimeState):
        self.spinExpTime.setValue(state.exposure_time)
        self.update_gui()

    def _update_sequence(self, state: DataSequenceState):
        self.exposures_left = state.count_left
        self.update_gui()

    @qasync.asyncSlot()  # type: ignore
    async def set_full_frame(self) -> None:
        caps = await self.comm.get_capabilities(self.module, IWindow)
        if caps is not None:
            # get binning
            binning = 1
            if self.comboBinning.count() > 0 and await self.comm.has_proxy(self.module, IBinning):
                binning = int(self.comboBinning.currentText()[0])

            # max values
            self.spinWindowLeft.setMaximum(int(caps.full_frame_width / binning))
            self.spinWindowTop.setMaximum(int(caps.full_frame_height / binning))
            self.spinWindowWidth.setMaximum(int(caps.full_frame_width / binning))
            self.spinWindowHeight.setMaximum(int(caps.full_frame_height / binning))

            # set it
            self.spinWindowLeft.setValue(caps.full_frame_x)
            self.spinWindowTop.setValue(caps.full_frame_y)
            self.spinWindowWidth.setValue(int(caps.full_frame_width / binning))
            self.spinWindowHeight.setValue(int(caps.full_frame_height / binning))

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
                except Exception:
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
                except Exception:
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

        # set gain and offset
        async with self.comm.safe_proxy(self.module, IGain) as proxy:
            if proxy is not None:
                await proxy.set_gain(self.spinGain.value())
                await proxy.set_offset(self.spinGainOffset.value())

        # set image type
        image_type = ImageType.OBJECT
        async with self.comm.safe_proxy(self.module, IImageType) as proxy:
            if proxy is not None:
                image_type = ImageType(self.comboImageType.currentText().lower())
                await proxy.set_image_type(image_type)

        # set initial image count
        self.exposures_left = self.spinCount.value()
        broadcast = self.checkBroadcast.isChecked()

        # if the module can grab a counted sequence server-side, let it
        async with self.comm.safe_proxy(self.module, IDataSequence) as proxy:
            if proxy is not None:
                await proxy.grab_sequence(self.exposures_left, broadcast)
                return

        # fall back to a client-side loop for modules that don't support IDataSequence
        while self.exposures_left > 0:
            await self.datadisplay.grab_data(broadcast)
            self.exposures_left -= 1
            self.signal_update_gui.emit()

    @qasync.asyncSlot()  # type: ignore
    async def abort(self) -> None:
        """Abort exposure."""
        # do we have a running exposure?
        if self.exposures_left == 0:
            return

        # got exposures left?
        if self.exposures_left > 1:
            # soft-stop the sequence server-side (current grab finishes normally), if
            # supported; otherwise just stop the client-side loop after the current grab
            async with self.comm.safe_proxy(self.module, IDataSequence) as proxy:
                if proxy is not None:
                    await proxy.abort_sequence()
                    return
            self.exposures_left = 0
        else:
            async with self.comm.safe_proxy(self.module, IAbortable) as proxy:
                if proxy is not None:
                    await proxy.abort()

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
