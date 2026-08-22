from unittest.mock import AsyncMock, MagicMock

import pytest

from pyobs.utils import exceptions as exc
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


@pytest.mark.asyncio
async def test_grab_image_awaits_expose_task_and_surfaces_failure(qapp) -> None:
    """grab_image() must run the expose sequence as an awaited task so failures surface (issue
    #134: it used to be fire-and-forget via asyncio.create_task, so an exception during the
    sequence was discarded at GC and the operator got no feedback)."""
    widget = VideoWidget()
    widget.modules = ["cam"]
    # empty _interfaces -> no IImageFormat/IImageType proxy calls, straight into the grab loop
    widget.datadisplay.grab_data = AsyncMock(side_effect=exc.GrabImageError("exposure failed"))
    widget.spinCount.setValue(2)

    with pytest.raises(exc.GrabImageError):
        await widget._grab_image()

    # the grab failed before the decrement, so the loop state is untouched
    assert widget.exposures_left == 2
    widget.close()


@pytest.mark.asyncio
async def test_grab_image_sets_exposure_count_before_grabbing(qapp) -> None:
    widget = VideoWidget()
    widget.modules = ["cam"]
    widget.datadisplay.grab_data = AsyncMock(return_value="img.fits")
    widget.spinCount.setValue(3)

    await widget._grab_image()

    assert widget.datadisplay.grab_data.await_count == 3
    widget.close()


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
