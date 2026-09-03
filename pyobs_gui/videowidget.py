import asyncio
import logging
from typing import Any
from urllib.parse import urlparse

from astroplan import Observer
from pyobs.comm import Comm
from pyobs.interfaces import ExposureTimeState, GainState, IExposureTime, IGain, IVideo
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
    """Live MJPEG view of a module's video stream, plus exposure-time/gain controls. Paired with
    VideoGrabWidget (same IVideo interface, a separate tab) for the FITS-grab side -- the two
    don't share any state, mirroring how they were already independent halves of one class."""

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # store
        self.host: str | None = None
        self.port: int | None = None
        self.path: str | None = None

        # add live view
        self.widgetLiveView = ScaledLabel()
        self.frameLiveView.layout().addWidget(self.widgetLiveView)

        # connect signals
        self.spinExpTime.valueChanged.connect(self.exposure_time_changed)
        self.spinGain.valueChanged.connect(self.gain_changed)

        # before first update, disable myself
        self.setEnabled(False)

        # interfaces cache
        self._interfaces: list = []

        # init buffer
        self.buffer = b""

        # raw socket for the MJPEG stream; created once the video URL is known
        # (see _init), because its type depends on the URL scheme -- https needs
        # a TLS socket so the plaintext HTTP request survives a TLS-terminating
        # reverse proxy (e.g. nginx)
        self.socket: QtNetwork.QAbstractSocket | None = None
        self.scheme: str | None = None

        # Authorization header for the raw-socket stream request, taken from the
        # HttpFile the widget opens in _init (None when the VFS root configures no token)
        self._auth_header: str | None = None

        # whether the HTTP response headers of the current stream connection have
        # been stripped from self.buffer yet (see _received_data)
        self._headers_received = False

    async def open(
        self,
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)

    async def _init(self) -> None:
        # get interfaces for visibility checks
        self._interfaces = await self.comm.get_interfaces(self.module)
        has_exposure_time = IExposureTime in self._interfaces
        has_gain = IGain in self._interfaces

        # hide single controls, if necessary
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
        if caps.mjpeg is None:
            log.error("Module %s has no MJPEG video path.", self.module)
            return

        # open VFS file in executor to avoid blocking the event loop
        loop = asyncio.get_running_loop()
        try:
            video_file = await loop.run_in_executor(None, self.vfs.open_file, caps.mjpeg, "r")
        except Exception as e:
            log.error("Could not open video VFS path %s: %s", caps.mjpeg, e)
            return

        if not isinstance(video_file, HttpFile):
            log.error("VFS path to video of module %s must be an HttpFile.", self.module)
            return

        # keep the Authorization header (Bearer token) for the raw-socket stream request --
        # HttpFile sends it itself for VFS reads, but the stream bypasses HttpFile entirely
        self._auth_header = video_file.headers.get("Authorization")

        # parse URL
        o = urlparse(video_file.url)
        if o.scheme not in ["http", "https"]:
            log.error("URL scheme to video of module %s must be HTTP.", self.module)
            return

        if ":" in o.netloc:
            s = o.netloc.split(":")[:2]
            self.host, self.port = s[0], int(s[1])
        else:
            self.host, self.port = (o.netloc, 443 if o.scheme == "https" else 80)
        self.path = o.path
        self.scheme = o.scheme

        # create the raw socket for the stream; https URLs need a TLS socket so
        # the plaintext MJPEG request works through a TLS-terminating reverse
        # proxy (a plain QTcpSocket can only reach a plain-HTTP endpoint)
        self.socket = QtNetwork.QSslSocket() if self.scheme == "https" else QtNetwork.QTcpSocket()
        self.socket.readyRead.connect(self._received_data)
        if isinstance(self.socket, QtNetwork.QSslSocket):
            self.socket.sslErrors.connect(self._on_ssl_errors)

        # subscribe to state
        if has_exposure_time:
            await self.comm.subscribe_state(self.module, IExposureTime, self._on_exposure_time_state)
        if has_gain:
            await self.comm.subscribe_state(self.module, IGain, self._on_gain_state)

        # enable myself, now that init is done
        self.setEnabled(True)

    def _on_exposure_time_state(self, state: ExposureTimeState) -> None:
        self.spinExpTime.setValue(state.exposure_time)

    def _on_gain_state(self, state: GainState) -> None:
        self.spinGain.setValue(state.gain)

    async def _showEvent(self, event: QtGui.QShowEvent) -> None:
        # call base
        await BaseWidget._showEvent(self, event)

        # connect socket
        if self.host is not None and self.port is not None and self.path is not None and self.socket is not None:
            if self.scheme == "https":
                if not isinstance(self.socket, QtNetwork.QSslSocket):
                    log.error("Video URL of %s is https but no TLS socket was created.", self.module)
                    return
                self.socket.connectToHostEncrypted(self.host, self.port)
            else:
                self.socket.connectToHost(self.host, self.port)
            host_header = self.host if self.port == 80 else f"{self.host}:{self.port}"
            # HTTP/1.0 on purpose: HTTP/1.1 responses to an endless MJPEG stream use chunked
            # transfer encoding, and this raw-socket parser doesn't decode chunk framing --
            # the hex chunk-size lines would land inside the JPEG data and corrupt every
            # frame they fall in. HTTP/1.0 forbids chunked encoding, so the body arrives
            # as the plain MJPEG byte stream (with Connection: close, which just means the
            # stream runs until the client disconnects).
            self.socket.write(
                b"GET %s HTTP/1.0\r\nHost: %s\r\n" % (bytes(self.path, "UTF-8"), bytes(host_header, "UTF-8"))
                + (b"Authorization: %s\r\n" % bytes(self._auth_header, "UTF-8") if self._auth_header else b"")
                + b"\r\n"
            )
            # new connection: the next bytes start with the HTTP response headers
            self._headers_received = False

    def _on_ssl_errors(self, errors: list) -> None:
        """Log SSL errors from the video-stream socket instead of failing silently."""
        log.error("SSL errors connecting to video stream of %s: %s", self.module, errors)

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # call base
        BaseWidget.hideEvent(self, event)

        # disconnect socket
        if self.socket is not None:
            self.socket.disconnectFromHost()

    def _received_data(self) -> None:
        if self.socket is None:
            return
        boundary = b"--jpgboundary\r\n"
        self.buffer += bytes(self.socket.readAll())

        # strip the HTTP response headers before parsing the MJPEG body -- the
        # boundary string also appears in the "Content-Type: ... boundary=--jpgboundary"
        # header line, so parsing it as a frame would produce garbage
        if not self._headers_received:
            pos = self.buffer.find(b"\r\n\r\n")
            if pos == -1:
                return  # headers not complete yet
            self.buffer = self.buffer[pos + 4 :]
            self._headers_received = True

        while boundary in self.buffer:
            # find boundary
            pos = self.buffer.find(boundary)

            # find end of header
            frame = self.buffer[:pos]

            # remove from buffer
            self.buffer = self.buffer[pos + len(boundary) :]

            # find end of frame
            image_data = frame[frame.find(b"\r\n\r\n") + 4 :]
            if not image_data:
                # preamble before the first boundary (e.g. HTTP response headers)
                # or a frame with no payload yet -- nothing to show
                continue

            # to pixmap and show it
            qp = QtGui.QPixmap()
            qp.loadFromData(image_data)
            self.widgetLiveView.setPixmap(qp)

    def exposure_time_changed(self) -> None:
        # get exp_time
        exp_time = self.spinExpTime.value()

        # set it
        self.run_background(self._set_exposure_time, exp_time)

    async def _set_exposure_time(self, exp_time: float) -> None:
        if IExposureTime in self._interfaces:
            async with self.comm.proxy(self.module, IExposureTime) as proxy:
                await proxy.set_exposure_time(exp_time)

    def gain_changed(self) -> None:
        # get gain
        gain = self.spinGain.value()

        # set it
        self.run_background(self._set_gain, gain)

    async def _set_gain(self, gain: float) -> None:
        if IGain in self._interfaces:
            async with self.comm.proxy(self.module, IGain) as proxy:
                await proxy.set_gain(gain)


__all__ = ["VideoWidget"]
