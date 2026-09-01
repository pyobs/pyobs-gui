from unittest.mock import AsyncMock

import astropy.units as u
import pytest

from pyobs.interfaces import IRobotic, RoboticState, RoboticTask
from pyobs.interfaces.IRunning import RunningState
from pyobs.utils.time import Time
from pyobs_gui.roboticwidget import RoboticWidget, _format_countdown, _format_time


class _AsyncProxyCM:
    def __init__(self, value):
        self._value = value

    async def __aenter__(self):
        return self._value

    async def __aexit__(self, *exc_info):
        return False


class FakeComm:
    def __init__(self, proxy):
        self._proxy = proxy

    def proxy(self, module, interface):
        assert interface is IRobotic
        return _AsyncProxyCM(self._proxy)


def make_widget(proxy=None) -> RoboticWidget:
    widget = RoboticWidget()
    widget.modules = ["mastermind"]
    widget._comm = FakeComm(proxy)  # pyrefly: ignore [bad-assignment]
    return widget


def test_format_time_and_countdown() -> None:
    assert _format_time(None) == ""
    t = Time("2026-08-31T12:00:00")
    assert _format_time(t) == "2026-08-31 12:00:00"

    assert _format_countdown(None) == ""
    assert _format_countdown(Time.now() - 10 * u.s) == "overdue"
    # allow +/-1s slack around the two Time.now() calls inside _format_countdown vs. here
    assert _format_countdown(Time.now() + 3725 * u.s) in ("1:02:04", "1:02:05")


def test_update_gui_renders_empty_state() -> None:
    widget = make_widget()
    widget.update_gui()

    assert widget.labelStatus.text() == "Stopped"
    assert widget.textCurrentName.text() == ""
    assert widget.textNextName.text() == ""
    assert widget.textCantRunReason.text() == ""
    widget.close()


def test_update_gui_renders_current_and_next_task() -> None:
    widget = make_widget()
    widget._running = True
    widget._state = RoboticState(
        current=RoboticTask(id=1, name="Photometry M31", target="M31", obsnum="20260831-001"),
        next=RoboticTask(id=2, name="Spectroscopy Vega", target="Vega"),
        cant_run_reason="waiting for weather",
    )
    widget.update_gui()

    assert widget.labelStatus.text() == "Running"
    assert widget.textCurrentName.text() == "Photometry M31"
    assert widget.textCurrentTarget.text() == "M31"
    assert widget.textCurrentObsnum.text() == "20260831-001"
    assert widget.textNextName.text() == "Spectroscopy Vega"
    assert widget.textCantRunReason.text() == "waiting for weather"
    widget.close()


def test_on_robotic_state_updates_cache() -> None:
    widget = make_widget()
    state = RoboticState(current=RoboticTask(id=1, name="task"))
    widget._on_robotic_state(state)
    assert widget._state is state
    widget.close()


def test_on_running_state_updates_cache() -> None:
    widget = make_widget()
    widget._on_running_state(RunningState(running=True))
    assert widget._running is True
    widget.close()


@pytest.mark.asyncio
async def test_start_calls_proxy_start() -> None:
    proxy = AsyncMock()
    widget = make_widget(proxy)
    await widget._start_robotic()
    proxy.start.assert_awaited_once()
    widget.close()


@pytest.mark.asyncio
async def test_stop_calls_proxy_stop() -> None:
    proxy = AsyncMock()
    widget = make_widget(proxy)
    await widget._stop_robotic()
    proxy.stop.assert_awaited_once()
    widget.close()


def test_registered_in_mainwindow_default_widgets() -> None:
    from pyobs_gui import mainwindow

    entry = next(e for e in mainwindow.MAIN_WIDGETS if e.interface is IRobotic)
    assert entry.widget is RoboticWidget
    assert entry.icon


def test_buttons_gated_by_running_state_and_permissions() -> None:
    widget = make_widget()
    widget._running = False
    widget._permitted_methods = {"stop"}  # start not permitted
    widget.update_gui()
    assert widget.buttonStart.isEnabled() is False
    assert widget.buttonStop.isEnabled() is False  # not running either

    widget._running = True
    widget.update_gui()
    assert widget.buttonStart.isEnabled() is False  # running
    assert widget.buttonStop.isEnabled() is True  # running and permitted
    widget.close()
