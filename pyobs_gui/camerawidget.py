import logging
from typing import Any
import qasync  # type: ignore
from PySide6 import QtWidgets, QtCore, QtGui  # type: ignore
from astroplan import Observer

from pyobs.comm import Comm
from pyobs.events import NewImageEvent
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
    IExposure,
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

        self.spinWindowLeft.init_modified(self.labelWindowLeft).committed.connect(self._window_changed)
        self.spinWindowTop.init_modified(self.labelWindowTop).committed.connect(self._window_changed)
        self.spinWindowWidth.init_modified(self.labelWindowWidth).committed.connect(self._window_changed)
        self.spinWindowHeight.init_modified(self.labelWindowHeight).committed.connect(self._window_changed)
        self.spinGain.init_modified(self.labelGain).committed.connect(self._gain_changed)
        self.spinGainOffset.init_modified(self.labelGain).committed.connect(self._gain_changed)

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
        async with self.comm.safe_proxy(self.module, IWindow) as proxy:
            if proxy is not None:
                await self.comm.subscribe_state(self.module, IWindow, self._update_window)
                await self.set_full_frame()

        # binning
        binning_caps = await self.comm.get_capabilities(self.module, IBinning)
        if binning_caps is not None:
            binnings = [f"{b.x}x{b.y}" for b in binning_caps.binnings]
            self.comboBinning.clear()
            self.comboBinning.addItems(binnings)
            await self.comm.subscribe_state(self.module, IBinning, self._update_binning)

        # gain — initial values delivered by subscription callback
        if await self.comm.has_proxy(self.module, IGain):
            await self.comm.subscribe_state(self.module, IGain, self._update_gain)

        # image format
        image_format_caps = await self.comm.get_capabilities(self.module, IImageFormat)
        if image_format_caps is not None:
            image_formats = [ImageFormat(f) for f in image_format_caps.image_formats]
            self.comboImageFormat.clear()
            self.comboImageFormat.addItems([f.name for f in image_formats])
            await self.comm.subscribe_state(self.module, IImageFormat, self._update_image_format)

        async with self.comm.safe_proxy(self.module, IImageType) as proxy:
            if proxy is not None:
                await self.comm.subscribe_state(self.module, IImageType, self._update_image_type)

        async with self.comm.safe_proxy(self.module, IExposure) as proxy:
            if proxy is not None:
                await self.comm.subscribe_state(self.module, IExposure, self._update_exposure)

        async with self.comm.safe_proxy(self.module, IExposureTime) as proxy:
            if proxy is not None:
                await self.comm.subscribe_state(self.module, IExposureTime, self._update_exposure_time)

        # update GUI
        self.signal_update_gui.emit()

    def _update_window(self, state: IWindow.State):
        self.labelWindowLeft.setText(str(state.x))
        self.labelWindowTop.setText(str(state.y))
        self.labelWindowWidth.setText(str(state.width))
        self.labelWindowHeight.setText(str(state.height))

    def _update_binning(self, state: IBinning.State):
        self.comboBinning.setCurrentText(f"{state.x}x{state.y}")

    def _update_gain(self, state: IGain.State):
        self.labelGain.setText(str(state.gain))
        self.labelGainOffset.setText(str(state.offset))

    def _update_image_format(self, state: IImageFormat.State):
        self.comboImageFormat.setCurrentText(state.image_format.name)

    def _update_image_type(self, state: IImageType.State):
        self.comboImageType.setCurrentText(state.image_type.name)

    def _update_exposure(self, state: IExposure.State):
        self.exposure_status = state.status
        self.exposure_progress = state.progress
        self.exposure_time_left = state.exposure_time_left
        self.update_gui()

    def _update_exposure_time(self, state: IExposureTime.State):
        self.spinExpTime.setValue(state.exposure_time)
        self.update_gui()

    @qasync.asyncSlot()
    async def _window_changed(self):
        print("ok")

    @qasync.asyncSlot()
    async def _gain_changed(self):
        print("ok")

    @qasync.asyncSlot()  # type: ignore
    async def set_full_frame(self) -> None:
        caps = await self.comm.get_capabilities(self.module, IWindow)
        if caps is not None:
            full_frame = caps.full_frame

            # get binning
            binning = 1
            if self.comboBinning.count() > 0 and await self.comm.has_proxy(self.module, IBinning):
                binning = int(self.comboBinning.currentText()[0])

            # max values
            self.spinWindowLeft.setMaximum(int(full_frame.width / binning))
            self.spinWindowTop.setMaximum(int(full_frame.height / binning))
            self.spinWindowWidth.setMaximum(int(full_frame.width / binning))
            self.spinWindowHeight.setMaximum(int(full_frame.height / binning))

            # set it
            self.spinWindowLeft.setValue(full_frame.x)
            self.spinWindowTop.setValue(full_frame.y)
            self.spinWindowWidth.setValue(int(full_frame.width / binning))
            self.spinWindowHeight.setValue(int(full_frame.height / binning))

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
        # set initial image count
        self.exposures_left = self.spinCount.value()

        # do exposure(s)
        while self.exposures_left > 0:
            # expose
            broadcast = self.checkBroadcast.isChecked()
            await self.datadisplay.grab_data(broadcast)

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
