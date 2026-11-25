from types import SimpleNamespace
from unittest.mock import MagicMock

from pyobs.interfaces import CoolingState
from pyobs_gui.coolingwidget import CoolingWidget


def render(state: CoolingState) -> SimpleNamespace:
    """Run CoolingWidget.update_gui() against a stub, so that no Qt widget has to be created."""
    stub = SimpleNamespace(
        state=state,
        labelStatus=MagicMock(),
        labelPower=MagicMock(),
        setEnabled=MagicMock(),
        _status_text=CoolingWidget._status_text,
    )
    CoolingWidget.update_gui(stub)  # type: ignore[arg-type]
    return stub


def status(stub: SimpleNamespace) -> str:
    return stub.labelStatus.setText.call_args.args[0]  # type: ignore[no-any-return]


def test_idle() -> None:
    stub = render(CoolingState(enabled=True, setpoint=-10.0, power=40))
    assert status(stub) == "-10.0°C"
    stub.labelPower.setText.assert_called_once_with("40%")


def test_ramping_down() -> None:
    stub = render(CoolingState(enabled=True, setpoint=12.0, power=80, target=-10.0, ramping=True))
    assert status(stub) == "12.0°C → -10.0°C"


def test_warming_while_off() -> None:
    stub = render(CoolingState(enabled=False, setpoint=8.0, power=None, target=20.0, ramping=True))
    assert status(stub) == "warming 8.0°C → 20.0°C"
    stub.labelPower.clear.assert_called_once()


def test_off() -> None:
    stub = render(CoolingState(enabled=False, setpoint=None, power=None))
    assert status(stub) == "OFF"


def test_old_module_without_new_fields() -> None:
    # a module on older pyobs-core sends no target/ramping, which deserialize to their defaults
    stub = render(CoolingState(enabled=True, setpoint=-5.0, power=10))
    assert status(stub) == "-5.0°C"
