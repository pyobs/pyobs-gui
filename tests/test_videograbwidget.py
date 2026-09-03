from unittest.mock import AsyncMock

import pytest

from pyobs.utils import exceptions as exc
from pyobs_gui.videograbwidget import VideoGrabWidget


@pytest.mark.asyncio
async def test_grab_image_awaits_expose_task_and_surfaces_failure(qapp) -> None:
    """grab_image() must run the expose sequence as an awaited task so failures surface (issue
    #134: it used to be fire-and-forget via asyncio.create_task, so an exception during the
    sequence was discarded at GC and the operator got no feedback)."""
    widget = VideoGrabWidget()
    widget.modules = ["cam"]
    # empty _interfaces -> no IImageFormat/IImageType proxy calls, straight into the grab loop
    widget.datadisplay.grab_data = AsyncMock(side_effect=exc.GrabImageError("exposure failed"))
    widget.spinCount.setValue(2)

    with pytest.raises(exc.GrabImageError):
        await widget._grab_image()

    # the grab failed before the decrement, so the loop state is untouched
    assert widget.exposures_left == 2
    widget.close()


@pytest.mark.asyncio
async def test_grab_image_sets_exposure_count_before_grabbing(qapp) -> None:
    widget = VideoGrabWidget()
    widget.modules = ["cam"]
    widget.datadisplay.grab_data = AsyncMock(return_value="img.fits")
    widget.spinCount.setValue(3)

    await widget._grab_image()

    assert widget.datadisplay.grab_data.await_count == 3
    widget.close()
