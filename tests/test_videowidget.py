import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from PySide6 import QtCore, QtGui

from pyobs_gui.livestream import RawFrame
from pyobs_gui.videowidget import MJPEG, RAW, VideoWidget, _StreamUrl, render_raw


def _widget(
    tmp_path: Path, mode: str = MJPEG, auth: str | None = None, urls: tuple[str, ...] = (MJPEG, RAW)
) -> tuple[VideoWidget, list[MagicMock]]:
    """VideoWidget with known stream URLs and mocked sockets (one per connect), skipping _init."""
    widget = VideoWidget()
    widget._initialized = True
    widget.modules = ["cam"]
    all_urls = {
        MJPEG: _StreamUrl("http", "localhost", 37077, "/webcam/video.mjpg", auth),
        RAW: _StreamUrl("http", "localhost", 37077, "/webcam/video.raw", auth),
    }
    widget._urls = {m: all_urls[m] for m in urls}
    widget._mode = mode
    settings = QtCore.QSettings(str(tmp_path / "settings.ini"), QtCore.QSettings.Format.IniFormat)
    widget._settings = lambda: settings  # type: ignore[method-assign]
    widget._settings_loaded = True
    sockets: list[MagicMock] = []

    def create_socket(scheme: str) -> MagicMock:
        sockets.append(MagicMock())
        return sockets[-1]

    widget._create_socket = create_socket  # type: ignore[method-assign]
    return widget, sockets


def _request(socket: MagicMock) -> bytes:
    return socket.write.call_args[0][0]


# ── request ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_show_event_sends_authorization_header_when_token_configured(tmp_path: Path) -> None:
    widget, sockets = _widget(tmp_path, auth="Bearer secret")
    await widget._showEvent(MagicMock())
    written = _request(sockets[-1])
    assert written.startswith(b"GET /webcam/video.mjpg?stretch=linear HTTP/1.0\r\nHost: localhost:37077\r\n")
    assert b"Authorization: Bearer secret\r\n" in written
    assert written.endswith(b"\r\n\r\n")
    widget.close()


@pytest.mark.asyncio
async def test_show_event_sends_no_authorization_header_without_token(tmp_path: Path) -> None:
    widget, sockets = _widget(tmp_path)
    await widget._showEvent(MagicMock())
    assert _request(sockets[-1]) == b"GET /webcam/video.mjpg?stretch=linear HTTP/1.0\r\nHost: localhost:37077\r\n\r\n"
    widget.close()


def test_mjpeg_query(tmp_path: Path) -> None:
    widget, _ = _widget(tmp_path)
    widget.comboStretch.setCurrentIndex(widget.comboStretch.findData("asinh"))
    widget.comboCuts.setCurrentIndex(widget.comboCuts.findData("percentile"))
    widget.spinLo.setValue(1.0)
    widget.spinHi.setValue(99.0)
    widget.spinQuality.setValue(60)
    widget._factor = 3
    assert widget._query() == {
        "stretch": "asinh",
        "cuts": "percentile",
        "lo": "1.0",
        "hi": "99.0",
        "scale": "3",
        "quality": "60",
    }
    widget.close()


def test_raw_query(tmp_path: Path) -> None:
    widget, _ = _widget(tmp_path, mode=RAW)
    widget.spinMaxRate.setValue(2.0)
    widget._factor = 2
    assert widget._query() == {"bin": "2", "max_rate": "2.0"}
    widget.spinMaxRate.setValue(0.0)
    widget._factor = 1
    assert widget._query() == {}
    widget.close()


def test_percentile_resets_invalid_lo_hi(tmp_path: Path) -> None:
    widget, _ = _widget(tmp_path)
    widget.comboCuts.setCurrentIndex(widget.comboCuts.findData("manual"))
    widget.spinLo.setValue(1000.0)
    widget.spinHi.setValue(5000.0)
    widget.comboCuts.setCurrentIndex(widget.comboCuts.findData("percentile"))
    assert (widget.spinLo.value(), widget.spinHi.value()) == (0.5, 99.5)
    widget.close()


# ── mode switching and fit ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_mode_switch_reconnects_to_raw(tmp_path: Path) -> None:
    widget, sockets = _widget(tmp_path)
    await widget._showEvent(MagicMock())
    widget.comboMode.setCurrentIndex(widget.comboMode.findData(RAW))
    assert len(sockets) == 2
    sockets[0].abort.assert_called_once()
    assert _request(sockets[1]).startswith(b"GET /webcam/video.raw?max_rate=5.0 HTTP/1.0\r\n")
    widget.close()


@pytest.mark.asyncio
async def test_first_frame_sets_fit_factor_and_reconnects(tmp_path: Path) -> None:
    widget, sockets = _widget(tmp_path, mode=RAW)
    widget.widgetLiveView.resize(400, 300)
    widget._render = MagicMock()  # type: ignore[method-assign]
    await widget._showEvent(MagicMock())
    widget._show_raw(RawFrame({"SWBIN": 1}, np.zeros((1200, 1600), dtype=np.uint16)))
    assert widget._factor == 4
    assert len(sockets) == 2
    assert b"bin=4" in _request(sockets[1])

    # binned frames of the same camera don't change anything
    widget._show_raw(RawFrame({"SWBIN": 4}, np.zeros((300, 400), dtype=np.uint16)))
    assert len(sockets) == 2
    widget.close()


# ── raw rendering ──────────────────────────────────────────────────────────


def test_render_raw_flips_and_is_grayscale() -> None:
    data = np.array([[0, 0], [100, 100]], dtype=np.uint16)
    image = render_raw(data, VideoWidget()._stretch_params())
    assert image.format() == QtGui.QImage.Format.Format_Grayscale8
    assert (image.width(), image.height()) == (2, 2)
    # FITS row 0 is at the bottom
    assert QtGui.qGray(image.pixel(0, 0)) == 255
    assert QtGui.qGray(image.pixel(0, 1)) == 0


def test_render_raw_colour() -> None:
    data = np.zeros((2, 3, 3), dtype=np.uint8)
    image = render_raw(data, VideoWidget()._stretch_params())
    assert image.format() == QtGui.QImage.Format.Format_RGB888
    assert (image.width(), image.height()) == (3, 2)


@pytest.mark.asyncio
async def test_raw_stretch_change_rerenders_without_reconnect(tmp_path: Path) -> None:
    widget, sockets = _widget(tmp_path, mode=RAW)
    await widget._showEvent(MagicMock())
    widget._full_size = (2, 2)
    widget._factor = widget._fit_factor()
    with patch.object(widget.widgetLiveView, "setPixmap") as set_pixmap:
        widget._show_raw(RawFrame({}, np.arange(4, dtype=np.uint16).reshape(2, 2)))
        while widget._render_busy:
            await asyncio.sleep(0.01)
        assert set_pixmap.call_count == 1

        widget.comboStretch.setCurrentIndex(widget.comboStretch.findData("sqrt"))
        while widget._render_busy:
            await asyncio.sleep(0.01)
        assert set_pixmap.call_count == 2
    assert len(sockets) == 1
    assert not widget._reconnect_timer.isActive()
    widget.close()


# ── settings ───────────────────────────────────────────────────────────────


def test_settings_round_trip_per_camera(tmp_path: Path) -> None:
    widget, _ = _widget(tmp_path)
    widget.comboMode.setCurrentIndex(widget.comboMode.findData(RAW))
    widget.comboStretch.setCurrentIndex(widget.comboStretch.findData("log"))
    widget.spinMaxRate.setValue(12.0)

    other, _ = _widget(tmp_path)
    other._settings_loaded = False
    other._load_settings()
    assert other._mode == RAW
    assert other.comboStretch.currentData() == "log"
    assert other.spinMaxRate.value() == 12.0

    # another camera starts with the defaults
    third, _ = _widget(tmp_path)
    third.modules = ["other"]
    third._load_settings()
    assert third._mode == MJPEG
    assert third.comboStretch.currentData() == "linear"
    for w in (widget, other, third):
        w.close()


def test_render_raw_full_cuts_follow_source_dtype() -> None:
    # a binned frame is float32; "full" cuts need the dtype it had before binning
    data = np.full((4, 4), 32768.0, dtype=np.float32)
    widget = VideoWidget()
    widget.comboCuts.setCurrentIndex(widget.comboCuts.findData("full"))

    image = render_raw(data, widget._stretch_params(), "<u2")

    assert image.pixelColor(0, 0).red() == 128
