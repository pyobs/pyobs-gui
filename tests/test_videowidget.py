from unittest.mock import MagicMock

import pytest

from pyobs_gui.videowidget import VideoWidget


def _widget_with_stream_socket() -> tuple[VideoWidget, MagicMock]:
    """VideoWidget with a mocked raw stream socket, skipping _init."""
    widget = VideoWidget()
    widget._initialized = True
    widget.host = "localhost"
    widget.port = 37077
    widget.path = "/webcam/video.mjpg"
    widget.scheme = "http"
    socket = MagicMock()
    widget.socket = socket
    return widget, socket


# ── raw-socket stream auth ─────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_show_event_sends_authorization_header_when_token_configured(qapp) -> None:
    """With an HttpFile carrying a token, the raw-socket GET must include Authorization."""
    widget, socket = _widget_with_stream_socket()
    widget._auth_header = "Bearer secret"

    await widget._showEvent(MagicMock())

    written = socket.write.call_args[0][0]
    assert written.startswith(b"GET /webcam/video.mjpg HTTP/1.0\r\nHost: localhost:37077\r\n")
    assert b"Authorization: Bearer secret\r\n" in written
    assert written.endswith(b"\r\n")
    widget.close()


@pytest.mark.asyncio
async def test_show_event_sends_no_authorization_header_without_token(qapp) -> None:
    """Without a token, the bytes written to the socket are unchanged from today."""
    widget, socket = _widget_with_stream_socket()
    widget._auth_header = None

    await widget._showEvent(MagicMock())

    written = socket.write.call_args[0][0]
    assert written == b"GET /webcam/video.mjpg HTTP/1.0\r\nHost: localhost:37077\r\n\r\n"
    widget.close()
