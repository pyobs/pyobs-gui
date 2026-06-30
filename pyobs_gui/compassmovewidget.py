from typing import Any
from PySide6 import QtWidgets, QtCore  # type: ignore
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

    @QtCore.Slot()  # type: ignore
    def _move_offset(self) -> None:
        self.run_background(self.__move_offset, self.sender())

    async def __move_offset(self, sender: QtWidgets.QWidget) -> None:
        if self.observer is None:
            return

        # get offsets
        altaz = None
        has_offsets_altaz = await self.comm.has_proxy(self.module, IOffsetsAltAz)
        has_pointing_altaz = await self.comm.has_proxy(self.module, IPointingAltAz)
        has_offsets_radec = await self.comm.has_proxy(self.module, IOffsetsRaDec)
        if has_offsets_altaz and has_pointing_altaz:
            async with self.comm.proxy(self.module, IPointingAltAz) as p:
                alt, az = await p.get_altaz()  # type: ignore[attr-defined]
            altaz = SkyCoord(
                alt=alt * u.degree,  # type: ignore[attr-defined]
                az=az * u.degree,  # type: ignore[attr-defined]
                obstime=Time.now(),
                location=self.observer.location,
                frame="altaz",
            )
            async with self.comm.proxy(self.module, IOffsetsAltAz) as p:
                off_alt, off_az = await p.get_offsets_altaz()  # type: ignore[attr-defined]
            off_ra, off_dec = offset_altaz_to_radec(altaz, off_alt, off_az)
        elif has_offsets_radec:
            async with self.comm.proxy(self.module, IOffsetsRaDec) as p:
                off_ra, off_dec = await p.get_offsets_radec()  # type: ignore[attr-defined]
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
        if has_offsets_radec:
            async with self.comm.proxy(self.module, IOffsetsRaDec) as p:
                await p.set_offsets_radec(off_ra, off_dec)
        elif has_offsets_altaz and altaz is not None:
            off_alt, off_az = offset_radec_to_altaz(altaz.transform_to(ICRS()), off_ra, off_dec, self.observer.location)  # noqa: E501
            async with self.comm.proxy(self.module, IOffsetsAltAz) as p:
                await p.set_offsets_altaz(off_alt, off_az)
        else:
            raise ValueError


__all__ = ["CompassMoveWidget"]
