from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from pyobs.events import NewImageEvent
from pyobs.vfs import VirtualFileSystem

from pyobs_gui.base import missing_root_message
from pyobs_gui.datadisplaywidget import DataDisplayWidget
from pyobs_gui.videowidget import VideoWidget


def _missing_root_error() -> ValueError:
    try:
        VirtualFileSystem().open_file("/cache/img.fits", "rb")
    except ValueError as e:
        return e
    raise AssertionError("expected ValueError")


def test_missing_root_message_names_root_path_and_module() -> None:
    message = missing_root_message(_missing_root_error(), "/cache/img.fits", "cam")
    assert message is not None
    assert "'cache'" in message and "'/cache/img.fits'" in message and "'cam'" in message


def test_missing_root_message_ignores_other_errors() -> None:
    assert missing_root_message(ValueError("something else"), "/cache/img.fits", "cam") is None
    assert missing_root_message(OSError("Could not find root"), "/cache/img.fits", "cam") is None


def _datadisplay() -> DataDisplayWidget:
    widget = DataDisplayWidget(None)
    widget.modules = ["cam"]
    widget.vfs = VirtualFileSystem()
    return widget


@pytest.mark.asyncio
async def test_datadisplay_reports_missing_root_once_per_root() -> None:
    widget = _datadisplay()
    with patch("pyobs_gui.datadisplaywidget.QAsyncMessageBox.warning", new=AsyncMock()) as warning:
        assert await widget._on_new_data(NewImageEvent("/cache/a.fits", None), "cam") is False
        assert await widget._on_new_data(NewImageEvent("/cache/b.fits", None), "cam") is False
        assert warning.await_count == 1
        assert "'cache'" in str(warning.await_args)

        # a different root is a new problem
        await widget._on_new_data(NewImageEvent("/other/c.fits", None), "cam")
        assert warning.await_count == 2
    widget.close()


@pytest.mark.asyncio
async def test_datadisplay_does_not_swallow_other_value_errors() -> None:
    widget = _datadisplay()
    widget.vfs.read_fits = AsyncMock(side_effect=ValueError("No valid path with a root."))  # type: ignore[method-assign]
    with patch("pyobs_gui.datadisplaywidget.QAsyncMessageBox.warning", new=AsyncMock()) as warning:
        with pytest.raises(ValueError, match="No valid path"):
            await widget._on_new_data(NewImageEvent("nofile.fits", None), "cam")
        warning.assert_not_awaited()
    widget.close()


@pytest.mark.asyncio
async def test_video_resolve_url_records_missing_root() -> None:
    widget = VideoWidget()
    widget.modules = ["cam"]
    widget.vfs = VirtualFileSystem()
    assert await widget._resolve_url("/webcam/video.mjpg") is None
    assert widget._missing_root_message is not None
    assert "'webcam'" in widget._missing_root_message
    widget.close()


@pytest.mark.asyncio
async def test_video_init_shows_message_when_no_stream_resolves() -> None:
    widget = VideoWidget()
    widget.modules = ["cam"]
    widget.vfs = VirtualFileSystem()
    comm = MagicMock()
    comm.get_interfaces = AsyncMock(return_value=[])
    comm.get_capabilities = AsyncMock(return_value=MagicMock(mjpeg="/webcam/video.mjpg", raw="/webcam/video.raw"))
    widget._comm = comm  # type: ignore[attr-defined]
    with (
        patch.object(type(widget), "comm", new=comm),
        patch("pyobs_gui.videowidget.QAsyncMessageBox.warning", new=AsyncMock()) as warning,
    ):
        await widget._init()
    warning.assert_awaited_once()
    assert "'webcam'" in str(warning.await_args)
    assert not widget.isEnabled()
    widget.close()
