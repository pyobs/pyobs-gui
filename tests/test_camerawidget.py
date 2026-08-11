from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from pyobs.interfaces import IDataSequence
from pyobs_gui.camerawidget import CameraWidget


class _AsyncProxyCM:
    """Mimics Comm.safe_proxy()'s async context manager, yielding a fixed proxy (or None)."""

    def __init__(self, value):
        self._value = value

    async def __aenter__(self):
        return self._value

    async def __aexit__(self, *exc_info):
        return False


class FakeComm:
    """Only implements what CameraWidget.expose() touches; every optional interface except
    IDataSequence resolves to "not supported" (proxy is None)."""

    def __init__(self, data_sequence_proxy=None):
        self._data_sequence_proxy = data_sequence_proxy

    def safe_proxy(self, module, interface):
        value = self._data_sequence_proxy if interface is IDataSequence else None
        return _AsyncProxyCM(value)


def make_widget(data_sequence_proxy) -> CameraWidget:
    widget = CameraWidget()
    widget.modules = ["camera"]
    widget._comm = FakeComm(data_sequence_proxy=data_sequence_proxy)  # pyrefly: ignore [bad-assignment]
    widget.datadisplay.grab_data = AsyncMock()
    return widget


@pytest.mark.asyncio
async def test_expose_uses_server_side_sequence_when_broadcasting(qapp) -> None:
    proxy = SimpleNamespace(grab_sequence=AsyncMock())
    widget = make_widget(proxy)
    widget.checkBroadcast.setChecked(True)
    widget.spinCount.setValue(3)

    await widget.expose()

    proxy.grab_sequence.assert_awaited_once_with(3, True)
    widget.datadisplay.grab_data.assert_not_called()
    widget.close()


@pytest.mark.asyncio
async def test_expose_falls_back_to_client_side_loop_when_not_broadcasting(qapp) -> None:
    """Regression test: grab_sequence() has no way to hand a filename back to the caller, so
    without broadcasting, taking the server-side sequence path would leave the GUI with no way
    to learn an image is ready and nothing would ever be displayed (issue #122)."""
    proxy = SimpleNamespace(grab_sequence=AsyncMock())
    widget = make_widget(proxy)
    widget.checkBroadcast.setChecked(False)
    widget.spinCount.setValue(2)

    await widget.expose()

    proxy.grab_sequence.assert_not_called()
    assert widget.datadisplay.grab_data.await_count == 2
    widget.datadisplay.grab_data.assert_awaited_with(False)
    widget.close()


@pytest.mark.asyncio
async def test_expose_falls_back_when_module_has_no_data_sequence_support(qapp) -> None:
    widget = make_widget(data_sequence_proxy=None)
    widget.checkBroadcast.setChecked(True)
    widget.spinCount.setValue(1)

    await widget.expose()

    assert widget.datadisplay.grab_data.await_count == 1
    widget.datadisplay.grab_data.assert_awaited_with(True)
    widget.close()
