import logging
from typing import Any

from astroplan import Observer
from pyobs.comm import Comm
from pyobs.interfaces import (
    IImageFormat,
    IImageType,
    ImageTypeState,
)
from pyobs.utils.enums import ImageFormat, ImageType
from pyobs.vfs import VirtualFileSystem
from PySide6 import QtCore  # type: ignore

from .base import BaseWidget
from .qt.videograbwidget_ui import Ui_VideoGrabWidget

log = logging.getLogger(__name__)


class VideoGrabWidget(BaseWidget, Ui_VideoGrabWidget):
    """Image-type/count/broadcast controls, grab/abort buttons, and the resulting FITS preview
    (via datadisplay) for a module's video stream. Paired with VideoWidget (same IVideo
    interface, a separate tab) for the live-view side -- the two don't share any state."""

    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        self.exposures_left = 0

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonGrabImage.clicked.connect(self.grab_image)
        self.buttonAbort.clicked.connect(self.abort_sequence)

        # before first update, disable myself
        self.setEnabled(False)

        # interfaces cache
        self._interfaces: list = []

        # set exposure types
        image_types = sorted([it.name for it in ImageType])
        self.comboImageType.addItems(image_types)
        self.comboImageType.setCurrentText("OBJECT")

        # initial values
        self.comboImageType.setCurrentIndex(image_types.index("OBJECT"))

    async def open(
        self,
        modules: list[str] | None = None,
        comm: Comm | None = None,
        observer: Observer | None = None,
        vfs: VirtualFileSystem | dict[str, Any] | None = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)
        await self.datadisplay.open(modules=modules, comm=comm, observer=observer, vfs=vfs)

    async def _init(self) -> None:
        # get interfaces for visibility checks
        self._interfaces = await self.comm.get_interfaces(self.module)
        has_image_type = IImageType in self._interfaces

        # hide single controls, if necessary
        self.labelImageType.setVisible(has_image_type)
        self.comboImageType.setVisible(has_image_type)

        # subscribe to state
        if has_image_type:
            await self.comm.subscribe_state(self.module, IImageType, self._on_image_type_state)

        # update GUI
        self.signal_update_gui.emit()

    def _on_image_type_state(self, state: ImageTypeState) -> None:
        self.comboImageType.setCurrentText(state.image_type.name)

    def update_gui(self) -> None:
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # enable/disable buttons
        self.buttonAbort.setEnabled(self.exposures_left > 0)

        # exposures left
        if self.exposures_left > 0:
            self.labelExposuresLeft.setText("%d exposure(s) left" % self.exposures_left)
        else:
            self.labelExposuresLeft.setText("")

    def grab_image(self) -> None:
        self.run_background(self._grab_image)

    async def _grab_image(self) -> None:
        # set image format
        if IImageFormat in self._interfaces:
            image_format = ImageFormat[self.comboImageFormat.currentText()]  # type: ignore[attr-defined]
            async with self.comm.proxy(self.module, IImageFormat) as proxy:
                await proxy.set_image_format(image_format)

        # set initial image count
        self.exposures_left = self.spinCount.value()

        # signal GUI update
        self.signal_update_gui.emit()

        # start exposures
        await self._expose_task_func()

    async def _expose_task_func(self) -> None:
        # get image type
        image_type = ImageType(self.comboImageType.currentText().lower())

        # do exposure(s)
        while self.exposures_left > 0:
            # set image type
            if IImageType in self._interfaces:
                async with self.comm.proxy(self.module, IImageType) as proxy:
                    await proxy.set_image_type(image_type)

            # expose
            broadcast = self.checkBroadcast.isChecked()
            await self.datadisplay.grab_data(broadcast)

            # decrement number of exposures left
            self.exposures_left -= 1

            # signal GUI update
            self.signal_update_gui.emit()

    @QtCore.Slot()  # type: ignore
    def abort_sequence(self) -> None:
        self.exposures_left = 0


__all__ = ["VideoGrabWidget"]
