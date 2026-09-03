import asyncio
import logging
from typing import Any
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
from .fitsheaderswidget import FitsHeadersWidget
from .qt.camerawidget_ui import Ui_CameraWidget

log = logging.getLogger(__name__)


# how long to wait for a module's first state value when initializing each control. The comm
# default is 10 s per interface, which would let a slow-publishing camera hold the page blank
# for ~70 s in the worst case; with this shorter timeout the control just keeps its default
# value and the subscription callback corrects it as soon as state arrives.
_WAIT_FOR_STATE_TIMEOUT = 2.0


class CameraWidget(BaseWidget, Ui_CameraWidget):
    signal_update_gui = QtCore.Signal()
    signal_new_image = QtCore.Signal(NewImageEvent, str)

    # declared sidebar fills (mainwindow.py, MAIN_WIDGETS/collect_main_widgets): consulted via
    # getattr(widget_class, "sidebar_fills", ...) so a site that wires CameraWidget in via
    # custom widgets: config still gets these. IFilters/ICooling/ITemperatures are NOT listed
    # here -- they're sidebar_preferred MAIN_WIDGETS entries, already demoted into the sidebar by
    # the promotion rule; declaring them here too would add each one twice (PR #157 review).
    sidebar_fills = [
        (None, FitsHeadersWidget),
    ]

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # scrollArea's horizontal scrollbar is off (this panel should never need to scroll
        # sideways), but with widgetResizable=True that leaves nothing to widen the scroll area
        # itself to fit its content -- it was clipping the right edge of every group box
        # (values/buttons ran past the visible border) because the .ui's Designer-time width hint
        # (239px) is narrower than the controls' actual required width. Size it from the real
        # content instead of a hardcoded guess; recomputed again at the end of _init() once
        # capability-dependent combo boxes (binning, image format) have their real items.
        self._size_scroll_area_to_content()

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

        # sidebar fills are applied by the page assembler (mainwindow.py: open_module_page),
        # driven by this class's sidebar_fills attribute -- see specs/2026-08-28-gui-main-vs-
        # sidebar-widgets.md, D2

    async def _init(self) -> None:
        # every interface is initialized independently (caps -> state -> subscribe, in that
        # order per interface), so run them concurrently instead of serially: a slow-publishing
        # camera used to hold the page blank for up to ~70 s (7 interfaces x the 10 s default
        # wait_for_state timeout); now each interface waits at most _WAIT_FOR_STATE_TIMEOUT and
        # the others fill in regardless
        await asyncio.gather(
            self._init_once("window", self._init_window),
            self._init_once("binning", self._init_binning),
            self._init_once("gain", self._init_gain),
            self._init_once("image_format", self._init_image_format),
            self._init_once("image_type", self._init_image_type),
            self._init_once("exposure", self._init_exposure),
            self._init_once("exposure_time", self._init_exposure_time),
            self._init_once("data_sequence", self._init_data_sequence),
        )

        # capability-dependent combo boxes (binning, image format) may have widened the panel
        # further, now that they're populated
        self._size_scroll_area_to_content()

        # update GUI
        self.signal_update_gui.emit()

    def _size_scroll_area_to_content(self) -> None:
        self.scrollArea.setMinimumWidth(self.scrollAreaWidgetContents.sizeHint().width())

    async def _init_window(self) -> None:
        # window
        window_caps = await self.comm.get_capabilities(self.module, IWindow)
        if window_caps is not None:
            self.spinWindowLeft.setMaximum(int(window_caps.full_frame_width))
            self.spinWindowTop.setMaximum(int(window_caps.full_frame_height))
            self.spinWindowWidth.setMaximum(int(window_caps.full_frame_width))
            self.spinWindowHeight.setMaximum(int(window_caps.full_frame_height))
        async with self.comm.safe_proxy(self.module, IWindow) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IWindow, timeout=_WAIT_FOR_STATE_TIMEOUT)
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

    async def _init_binning(self) -> None:
        # binning
        binning_caps = await self.comm.get_capabilities(self.module, IBinning)
        if binning_caps is not None:
            binnings = [f"{b.x}x{b.y}" for b in binning_caps.binnings]
            self.comboBinning.clear()
            self.comboBinning.addItems(binnings)
        async with self.comm.safe_proxy(self.module, IBinning) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IBinning, timeout=_WAIT_FOR_STATE_TIMEOUT)
                if state is not None:
                    self.comboBinning.setCurrentText(f"{state.x}x{state.y}")
                await self.comm.subscribe_state(self.module, IBinning, self._update_binning)

    async def _init_gain(self) -> None:
        # gain
        async with self.comm.safe_proxy(self.module, IGain) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IGain, timeout=_WAIT_FOR_STATE_TIMEOUT)
                if state is not None:
                    self.spinGain.setValue(state.gain)
                    self.spinGainOffset.setValue(state.offset)
                await self.comm.subscribe_state(self.module, IGain, self._update_gain)

    async def _init_image_format(self) -> None:
        # image format
        image_format_caps = await self.comm.get_capabilities(self.module, IImageFormat)
        if image_format_caps is not None:
            image_formats = [ImageFormat(f) for f in image_format_caps.image_formats]
            self.comboImageFormat.clear()
            self.comboImageFormat.addItems([f.name for f in image_formats])
        async with self.comm.safe_proxy(self.module, IImageFormat) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IImageFormat, timeout=_WAIT_FOR_STATE_TIMEOUT)
                if state is not None:
                    self.comboImageFormat.setCurrentText(state.image_format.name)
                await self.comm.subscribe_state(self.module, IImageFormat, self._update_image_format)

    async def _init_image_type(self) -> None:
        # image type
        async with self.comm.safe_proxy(self.module, IImageType) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IImageType, timeout=_WAIT_FOR_STATE_TIMEOUT)
                if state is not None:
                    self.comboImageType.setCurrentText(state.image_type.name)
                await self.comm.subscribe_state(self.module, IImageType, self._update_image_type)

    async def _init_exposure(self) -> None:
        # exposure (status, progress, time left)
        async with self.comm.safe_proxy(self.module, IExposure) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IExposure, timeout=_WAIT_FOR_STATE_TIMEOUT)
                if state is not None:
                    self.exposure_status = state.status
                    self.exposure_progress = state.progress
                    self.exposure_time_left = state.exposure_time_left
                await self.comm.subscribe_state(self.module, IExposure, self._update_exposure)

    async def _init_exposure_time(self) -> None:
        # exposure time
        async with self.comm.safe_proxy(self.module, IExposureTime) as proxy:
            if proxy is not None:
                state = await proxy.wait_for_state(IExposureTime, timeout=_WAIT_FOR_STATE_TIMEOUT)
                if state is not None:
                    self.spinExpTime.setValue(state.exposure_time)
                await self.comm.subscribe_state(self.module, IExposureTime, self._update_exposure_time)

    async def _init_data_sequence(self) -> None:
        # data sequence
        if await self.comm.has_proxy(self.module, IDataSequence):
            await self.comm.subscribe_state(self.module, IDataSequence, self._update_sequence)

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

    def set_full_frame(self) -> None:
        self.run_background(self._do_set_full_frame)

    async def _do_set_full_frame(self) -> None:
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

    def expose(self) -> None:
        self.run_background(self._do_expose)

    async def _do_expose(self) -> None:
        # set binning
        async with self.comm.safe_proxy(self.module, IBinning) as proxy:
            if proxy is not None:
                binning = int(self.comboBinning.currentText()[0])
                await proxy.set_binning(binning, binning)
            else:
                binning = 1

        # set window
        async with self.comm.safe_proxy(self.module, IWindow) as proxy:
            if proxy is not None:
                left, top = self.spinWindowLeft.value(), self.spinWindowTop.value()
                width, height = self.spinWindowWidth.value(), self.spinWindowHeight.value()
                await proxy.set_window(left, top, width * binning, height * binning)

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

        # if the module can grab a counted sequence server-side, let it -- but only when
        # broadcasting, since grab_sequence() doesn't hand filenames back to the caller and
        # the client has no other way to learn an image is ready to display
        if broadcast:
            async with self.comm.safe_proxy(self.module, IDataSequence) as proxy:
                if proxy is not None:
                    await proxy.grab_sequence(self.exposures_left, broadcast)
                    return

        # fall back to a client-side loop for modules that don't support IDataSequence, or
        # when not broadcasting (grab_data() returns the filename directly for display)
        while self.exposures_left > 0:
            await self.datadisplay.grab_data(broadcast)
            self.exposures_left -= 1
            self.signal_update_gui.emit()

    def abort(self) -> None:
        """Abort exposure."""
        # do we have a running exposure?
        if self.exposures_left == 0:
            return

        self.run_background(self._do_abort)

    async def _do_abort(self) -> None:
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
