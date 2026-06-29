import asyncio
import logging
from typing import Any, cast
from urllib.parse import urlparse

import qasync  # type: ignore
from astroplan import Observer
from pyobs.comm import Comm, Proxy
from pyobs.interfaces import IExposureTime, IGain, IImageFormat, IImageType, IVideo
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
        modules: list[Proxy] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)
        await self.datadisplay.open(modules=modules, comm=comm, observer=observer, vfs=vfs)

    async def _init(self) -> None:
        # hide single controls, if necessary
        self.labelImageType.setVisible(await self.comm.has_proxy(self.module, IImageType))
        self.comboImageType.setVisible(await self.comm.has_proxy(self.module, IImageType))
        self.groupExposure.setVisible(await self.comm.has_proxy(self.module, IExposureTime))
        self.groupGain.setVisible(await self.comm.has_proxy(self.module, IGain))

        # get video stream URL via capabilities
        caps = await self.comm.get_capabilities(self.module, IVideo)
        if caps is None or not caps.url:
            log.error("Module %s does not provide a video URL.", self.module)
            return
        if not isinstance(self.vfs, VirtualFileSystem):
            log.error("Video is not available.")
            return
        video_file = self.vfs.open_file(caps.url, "r")

        # we need an HttpFile
        if not isinstance(video_file, HttpFile):
            log.error("VFS path to video of module %s must be an HttpFile.", self.module)
            return

        # analyse URL
        o = urlparse(video_file.url)

        # scheme must be http
        # TODO: how to do HTTPS?
        if o.scheme != "http":
            log.error("URL scheme to video of module %s must be HTTP.", self.module)
            return

        # get info
        if ":" in o.netloc:
            s = o.netloc.split(":")[:2]
            self.host, self.port = s[0], int(s[1])
        else:
            self.host, self.port = (o.netloc, 80)
        self.path = o.path

        # subscribe to state — initial values delivered by callbacks
        if await self.comm.has_proxy(self.module, IExposureTime):
            await self.comm.subscribe_state(self.module, IExposureTime, self._on_exposure_time_state)
        if await self.comm.has_proxy(self.module, IGain):
            await self.comm.subscribe_state(self.module, IGain, self._on_gain_state)

        # update GUI
        self.signal_update_gui.emit()

    async def _showEvent(self, event: QtGui.QShowEvent) -> None:
        # call base
        await BaseWidget._showEvent(self, event)

        # connect socket
        if self.host is not None and self.port is not None and self.path is not None:
            self.socket.connectToHost(self.host, self.port)
            self.socket.write(b"GET %s HTTP/1.1\r\n\r\n" % bytes(self.path, "UTF-8"))

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # call base
        BaseWidget.hideEvent(self, event)

        # disconnect socket
        self.socket.disconnectFromHost()

    def _on_exposure_time_state(self, state: IExposureTime.State) -> None:
        self.spinExpTime.setValue(state.exposure_time)

    def _on_gain_state(self, state: IGain.State) -> None:
        self.spinGain.setValue(state.gain)

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
        async with self.comm.safe_proxy(self.module, IImageFormat) as proxy:
            if proxy is not None:
                image_format = ImageFormat[self.comboImageFormat.currentText()]
                await proxy.set_image_format(image_format)

        self.exposures_left = self.spinCount.value()
        self.signal_update_gui.emit()
        asyncio.create_task(self._expose_task_func())

    async def _expose_task_func(self) -> None:
        image_type = ImageType(self.comboImageType.currentText().lower())

        while self.exposures_left > 0:
            async with self.comm.safe_proxy(self.module, IImageType) as proxy:
                if proxy is not None:
                    await proxy.set_image_type(image_type)

            broadcast = self.checkBroadcast.isChecked()
            await self.datadisplay.grab_data(broadcast, image_type)

            self.exposures_left -= 1
            self.signal_update_gui.emit()

    @QtCore.Slot()  # type: ignore
    def abort_sequence(self) -> None:
        self.exposures_left = 0

    @qasync.asyncSlot()  # type: ignore
    async def exposure_time_changed(self) -> None:
        async with self.comm.safe_proxy(self.module, IExposureTime) as proxy:
            if proxy is not None:
                await proxy.set_exposure_time(self.spinExpTime.value())

    @qasync.asyncSlot()  # type: ignore
    async def gain_changed(self) -> None:
        async with self.comm.safe_proxy(self.module, IGain) as proxy:
            if proxy is not None:
                await proxy.set_gain(self.spinGain.value())


__all__ = ["VideoWidget"]
