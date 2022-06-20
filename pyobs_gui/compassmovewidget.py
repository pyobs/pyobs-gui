import logging
from typing import Any, Optional, Union, Dict
from PyQt5 import QtWidgets, QtCore
from astroplan import Observer
from pyobs.vfs import VirtualFileSystem

from pyobs.comm import Proxy, Comm
from pyobs.interfaces import IOffsetsRaDec, IOffsetsAltAz
from .base import BaseWidget
from .qt.compassmovewidget_ui import Ui_CompassMoveWidget


class CompassMoveWidget(QtWidgets.QWidget, BaseWidget, Ui_CompassMoveWidget):
    def __init__(self, parent: QtWidgets.QWidget, **kwargs: Any):
        QtWidgets.QWidget.__init__(self, parent)
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # button colors
        self.colorize_button(self.buttonOffsetEast, QtCore.Qt.blue)
        self.colorize_button(self.buttonOffsetNorth, QtCore.Qt.blue)
        self.colorize_button(self.buttonOffsetSouth, QtCore.Qt.blue)
        self.colorize_button(self.buttonOffsetWest, QtCore.Qt.blue)

    @QtCore.pyqtSlot(name="on_buttonOffsetNorth_clicked")
    @QtCore.pyqtSlot(name="on_buttonOffsetSouth_clicked")
    @QtCore.pyqtSlot(name="on_buttonOffsetEast_clicked")
    @QtCore.pyqtSlot(name="on_buttonOffsetWest_clicked")
    def _move_offset(self) -> None:
        self.run_background(self.__move_offset, self.sender())

    async def __move_offset(self, sender: QtWidgets.QWidget) -> None:
        # get offsets
        if isinstance(self.module, IOffsetsAltAz):
            off_alt, off_az = await self.module.get_offsets_altaz()
            off_ra, off_dec = self._offset_altaz_to_radec(off_alt, off_az)
        elif isinstance(self.module, IOffsetsRaDec):
            off_ra, off_dec = await self.module.get_offsets_radec()
        else:
            return

        # new offset
        user_offset = self.spinOffset.value() / 3600.0

        # who send event?
        if sender == self.buttonOffsetNorth:
            off_dec += user_offset
        elif sender == self.buttonOffsetSouth:
            off_dec -= user_offset
        elif sender == self.buttonOffsetEast:
            off_ra += user_offset
        elif sender == self.buttonOffsetWest:
            off_ra -= user_offset

        # move
        if isinstance(self.module, IOffsetsRaDec):
            self.run_background(self.module.set_offsets_radec, off_ra, off_dec)
        elif isinstance(self.module, IOffsetsAltAz):
            off_alt, off_az = self._offset_radec_to_altaz(off_ra, off_dec)
            self.run_background(self.module.set_offsets_altaz, off_alt, off_az)
        else:
            raise ValueError


__all__ = ["CompassMoveWidget"]
