import asyncio
import logging
from typing import Any, Optional, cast, Union, Dict, List
from urllib.parse import urlparse
from PyQt5 import QtWidgets, QtCore, QtGui, QtNetwork
from astroplan import Observer

from pyobs.comm import Proxy, Comm

from pyobs.interfaces import IExposureTime, IImageType, IImageFormat, IVideo, IGain
from pyobs.modules import Module
from pyobs.utils.enums import ImageFormat, ImageType
from pyobs.vfs import HttpFile, VirtualFileSystem
from .base import BaseWidget
from .qt.videowidget_ui import Ui_VideoWidget
from .datadisplaywidget import DataDisplayWidget

log = logging.getLogger(__name__)


class ScaledLabel(QtWidgets.QLabel):
    def __init__(self, **kwargs: Any):
        QtWidgets.QLabel.__init__(self, **kwargs)
        self._pixmap = None
        self.setMinimumSize(QtCore.QSize(10, 10))

    def setPixmap(self, pixmap: QtGui.QPixmap) -> None:
        self._pixmap = pixmap
        scaled = pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio)
        QtWidgets.QLabel.setPixmap(self, scaled)

    def resizeEvent(self, event: Any) -> None:
        if self._pixmap is not None:
            self.setPixmap(self._pixmap)


class VideoWidget(QtWidgets.QWidget, BaseWidget, Ui_VideoWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # store
        self.host: Optional[str] = None
        self.port: Optional[int] = None
        self.path: Optional[str] = None
        self.exposures_left = 0

        # add live view
        self.widgetLiveView = ScaledLabel()
        self.frameLiveView.layout().addWidget(self.widgetLiveView)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

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
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)
        await self.datadisplay.open(modules=modules, comm=comm, observer=observer, vfs=vfs)

    async def _init(self) -> None:
        # hide single controls, if necessary
        self.labelImageType.setVisible(isinstance(self.module, IImageType))
        self.comboImageType.setVisible(isinstance(self.module, IImageType))
        self.groupExposure.setVisible(isinstance(self.module, IExposureTime))
        self.groupGain.setVisible(isinstance(self.module, IGain))

        # get video stream URL and open it
        if not isinstance(self.module, IVideo) or self.module is None:
            log.error("Module is not an IVideo.")
            return
        video_path = await self.module.get_video()
        video_file = self.vfs.open_file(video_path, "r")

        # we heed a HttpFile
        if not isinstance(video_file, HttpFile):
            log.error("VFS path to video of module %s must be an HttpFile.", cast(Module, self.module).name)
            return

        # analyse URL
        o = urlparse(video_file.url)

        # scheme must be http
        # TODO: how to do HTTPS?
        if o.scheme != "http":
            log.error("URL scheme to video of module %s must be HTTP.", cast(Module, self.module).name)
            return

        # get info
        (self.host, self.port) = tuple(o.netloc.split(":")[:2]) if ":" in o.netloc else (o.netloc, 80)
        self.path = o.path

        # get initial values
        if isinstance(self.module, IExposureTime):
            self.spinExpTime.setValue(await self.module.get_exposure_time())
        if isinstance(self.module, IGain):
            self.spinGain.setValue(await self.module.get_gain())

        # update GUI
        self.signal_update_gui.emit()

    async def _showEvent(self, event: QtGui.QShowEvent) -> None:
        # call base
        await BaseWidget._showEvent(self, event)

        # connect socket
        if self.host is not None and self.port is not None and self.path is not None:
            self.socket.connectToHost(self.host, int(self.port))
            self.socket.write(b"GET %s HTTP/1.1\r\n\r\n" % bytes(self.path, "UTF-8"))

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

    @QtCore.pyqtSlot(name="on_buttonGrabImage_clicked")
    def grab_image(self) -> None:
        # set image format
        if isinstance(self.module, IImageFormat):
            image_format = ImageFormat[self.comboImageFormat.currentText()]
            self.module.set_image_format(image_format)

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
            if isinstance(self.module, IImageType):
                await self.module.set_image_type(image_type)

            # expose
            broadcast = self.checkBroadcast.isChecked()
            await self.datadisplay.grab_data(broadcast, image_type)

            # decrement number of exposures left
            self.exposures_left -= 1

            # signal GUI update
            self.signal_update_gui.emit()

    @QtCore.pyqtSlot(name="on_buttonAbort_clicked")
    def abort_sequence(self) -> None:
        self.exposures_left = 0

    @QtCore.pyqtSlot(float, name="on_spinExpTime_valueChanged")
    def exposure_time_changed(self) -> None:
        # get exp_time
        exp_time = self.spinExpTime.value()

        # set it
        if isinstance(self.module, IExposureTime):
            asyncio.create_task(self.module.set_exposure_time(exp_time))

    @QtCore.pyqtSlot(float, name="on_spinGain_valueChanged")
    def gain_changed(self) -> None:
        # get gain
        gain = self.spinGain.value()

        # set it
        if isinstance(self.module, IGain):
            asyncio.create_task(self.module.set_gain(gain))


__all__ = ["VideoWidget"]
