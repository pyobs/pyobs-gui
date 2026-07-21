import asyncio
import logging
from typing import Any
from urllib.parse import urlparse

import qasync  # type: ignore
from astroplan import Observer
from pyobs.comm import Comm
from pyobs.interfaces import (
    IExposureTime,
    ExposureTimeState,
    IGain,
    GainState,
    IImageFormat,
    IImageType,
    ImageTypeState,
    IVideo,
)
from pyobs.utils.enums import ImageFormat, ImageType
from pyobs.vfs import HttpFile, VirtualFileSystem
from PySide6 import QtCore, QtGui, QtNetwork, QtWidgets  # type: ignore

from .base import BaseWidget
from .qt.videowidget_ui import Ui_VideoWidget


log = logging.getLogger(__name__)


class ScaledLabel(QtWidgets.QLabel):  # type: ignore
    def __init__(self, **kwargs: Any):
        QtWidgets.QLabel.__init__(self, **kwargs)
        self._pixmap: QtGui.QPixmap | None = None
        self.setMinimumSize(QtCore.QSize(10, 10))

    def setPixmap(self, pixmap: QtGui.QPixmap) -> None:
        self._pixmap = pixmap
        scaled = pixmap.scaled(self.width(), self.height(), QtCore.Qt.AspectRatioMode.KeepAspectRatio)
        QtWidgets.QLabel.setPixmap(self, scaled)

    def resizeEvent(self, event: Any) -> None:
        if self._pixmap is not None:
            self.setPixmap(self._pixmap)


class VideoWidget(BaseWidget, Ui_VideoWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # store
        self.host: str | None = None
        self.port: int | None = None
        self.path: str | None = None
        self.exposures_left = 0

        # add live view
        self.widgetLiveView = ScaledLabel()
        self.frameLiveView.layout().addWidget(self.widgetLiveView)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonGrabImage.clicked.connect(self.grab_image)
        self.buttonAbort.clicked.connect(self.abort_sequence)
        self.spinExpTime.valueChanged.connect(self.exposure_time_changed)
        self.spinGain.valueChanged.connect(self.gain_changed)

        # before first update, disable mys
        self.setEnabled(False)

        # interfaces cache
        self._interfaces: list = []

        # init buffer
        self.buffer = b""

        # socket
        self.socket = QtNetwork.QTcpSocket()
        self.socket.readyRead.connect(self._received_data)

        # set exposure types
        image_types = sorted([it.name for it in ImageType])
        self.comboImageType.addItems(image_types)
        self.comboImageType.setCurrentText("OBJECT")

        # initial values
        self.comboImageType.setCurrentIndex(image_types.index("OBJECT"))

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

    async def _init(self) -> None:
        # get interfaces for visibility checks
        self._interfaces = await self.comm.get_interfaces(self.module)
        has_image_type = IImageType in self._interfaces
        has_exposure_time = IExposureTime in self._interfaces
        has_gain = IGain in self._interfaces

        # hide single controls, if necessary
        self.labelImageType.setVisible(has_image_type)
        self.comboImageType.setVisible(has_image_type)
        self.groupExposure.setVisible(has_exposure_time)
        self.groupGain.setVisible(has_gain)

        # get video URL from capabilities
        caps = await self.comm.get_capabilities(self.module, IVideo)
        if caps is None:
            log.error("Module %s has no IVideo capabilities.", self.module)
            return
        if not isinstance(self.vfs, VirtualFileSystem):
            log.error("Video is not available — no VFS.")
            return

        # open VFS file in executor to avoid blocking the event loop
        loop = asyncio.get_running_loop()
        try:
            video_file = await loop.run_in_executor(None, self.vfs.open_file, caps.video, "r")
        except Exception as e:
            log.error("Could not open video VFS path %s: %s", caps.video, e)
            return

        if not isinstance(video_file, HttpFile):
            log.error("VFS path to video of module %s must be an HttpFile.", self.module)
            return

        # parse URL
        o = urlparse(video_file.url)
        if o.scheme != "http":
            log.error("URL scheme to video of module %s must be HTTP.", self.module)
            return

        if ":" in o.netloc:
            s = o.netloc.split(":")[:2]
            self.host, self.port = s[0], int(s[1])
        else:
            self.host, self.port = (o.netloc, 80)
        self.path = o.path

        # subscribe to state
        if has_exposure_time:
            await self.comm.subscribe_state(self.module, IExposureTime, self._on_exposure_time_state)
        if has_gain:
            await self.comm.subscribe_state(self.module, IGain, self._on_gain_state)
        if has_image_type:
            await self.comm.subscribe_state(self.module, IImageType, self._on_image_type_state)

        # update GUI
        self.signal_update_gui.emit()

    def _on_exposure_time_state(self, state: ExposureTimeState) -> None:
        self.spinExpTime.setValue(state.exposure_time)

    def _on_gain_state(self, state: GainState) -> None:
        self.spinGain.setValue(state.gain)

    def _on_image_type_state(self, state: ImageTypeState) -> None:
        self.comboImageType.setCurrentText(state.image_type.name)

    async def _showEvent(self, event: QtGui.QShowEvent) -> None:
        # call base
        await BaseWidget._showEvent(self, event)

        # connect socket
        if self.host is not None and self.port is not None and self.path is not None:
            self.socket.connectToHost(self.host, self.port)
            host_header = self.host if self.port == 80 else f"{self.host}:{self.port}"
            self.socket.write(
                b"GET %s HTTP/1.1\r\nHost: %s\r\n\r\n" % (bytes(self.path, "UTF-8"), bytes(host_header, "UTF-8"))
            )

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # call base
        BaseWidget.hideEvent(self, event)

        # disconnect socket
        self.socket.disconnectFromHost()

    def update_gui(self) -> None:
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # enable/disable buttons
        self.buttonAbort.setEnabled(self.exposures_left > 0)

        # exposures left
        if self.exposures_left > 0:
            self.labelExposuresLeft.setText("%d exposure(s) left" % self.exposures_left)
        else:
            self.labelExposuresLeft.setText("")

    def _received_data(self) -> None:
        boundary = b"--jpgboundary\r\n"
        self.buffer += bytes(self.socket.readAll())
        while boundary in self.buffer:
            # find boundary
            pos = self.buffer.find(boundary)

            # find end of header
            frame = self.buffer[:pos]

            # remove from buffer
            self.buffer = self.buffer[pos + len(boundary) :]

            # find end of frame
            image_data = frame[frame.find(b"\r\n\r\n") + 4 :]

            # to pixmap and show it
            qp = QtGui.QPixmap()
            qp.loadFromData(image_data)
            self.widgetLiveView.setPixmap(qp)

    @qasync.asyncSlot()  # type: ignore
    async def grab_image(self) -> None:
        # set image format
        if IImageFormat in self._interfaces:
            image_format = ImageFormat[self.comboImageFormat.currentText()]  # type: ignore[attr-defined]
            async with self.comm.proxy(self.module, IImageFormat) as proxy:
                await proxy.set_image_format(image_format)

        # set initial image count
        self.exposures_left = self.spinCount.value()

        # signal GUI update
        self.signal_update_gui.emit()

        # start exposures
        asyncio.create_task(self._expose_task_func())

    async def _expose_task_func(self) -> None:
        # get image type
        image_type = ImageType(self.comboImageType.currentText().lower())

        # do exposure(s)
        while self.exposures_left > 0:
            # set image type
            if IImageType in self._interfaces:
                async with self.comm.proxy(self.module, IImageType) as proxy:
                    await proxy.set_image_type(image_type)

            # expose
            broadcast = self.checkBroadcast.isChecked()
            await self.datadisplay.grab_data(broadcast)

            # decrement number of exposures left
            self.exposures_left -= 1

            # signal GUI update
            self.signal_update_gui.emit()

    @QtCore.Slot()  # type: ignore
    def abort_sequence(self) -> None:
        self.exposures_left = 0

    @qasync.asyncSlot()  # type: ignore
    async def exposure_time_changed(self) -> None:
        # get exp_time
        exp_time = self.spinExpTime.value()

        # set it
        if IExposureTime in self._interfaces:
            async with self.comm.proxy(self.module, IExposureTime) as proxy:
                await proxy.set_exposure_time(exp_time)

    @qasync.asyncSlot()  # type: ignore
    async def gain_changed(self) -> None:
        # get gain
        gain = self.spinGain.value()

        # set it
        if IGain in self._interfaces:
            async with self.comm.proxy(self.module, IGain) as proxy:
                await proxy.set_gain(gain)


__all__ = ["VideoWidget"]
