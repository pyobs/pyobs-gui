from unittest.mock import AsyncMock, MagicMock

import pytest

from pyobs.interfaces import IMotion
from pyobs.utils.enums import MotionStatus

from pyobs_gui.modewidget import ModeWidget


def _widget_with_group(qapp, group: str = "") -> tuple[ModeWidget, MagicMock]:
    widget = ModeWidget()
    widget._mode_groups = [group]
    widget._mode_options = {group: ["Primary", "Gregory"]}
    widget._modes = {}
    widget._motion_status = MotionStatus.UNKNOWN
    widget._has_motion = False
    button = MagicMock()
    widget._mode_widgets = {group: (MagicMock(), button)}
    return widget, button


def test_edit_button_enabled_without_imotion_even_while_status_is_unknown(qapp) -> None:
    """Regression: a plain IMode module with no IMotion (e.g. a camera's fiber-hole selector)
    left the IMotion state subscription in _init() permanently unfired, so _motion_status never
    left UNKNOWN and the edit button could never be enabled."""
    widget, button = _widget_with_group(qapp)
    widget._has_motion = False
    widget._motion_status = MotionStatus.UNKNOWN

    widget.update_gui()

    button.setEnabled.assert_called_once_with(True)


def test_edit_button_disabled_with_imotion_while_status_is_unknown(qapp) -> None:
    widget, button = _widget_with_group(qapp)
    widget._has_motion = True
    widget._motion_status = MotionStatus.UNKNOWN

    widget.update_gui()

    button.setEnabled.assert_called_once_with(False)


def test_edit_button_enabled_with_imotion_once_idle(qapp) -> None:
    widget, button = _widget_with_group(qapp)
    widget._has_motion = True
    widget._motion_status = MotionStatus.IDLE

    widget.update_gui()

    button.setEnabled.assert_called_once_with(True)


@pytest.mark.asyncio
async def test_init_only_subscribes_to_imotion_when_implemented(qapp) -> None:
    widget = ModeWidget()
    widget.modules = ["fibercamera"]
    widget._fetch_permitted_methods = AsyncMock()

    comm = MagicMock()
    comm.has_proxy = AsyncMock(return_value=False)
    comm.subscribe_state = AsyncMock()
    comm.get_capabilities = AsyncMock(return_value=None)
    widget._comm = comm

    await widget._init()

    comm.has_proxy.assert_awaited_once_with("fibercamera", IMotion)
    assert comm.subscribe_state.await_args_list == []
    assert widget._has_motion is False
