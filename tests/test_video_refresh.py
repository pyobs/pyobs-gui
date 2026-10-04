"""VideoWidget re-resolves its stream URLs when the settings (VFS roots) change."""

import asyncio
from collections.abc import AsyncIterator
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from pyobs.vfs import VirtualFileSystem

from pyobs_gui.guisignals import gui_signals
from pyobs_gui.videowidget import MJPEG, VideoWidget


def _root(port: int) -> dict[str, Any]:
    return {"class": "pyobs.vfs.HttpFile", "download": f"http://localhost:{port}/"}


def _set_webcam_root(vfs: VirtualFileSystem, port: int | None) -> None:
    vfs.set_roots({} if port is None else {"webcam": _root(port)})


async def _settle() -> None:
    """Wait for the task started by the signal, which resolves the VFS path in an executor."""
    current = asyncio.current_task()
    pending = [t for t in asyncio.all_tasks() if t is not current and not t.done()]
    if pending:
        await asyncio.wait_for(asyncio.gather(*pending, return_exceptions=True), timeout=5)


@pytest_asyncio.fixture
async def setup() -> AsyncIterator[tuple[VideoWidget, VirtualFileSystem, MagicMock, MagicMock]]:
    widget = VideoWidget()
    widget.modules = ["cam"]
    widget.vfs = VirtualFileSystem()
    comm = MagicMock()
    comm.get_interfaces = AsyncMock(return_value=[])
    comm.get_capabilities = AsyncMock(return_value=MagicMock(mjpeg="/webcam/video.mjpg", raw=None))
    comm.unregister_event = AsyncMock()
    warning = AsyncMock()
    with (
        patch.object(type(widget), "comm", new=comm),
        patch("pyobs_gui.videowidget.QAsyncMessageBox.warning", new=warning),
    ):
        yield widget, widget.vfs, comm, warning  # type: ignore[misc]
        await widget.discard()
    widget.close()


async def _init(widget: VideoWidget) -> None:
    await widget._init()
    widget._initialized = True


@pytest.mark.asyncio
async def test_failed_init_is_completed_when_settings_change(setup: Any) -> None:
    widget, vfs, _, warning = setup
    await _init(widget)
    assert not widget._started and not widget.isEnabled()
    warning.assert_awaited_once()

    _set_webcam_root(vfs, 37077)
    gui_signals.settings_changed.emit()
    await _settle()

    assert widget._started and widget.isEnabled()
    assert widget._urls[MJPEG].port == 37077


@pytest.mark.asyncio
async def test_new_urls_are_used_at_next_connect_without_reconnecting(setup: Any) -> None:
    widget, vfs, _, _ = setup
    _set_webcam_root(vfs, 37077)
    await _init(widget)
    assert widget._urls[MJPEG].port == 37077

    widget._connect = MagicMock()  # type: ignore[method-assign]
    _set_webcam_root(vfs, 40000)
    gui_signals.settings_changed.emit()
    await _settle()

    assert widget._urls[MJPEG].port == 40000
    widget._connect.assert_not_called()


@pytest.mark.asyncio
async def test_old_urls_are_kept_when_nothing_resolves_any_more(setup: Any) -> None:
    widget, vfs, _, warning = setup
    _set_webcam_root(vfs, 37077)
    await _init(widget)

    _set_webcam_root(vfs, None)
    gui_signals.settings_changed.emit()
    await _settle()

    assert widget._urls[MJPEG].port == 37077
    assert widget.isEnabled()
    warning.assert_awaited_once()
    assert "'webcam'" in str(warning.await_args)


@pytest.mark.asyncio
async def test_change_before_init_finished_is_ignored(setup: Any) -> None:
    widget, vfs, comm, _ = setup
    await widget._init()  # connects the signal, but _initialized is not set yet
    comm.get_capabilities.reset_mock()

    _set_webcam_root(vfs, 37077)
    gui_signals.settings_changed.emit()
    await _settle()

    comm.get_capabilities.assert_not_awaited()


@pytest.mark.asyncio
async def test_discarded_widget_no_longer_reacts(setup: Any) -> None:
    widget, vfs, comm, _ = setup
    await _init(widget)
    await widget.discard()
    comm.get_capabilities.reset_mock()

    _set_webcam_root(vfs, 37077)
    gui_signals.settings_changed.emit()
    await _settle()

    comm.get_capabilities.assert_not_awaited()
