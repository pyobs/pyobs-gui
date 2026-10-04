from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest
from astroplan import Observer
from pyobs.comm import Comm
from pyobs.events import NewImageEvent
from pyobs.vfs import VirtualFileSystem

from pyobs_gui.base import BaseWidget


class ChildWidget(BaseWidget):
    async def open(
        self,
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)
        await self.register_event(NewImageEvent, self._on_new_image)

    async def _on_new_image(self, event: Any, sender: str) -> bool:
        return True


class ParentWidget(BaseWidget):
    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        # like CameraWidget.datadisplay: an embedded child, not a sidebar widget
        self.child = ChildWidget()

    async def open(
        self,
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)
        await self._open_child(self.child)


@pytest.mark.asyncio
async def test_discard_unregisters_handlers_of_embedded_children() -> None:
    comm = MagicMock()
    comm.register_event = AsyncMock()
    comm.unregister_event = AsyncMock()
    widget = ParentWidget()
    await widget.open(modules=["camera"], comm=comm)

    await widget.discard()

    comm.unregister_event.assert_awaited_once_with(NewImageEvent, widget.child._on_new_image)

    # discarding again doesn't unregister twice
    await widget.discard()
    assert comm.unregister_event.await_count == 1
