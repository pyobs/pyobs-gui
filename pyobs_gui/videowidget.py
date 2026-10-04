import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any
from urllib.parse import urlencode, urlparse

import numpy as np
from astroplan import Observer
from numpy.typing import NDArray
from pyobs.comm import Comm
from pyobs.interfaces import ExposureTimeState, GainState, IExposureTime, IGain, IVideo
from pyobs.utils.stretch import CUTS_MODES, STRETCH_FUNCTIONS, StretchParams, stretch_to_uint8
from pyobs.vfs import HttpFile, VirtualFileSystem
from PySide6 import QtCore, QtGui, QtNetwork, QtWidgets  # type: ignore

from .accounts import _APPLICATION, _ORGANIZATION
from .base import BaseWidget
from .livestream import MjpegParser, RawFrame, RawParser, StreamError, fit_factor
from .qt.videowidget_ui import Ui_VideoWidget

log = logging.getLogger(__name__)

MJPEG = "mjpeg"
RAW = "raw"
_MODES = {MJPEG: "MJPEG (low bandwidth)", RAW: "Raw (full quality)"}

# cuts entry that sends no cuts at all (MJPEG: the module's default, raw: StretchParams' default)
_AUTO_CUTS = "auto"

# delay before a changed MJPEG setting or a resize reconnects, so typing into a spin box or
# dragging a window edge doesn't reconnect on every step
_RECONNECT_DELAY_MS = 500


class ScaledLabel(QtWidgets.QLabel):  # type: ignore
    resized = QtCore.Signal()

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
        self.resized.emit()


@dataclass
class _StreamUrl:
    """Where and how to request one of the camera's streams."""

    scheme: str
    host: str
    port: int
    path: str
    auth_header: str | None


def render_raw(data: NDArray[Any], params: StretchParams, source_dtype: str | None = None) -> QtGui.QImage:
    """Stretch a raw frame to 8 bit and turn it into a QImage. Runs in a worker thread.

    source_dtype is the frame's dtype before the server binned it (meta `SRCDTYPE`), which the cuts
    follow: binning turns integer data into float32.

    Flipped vertically like the server's JPEGs, since FITS rows go bottom-up.
    """
    img = np.ascontiguousarray(np.flip(stretch_to_uint8(data, params, dtype=source_dtype), axis=0))
    height, width = img.shape[:2]
    if img.ndim == 3 and img.shape[2] == 3:
        fmt = QtGui.QImage.Format.Format_RGB888
    elif img.ndim == 3 and img.shape[2] == 4:
        fmt = QtGui.QImage.Format.Format_RGBA8888
    else:
        if img.ndim == 3:
            img = np.ascontiguousarray(img[..., 0])
        fmt = QtGui.QImage.Format.Format_Grayscale8
    # copy, since the QImage would otherwise point into the numpy buffer
    return QtGui.QImage(img.data, width, height, img.strides[0], fmt).copy()


class VideoWidget(BaseWidget, Ui_VideoWidget):
    """Live view of a module's video stream, plus exposure-time/gain controls. Paired with
    VideoGrabWidget (same IVideo interface, a separate tab) for the FITS-grab side -- the two
    don't share any state, mirroring how they were already independent halves of one class.

    The live view either shows the MJPEG stream, stretched on the server, or reads the raw stream
    and stretches it here (see specs/2026-09-29-live-view-mjpeg-raw.md)."""

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # stream URLs by mode, known after _init
        self._urls: dict[str, _StreamUrl] = {}

        # current mode
        self._mode = MJPEG

        # add live view
        self.widgetLiveView = ScaledLabel()
        self.frameLiveView.layout().addWidget(self.widgetLiveView)

        # fill live view controls
        for mode, label in _MODES.items():
            self.comboMode.addItem(label, mode)
        for stretch in STRETCH_FUNCTIONS:
            self.comboStretch.addItem(stretch, stretch)
        for cuts in (_AUTO_CUTS, *CUTS_MODES):
            self.comboCuts.addItem(cuts, cuts)

        # connect signals
        self.spinExpTime.valueChanged.connect(self.exposure_time_changed)
        self.spinGain.valueChanged.connect(self.gain_changed)
        self.comboMode.currentIndexChanged.connect(self._mode_changed)
        self.comboStretch.currentIndexChanged.connect(self._stretch_changed)
        self.comboCuts.currentIndexChanged.connect(self._cuts_changed)
        self.spinLo.valueChanged.connect(self._stretch_changed)
        self.spinHi.valueChanged.connect(self._stretch_changed)
        self.spinQuality.valueChanged.connect(self._stream_params_changed)
        self.spinMaxRate.valueChanged.connect(self._stream_params_changed)
        self.widgetLiveView.resized.connect(self._reconnect_timer_start)

        # reconnects, delayed (see _RECONNECT_DELAY_MS)
        self._reconnect_timer = QtCore.QTimer(self)
        self._reconnect_timer.setSingleShot(True)
        self._reconnect_timer.setInterval(_RECONNECT_DELAY_MS)
        self._reconnect_timer.timeout.connect(self._on_reconnect_timer)

        # before first update, disable myself
        self.setEnabled(False)

        # interfaces cache
        self._interfaces: list = []

        # socket for the current stream, recreated on every connect, because its type depends on
        # the URL scheme -- https needs a TLS socket so the plaintext HTTP request survives a
        # TLS-terminating reverse proxy (e.g. nginx)
        self.socket: QtNetwork.QAbstractSocket | None = None
        self._parser: MjpegParser | RawParser | None = None

        # full frame size (width, height) and the downsampling factor requested from the server,
        # to fit the stream to the view; the size is only known after the first frame
        self._full_size: tuple[int, int] | None = None
        self._factor = 1

        # raw mode: newest frame, kept to re-render when the stretch changes; rendering happens in
        # a worker thread, and frames arriving while it's busy only replace the newest one
        self._raw_frame: RawFrame | None = None
        self._render_busy = False
        self._render_again = False
        self._executor: ThreadPoolExecutor | None = None
        self._render_error: str | None = None

        # settings are only saved once they have been restored for this camera
        self._settings_loaded = False

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

        # get video URLs from capabilities
        caps = await self.comm.get_capabilities(self.module, IVideo)
        if caps is None:
            log.error("Module %s has no IVideo capabilities.", self.module)
            return
        if not isinstance(self.vfs, VirtualFileSystem):
            log.error("Video is not available — no VFS.")
            return
        for mode, path in ((MJPEG, caps.mjpeg), (RAW, caps.raw)):
            if path is not None:
                url = await self._resolve_url(path)
                if url is not None:
                    self._urls[mode] = url
        if not self._urls:
            log.error("Module %s has no usable video stream.", self.module)
            return

        # only offer available modes
        for mode in _MODES:
            item = self.comboMode.model().item(self.comboMode.findData(mode))
            item.setEnabled(mode in self._urls)

        # restore settings for this camera, falling back to an available mode
        self._load_settings()
        if self._mode not in self._urls:
            self._mode = next(iter(self._urls))
        self._update_controls()
        self._settings_loaded = True

        # subscribe to state
        if has_exposure_time:
            await self.comm.subscribe_state(self.module, IExposureTime, self._on_exposure_time_state)
        if has_gain:
            await self.comm.subscribe_state(self.module, IGain, self._on_gain_state)

        # enable myself, now that init is done
        self.setEnabled(True)

        # _showEvent may already have run before the URLs were known
        if self.isVisible():
            self._connect()

    async def _resolve_url(self, path: str) -> _StreamUrl | None:
        """Get URL and Authorization header for a stream's VFS path."""
        # open VFS file in executor to avoid blocking the event loop
        loop = asyncio.get_running_loop()
        try:
            video_file = await loop.run_in_executor(None, self.vfs.open_file, path, "r")  # type: ignore[union-attr]
        except Exception as e:
            log.error("Could not open video VFS path %s: %s", path, e)
            return None
        if not isinstance(video_file, HttpFile):
            log.error("VFS path %s to video of module %s must be an HttpFile.", path, self.module)
            return None

        o = urlparse(video_file.url)
        if o.scheme not in ["http", "https"]:
            log.error("URL scheme to video of module %s must be HTTP.", self.module)
            return None
        if ":" in o.netloc:
            s = o.netloc.split(":")[:2]
            host, port = s[0], int(s[1])
        else:
            host, port = o.netloc, 443 if o.scheme == "https" else 80

        # keep the Authorization header (Bearer token) for the raw-socket stream request --
        # HttpFile sends it itself for VFS reads, but the stream bypasses HttpFile entirely
        return _StreamUrl(o.scheme, host, port, o.path, video_file.headers.get("Authorization"))

    def _on_exposure_time_state(self, state: ExposureTimeState) -> None:
        self.spinExpTime.setValue(state.exposure_time)

    def _on_gain_state(self, state: GainState) -> None:
        self.spinGain.setValue(state.gain)

    async def _showEvent(self, event: QtGui.QShowEvent) -> None:
        # call base
        await BaseWidget._showEvent(self, event)

        # connect socket
        self._connect()

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # call base
        BaseWidget.hideEvent(self, event)

        # disconnect socket
        self._reconnect_timer.stop()
        self._disconnect()

    # ── stream connection ──────────────────────────────────────────────────

    def _create_socket(self, scheme: str) -> QtNetwork.QAbstractSocket:
        # https URLs need a TLS socket so the plaintext request works through a TLS-terminating
        # reverse proxy (a plain QTcpSocket can only reach a plain-HTTP endpoint)
        return QtNetwork.QSslSocket() if scheme == "https" else QtNetwork.QTcpSocket()

    def _query(self) -> dict[str, str]:
        """Query parameters for the current mode's stream."""
        q: dict[str, str] = {}
        if self._mode == MJPEG:
            q["stretch"] = self.comboStretch.currentData()
            cuts = self.comboCuts.currentData()
            if cuts != _AUTO_CUTS:
                q["cuts"] = cuts
            if cuts in ("percentile", "manual"):
                q["lo"] = repr(self.spinLo.value())
                q["hi"] = repr(self.spinHi.value())
            if self._factor > 1:
                q["scale"] = str(self._factor)
            if self.spinQuality.value() > 0:
                q["quality"] = str(self.spinQuality.value())
        else:
            if self._factor > 1:
                q["bin"] = str(self._factor)
            if self.spinMaxRate.value() > 0:
                q["max_rate"] = repr(self.spinMaxRate.value())
        return q

    def _connect(self) -> None:
        """(Re)connect to the stream of the current mode."""
        self._disconnect()
        url = self._urls.get(self._mode)
        if url is None:
            return

        # new socket and parser
        socket = self._create_socket(url.scheme)
        socket.readyRead.connect(self._received_data)
        socket.disconnected.connect(self._on_disconnected)
        if isinstance(socket, QtNetwork.QSslSocket):
            socket.sslErrors.connect(self._on_ssl_errors)
        self.socket = socket
        self._parser = MjpegParser() if self._mode == MJPEG else RawParser()

        # connect
        if url.scheme == "https":
            if not isinstance(socket, QtNetwork.QSslSocket):
                log.error("Video URL of %s is https but no TLS socket was created.", self.module)
                return
            socket.connectToHostEncrypted(url.host, url.port)
        else:
            socket.connectToHost(url.host, url.port)

        # HTTP/1.0 on purpose: HTTP/1.1 responses to an endless stream use chunked transfer
        # encoding, and the parsers don't decode chunk framing -- the hex chunk-size lines would
        # land inside the frame data and corrupt it. HTTP/1.0 forbids chunked encoding, so the body
        # arrives as the plain byte stream (with Connection: close, which just means the stream
        # runs until the client disconnects).
        query = self._query()
        target = url.path + ("?" + urlencode(query) if query else "")
        host_header = url.host if url.port == 80 else f"{url.host}:{url.port}"
        socket.write(
            b"GET %s HTTP/1.0\r\nHost: %s\r\n" % (bytes(target, "UTF-8"), bytes(host_header, "UTF-8"))
            + (b"Authorization: %s\r\n" % bytes(url.auth_header, "UTF-8") if url.auth_header else b"")
            + b"\r\n"
        )

    def _disconnect(self) -> None:
        """Close the current stream, if any."""
        socket, self.socket, self._parser = self.socket, None, None
        if socket is None:
            return
        # detach first, so data or a disconnect still in flight doesn't reach the next stream
        socket.readyRead.disconnect(self._received_data)
        socket.disconnected.disconnect(self._on_disconnected)
        socket.abort()
        socket.deleteLater()

    def _on_disconnected(self) -> None:
        # we never close a stream without detaching first, so this is the server's doing
        log.warning("Live view stream of %s was closed by the server.", self.module)

    def _on_ssl_errors(self, errors: list) -> None:
        """Log SSL errors from the video-stream socket instead of failing silently."""
        log.error("SSL errors connecting to video stream of %s: %s", self.module, errors)

    def _received_data(self) -> None:
        if self.socket is None or self._parser is None:
            return
        try:
            frames = self._parser.feed(bytes(self.socket.readAll()))
        except (StreamError, ValueError, KeyError) as e:
            log.error("Invalid live view stream from %s: %s", self.module, e)
            self._disconnect()
            return

        # only the newest frame is of interest
        if not frames:
            return
        if self._mode == MJPEG:
            self._show_jpeg(frames[-1])
        else:
            self._show_raw(frames[-1])

    def _show_jpeg(self, jpeg: bytes) -> None:
        qp = QtGui.QPixmap()
        if not qp.loadFromData(jpeg):
            return
        self._set_full_size(qp.width() * self._factor, qp.height() * self._factor)
        self.widgetLiveView.setPixmap(qp)

    def _show_raw(self, frame: RawFrame) -> None:
        binning = int(frame.meta.get("SWBIN", 1))
        height, width = frame.data.shape[:2]
        self._set_full_size(width * binning, height * binning)
        self._raw_frame = frame
        self._render()

    # ── fit to view ────────────────────────────────────────────────────────

    def _set_full_size(self, width: int, height: int) -> None:
        """Store the full frame size; reconnect right away if the first frame shows that the
        current downsampling factor doesn't fit the view."""
        if self._full_size == (width, height):
            return
        self._full_size = (width, height)
        if self._fit_factor() != self._factor:
            self._factor = self._fit_factor()
            self._connect()

    def _fit_factor(self) -> int:
        if self._full_size is None:
            return 1
        view = self.widgetLiveView.size()
        return fit_factor(*self._full_size, view.width(), view.height())

    def _reconnect_timer_start(self) -> None:
        if self.socket is not None:
            self._reconnect_timer.start()

    def _on_reconnect_timer(self) -> None:
        if self.socket is None:
            return
        self._factor = self._fit_factor()
        self._connect()

    # ── client-side stretch (raw mode) ─────────────────────────────────────

    def _stretch_params(self) -> StretchParams:
        cuts = self.comboCuts.currentData()
        lo_hi = cuts in ("percentile", "manual")
        return StretchParams(
            stretch=self.comboStretch.currentData(),
            cuts=None if cuts == _AUTO_CUTS else cuts,
            lo=self.spinLo.value() if lo_hi else None,
            hi=self.spinHi.value() if lo_hi else None,
        )

    def _render(self) -> None:
        """Render the newest raw frame, unless a render is already running (it picks it up)."""
        if self._raw_frame is None:
            return
        if self._render_busy:
            self._render_again = True
            return
        self._render_busy = True
        asyncio.create_task(self._render_loop())

    async def _render_loop(self) -> None:
        loop = asyncio.get_running_loop()
        if self._executor is None:
            self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="liveview")
        try:
            while self._raw_frame is not None:
                self._render_again = False
                try:
                    params = self._stretch_params()
                    frame = self._raw_frame
                    image = await loop.run_in_executor(
                        self._executor, render_raw, frame.data, params, frame.meta.get("SRCDTYPE")
                    )
                except ValueError as e:
                    # e.g. invalid percentiles or "full" cuts on float data; log each problem once
                    if str(e) != self._render_error:
                        log.warning("Could not stretch live view of %s: %s", self.module, e)
                        self._render_error = str(e)
                else:
                    self._render_error = None
                    if self._mode == RAW:
                        self.widgetLiveView.setPixmap(QtGui.QPixmap.fromImage(image))
                if not self._render_again:
                    break
        finally:
            self._render_busy = False

    # ── controls ───────────────────────────────────────────────────────────

    def _update_controls(self) -> None:
        """Set the controls from the current mode and enable what applies to it."""
        with QtCore.QSignalBlocker(self.comboMode):
            self.comboMode.setCurrentIndex(self.comboMode.findData(self._mode))
        cuts = self.comboCuts.currentData()
        for w in (self.labelLo, self.spinLo, self.labelHi, self.spinHi):
            w.setEnabled(cuts in ("percentile", "manual"))
        for w in (self.labelQuality, self.spinQuality):
            w.setVisible(self._mode == MJPEG)
        for w in (self.labelMaxRate, self.spinMaxRate):
            w.setVisible(self._mode == RAW)

    def _mode_changed(self) -> None:
        self._mode = self.comboMode.currentData()
        self._raw_frame = None
        self._update_controls()
        self._save_settings()
        if self.socket is not None:
            self._connect()

    def _cuts_changed(self) -> None:
        # percentiles outside 0..100 (e.g. left over from manual cuts) would be rejected
        if self.comboCuts.currentData() == "percentile" and not (0 <= self.spinLo.value() < self.spinHi.value() <= 100):
            for spin, value in ((self.spinLo, 0.5), (self.spinHi, 99.5)):
                with QtCore.QSignalBlocker(spin):
                    spin.setValue(value)
        self._update_controls()
        self._stretch_changed()

    def _stretch_changed(self) -> None:
        """Stretch or cuts changed: raw re-renders the last frame, MJPEG needs a new stream."""
        self._save_settings()
        if self._mode == RAW:
            self._render()
        else:
            self._reconnect_timer_start()

    def _stream_params_changed(self) -> None:
        self._save_settings()
        self._reconnect_timer_start()

    # ── settings per camera ────────────────────────────────────────────────

    def _settings(self) -> QtCore.QSettings:
        return QtCore.QSettings(_ORGANIZATION, _APPLICATION)

    def _settings_key(self, name: str) -> str:
        return f"liveview/{self.module}/{name}"

    def _save_settings(self) -> None:
        if not self._settings_loaded:
            # still in _init, restoring
            return
        s = self._settings()
        s.setValue(self._settings_key("mode"), self._mode)
        s.setValue(self._settings_key("stretch"), self.comboStretch.currentData())
        s.setValue(self._settings_key("cuts"), self.comboCuts.currentData())
        s.setValue(self._settings_key("lo"), self.spinLo.value())
        s.setValue(self._settings_key("hi"), self.spinHi.value())
        s.setValue(self._settings_key("quality"), self.spinQuality.value())
        s.setValue(self._settings_key("max_rate"), self.spinMaxRate.value())

    def _load_settings(self) -> None:
        s = self._settings()

        mode = s.value(self._settings_key("mode"), MJPEG)
        self._mode = mode if mode in _MODES else MJPEG

        for combo, name in ((self.comboStretch, "stretch"), (self.comboCuts, "cuts")):
            index = combo.findData(s.value(self._settings_key(name)))
            if index >= 0:
                with QtCore.QSignalBlocker(combo):
                    combo.setCurrentIndex(index)

        spins: list[tuple[Any, str, type]] = [
            (self.spinLo, "lo", float),
            (self.spinHi, "hi", float),
            (self.spinQuality, "quality", int),
            (self.spinMaxRate, "max_rate", float),
        ]
        for spin, name, typ in spins:
            value = s.value(self._settings_key(name))
            if value is None:
                continue
            try:
                converted = typ(value)
            except (TypeError, ValueError):
                continue
            with QtCore.QSignalBlocker(spin):
                spin.setValue(converted)

    # ── exposure time and gain ─────────────────────────────────────────────

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
