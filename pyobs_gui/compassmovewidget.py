from typing import Any
from PySide6 import QtWidgets, QtCore  # type: ignore
import qasync  # type: ignore
import astropy.units as u
from astropy.coordinates import SkyCoord, ICRS

from pyobs.interfaces import IOffsetsRaDec, IOffsetsAltAz, IPointingAltAz
from pyobs.utils.coordinates import offset_altaz_to_radec, offset_radec_to_altaz
from pyobs.utils.time import Time
from .base import BaseWidget
from .qt.compassmovewidget_ui import Ui_CompassMoveWidget


class CompassMoveWidget(BaseWidget, Ui_CompassMoveWidget):
    def __init__(self, parent: QtWidgets.QWidget, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # button colors
        self.colorize_button(self.buttonOffsetEast, QtCore.Qt.GlobalColor.blue)
        self.colorize_button(self.buttonOffsetNorth, QtCore.Qt.GlobalColor.blue)
        self.colorize_button(self.buttonOffsetSouth, QtCore.Qt.GlobalColor.blue)
        self.colorize_button(self.buttonOffsetWest, QtCore.Qt.GlobalColor.blue)

        # signals
        self.buttonOffsetEast.clicked.connect(self._move_offset)
        self.buttonOffsetNorth.clicked.connect(self._move_offset)
        self.buttonOffsetSouth.clicked.connect(self._move_offset)
        self.buttonOffsetWest.clicked.connect(self._move_offset)

    @qasync.asyncSlot()  # type: ignore
    async def _move_offset(self) -> None:
        module = self.module

        # get offsets
        if self.observer is not None and isinstance(module, IOffsetsAltAz) and isinstance(module, IPointingAltAz):
            alt, az = await module.get_altaz()
            altaz = SkyCoord(
                alt=alt * u.degree,
                az=alt * u.degree,
                obstime=Time.now(),
                location=self.observer.location,
                frame="altaz",
            )
            off_alt, off_az = await module.get_offsets_altaz()
            off_ra, off_dec = offset_altaz_to_radec(altaz, off_alt, off_az)
        elif isinstance(module, IOffsetsRaDec):
            off_ra, off_dec = await module.get_offsets_radec()
        else:
            return

        # new offset
        user_offset = self.spinOffset.value() / 3600.0

        # who send event?
        if self.sender() == self.buttonOffsetNorth:
            off_dec += user_offset
        elif self.sender() == self.buttonOffsetSouth:
            off_dec -= user_offset
        elif self.sender() == self.buttonOffsetEast:
            off_ra += user_offset
        elif self.sender() == self.buttonOffsetWest:
            off_ra -= user_offset

        # move
        if isinstance(module, IOffsetsRaDec):
            await module.set_offsets_radec(off_ra, off_dec)
        elif isinstance(module, IOffsetsAltAz) and self.observer is not None:
            off_alt, off_az = offset_radec_to_altaz(altaz.transform_to(ICRS()), off_ra, off_dec, self.observer.location)
            await module.set_offsets_altaz(off_alt, off_az)
        else:
            raise ValueError


__all__ = ["CompassMoveWidget"]
