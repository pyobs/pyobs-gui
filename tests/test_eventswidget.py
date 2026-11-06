from unittest.mock import AsyncMock, MagicMock

import pytest

import pyobs.events
from pyobs.events import Event

from pyobs_gui.eventswidget import EventsWidget


class _NotAnEvent:
    """Stands in for helpers like EventFactory that newer pyobs-core exports from pyobs.events."""


@pytest.mark.asyncio
async def test_open_skips_non_event_classes(qapp, monkeypatch) -> None:
    """Regression: EventFactory (no `local` attribute) is exported by pyobs.events in newer
    pyobs-core, register_event crashed on it and the whole Events page disappeared."""
    monkeypatch.setattr(pyobs.events, "NotAnEvent", _NotAnEvent, raising=False)
    comm = MagicMock()
    comm.register_event = AsyncMock()

    widget = EventsWidget()
    await widget.open(modules=[], comm=comm, observer=MagicMock(), vfs=MagicMock())

    registered = [call.args[0] for call in comm.register_event.call_args_list]
    assert registered
    assert _NotAnEvent not in registered
    assert all(issubclass(cls, Event) for cls in registered)
