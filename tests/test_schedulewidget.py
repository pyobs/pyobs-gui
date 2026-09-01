from unittest.mock import AsyncMock

import astropy.units as u
import pytest

from pyobs.interfaces import IRoboticScheduler, IRunnable, RoboticTask, SchedulerState
from pyobs.utils.time import Time
from pyobs_gui.schedulewidget import ScheduleWidget


class _AsyncProxyCM:
    def __init__(self, value):
        self._value = value

    async def __aenter__(self):
        return self._value

    async def __aexit__(self, *exc_info):
        return False


class FakeComm:
    def __init__(self, scheduler_proxy=None, runnable_proxy=None):
        self._scheduler_proxy = scheduler_proxy
        self._runnable_proxy = runnable_proxy

    def proxy(self, module, interface):
        if interface is IRoboticScheduler:
            return _AsyncProxyCM(self._scheduler_proxy)
        if interface is IRunnable:
            return _AsyncProxyCM(self._runnable_proxy)
        raise AssertionError(f"unexpected interface {interface}")


def make_widget(scheduler_proxy=None, runnable_proxy=None) -> ScheduleWidget:
    widget = ScheduleWidget()
    widget.modules = ["scheduler"]
    widget._comm = FakeComm(scheduler_proxy, runnable_proxy)  # pyrefly: ignore [bad-assignment]
    return widget


@pytest.mark.asyncio
async def test_refresh_schedule_populates_table() -> None:
    tasks = [
        RoboticTask(
            id=1, name="Photometry M31", target="M31", start=Time.now(), end=Time.now() + 60 * u.s, priority=1.0
        ),
        RoboticTask(id=2, name="Spectroscopy Vega", target="Vega", state="pending"),
    ]
    proxy = AsyncMock()
    proxy.get_schedule.return_value = tasks
    widget = make_widget(scheduler_proxy=proxy)

    await widget._refresh_schedule()

    proxy.get_schedule.assert_awaited_once_with(limit=20)
    assert widget.tableSchedule.rowCount() == 2
    assert widget.tableSchedule.item(0, 2).text() == "Photometry M31"
    assert widget.tableSchedule.item(0, 3).text() == "M31"
    assert widget.tableSchedule.item(1, 4).text() == "pending"
    widget.close()


@pytest.mark.asyncio
async def test_refresh_schedule_survives_proxy_failure() -> None:
    proxy = AsyncMock()
    proxy.get_schedule.side_effect = RuntimeError("boom")
    widget = make_widget(scheduler_proxy=proxy)

    await widget._refresh_schedule()  # must not raise

    assert widget.tableSchedule.rowCount() == 0
    widget.close()


@pytest.mark.asyncio
async def test_reschedule_calls_run_and_refreshes(monkeypatch) -> None:
    runnable_proxy = AsyncMock()
    scheduler_proxy = AsyncMock()
    scheduler_proxy.get_schedule.return_value = []
    widget = make_widget(scheduler_proxy=scheduler_proxy, runnable_proxy=runnable_proxy)

    await widget._run_reschedule()

    runnable_proxy.run.assert_awaited_once()
    scheduler_proxy.get_schedule.assert_awaited_once()
    widget.close()


def test_on_scheduler_state_updates_cache() -> None:
    widget = make_widget()
    t = Time.now()
    widget._on_scheduler_state(SchedulerState(last_reschedule=t))
    assert widget._last_reschedule is t
    widget.close()


def test_update_gui_status_line() -> None:
    widget = make_widget()
    widget.update_gui()
    assert "never" in widget.labelStatus.text()
    assert "Stopped" in widget.labelStatus.text()

    widget._running = True
    widget._last_reschedule = Time("2026-08-31T12:00:00")
    widget.update_gui()
    assert "Running" in widget.labelStatus.text()
    assert "2026-08-31 12:00:00" in widget.labelStatus.text()
    widget.close()


def test_registered_in_mainwindow_default_widgets() -> None:
    from pyobs_gui import mainwindow

    entry = next(e for e in mainwindow.MAIN_WIDGETS if e.interface is IRoboticScheduler)
    assert entry.widget is ScheduleWidget
    assert entry.icon


def test_reschedule_button_gated_by_permissions() -> None:
    widget = make_widget()
    widget._permitted_methods = set()  # nothing permitted
    widget.update_gui()
    assert widget.buttonReschedule.isEnabled() is False

    widget._permitted_methods = {"run"}
    widget.update_gui()
    assert widget.buttonReschedule.isEnabled() is True
    widget.close()
