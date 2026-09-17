from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from pyobs.interfaces import IAbortable, IDataSequence
from pyobs_gui.spectrographwidget import SpectrographWidget


class _AsyncProxyCM:
    """Mimics Comm.safe_proxy()'s async context manager, yielding a fixed proxy (or None)."""

    def __init__(self, value):
        self._value = value

    async def __aenter__(self):
        return self._value

    async def __aexit__(self, *exc_info):
        return False


class FakeComm:
    """Only implements what SpectrographWidget._grab_spectra()/_do_abort() touch; an interface
    with no proxy given resolves to "not supported" (proxy is None)."""

    def __init__(self, data_sequence_proxy=None, abortable_proxy=None):
        self._data_sequence_proxy = data_sequence_proxy
        self._abortable_proxy = abortable_proxy

    def safe_proxy(self, module, interface):
        if interface is IDataSequence:
            value = self._data_sequence_proxy
        elif interface is IAbortable:
            value = self._abortable_proxy
        else:
            value = None
        return _AsyncProxyCM(value)


def make_widget(data_sequence_proxy=None, abortable_proxy=None) -> SpectrographWidget:
    widget = SpectrographWidget()
    widget.modules = ["spectrograph"]
    widget._comm = FakeComm(  # pyrefly: ignore [bad-assignment]
        data_sequence_proxy=data_sequence_proxy, abortable_proxy=abortable_proxy
    )
    widget.datadisplay.grab_data = AsyncMock()
    return widget


@pytest.mark.asyncio
async def test_grab_spectra_uses_server_side_sequence_when_broadcasting(qapp) -> None:
    proxy = SimpleNamespace(grab_sequence=AsyncMock())
    widget = make_widget(proxy)
    widget.checkBroadcast.setChecked(True)
    widget.spinCount.setValue(3)

    await widget._grab_spectra()

    proxy.grab_sequence.assert_awaited_once_with(3, True)
    widget.datadisplay.grab_data.assert_not_called()
    widget.close()


@pytest.mark.asyncio
async def test_grab_spectra_falls_back_to_client_side_loop_when_not_broadcasting(qapp) -> None:
    """Without broadcasting, grab_sequence() has no way to hand a filename back to the caller,
    so the GUI would have no way to learn a spectrum is ready and nothing would ever be
    displayed -- same reasoning as CameraWidget's equivalent regression test (issue #122)."""
    proxy = SimpleNamespace(grab_sequence=AsyncMock())
    widget = make_widget(proxy)
    widget.checkBroadcast.setChecked(False)
    widget.spinCount.setValue(2)

    await widget._grab_spectra()

    proxy.grab_sequence.assert_not_called()
    assert widget.datadisplay.grab_data.await_count == 2
    widget.datadisplay.grab_data.assert_awaited_with(False)
    widget.close()


@pytest.mark.asyncio
async def test_grab_spectra_falls_back_when_module_has_no_data_sequence_support(qapp) -> None:
    widget = make_widget(data_sequence_proxy=None)
    widget.checkBroadcast.setChecked(True)
    widget.spinCount.setValue(1)

    await widget._grab_spectra()

    assert widget.datadisplay.grab_data.await_count == 1
    widget.datadisplay.grab_data.assert_awaited_with(True)
    widget.close()


@pytest.mark.asyncio
async def test_abort_soft_stops_server_side_sequence_when_more_than_one_left(qapp) -> None:
    proxy = SimpleNamespace(abort_sequence=AsyncMock())
    widget = make_widget(proxy)
    widget.exposures_left = 2

    await widget._do_abort()

    proxy.abort_sequence.assert_awaited_once()
    widget.close()


@pytest.mark.asyncio
async def test_abort_hard_aborts_when_one_left(qapp) -> None:
    proxy = SimpleNamespace(abort=AsyncMock())
    widget = make_widget(abortable_proxy=proxy)
    widget.exposures_left = 1

    await widget._do_abort()

    proxy.abort.assert_awaited_once()
    widget.close()
