import asyncio
from enum import Enum
from typing import Any

import numpy as np
import qasync  # type: ignore
from PySide6 import QtWidgets, QtCore  # type: ignore
from astropy.coordinates import SkyCoord, ICRS, AltAz, get_sun
import astropy.units as u
import logging
from astroquery.exceptions import InvalidQueryError
import astropy.constants
from sunpy.coordinates.frames import Helioprojective, HeliographicStonyhurst  # type: ignore

from pyobs.interfaces import (
    IPointingRaDec,
    RaDecState,
    IPointingAltAz,
    AltAzState,
    IPointingHelioprojective,
    IPointingHGS,
    IOffsetsRaDec,
    RaDecOffsetState,
    IOffsetsAltAz,
    AltAzOffsetState,
    IFilters,
    IFocuser,
    ITemperatures,
    IMotion,
    MotionState,
)
from pyobs.utils.enums import MotionStatus
from pyobs.utils.time import Time
from .filterwidget import FilterWidget
from .focuswidget import FocusWidget
from .temperatureswidget import TemperaturesWidget
from .compassmovewidget import CompassMoveWidget
from .qt.telescopewidget_ui import Ui_TelescopeWidget
from .base import BaseWidget

log = logging.getLogger(__name__)


class COORDS(Enum):
    EQUITORIAL = "Equitorial"
    HORIZONTAL = "Horizontal"
    ORBIT_ELEMENTS = "Orbit Elements"
    HELIOGRAPHIC_STONYHURST = "Heliographic Stonyhurst"
    HELIOPROJECTIVE_RADIAL = "Helioprojective Radial"
    HELIOPROJECTIVE_MUPSI = "Helioprojective Mu/Psi"


class TelescopeWidget(BaseWidget, Ui_TelescopeWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)  # type: ignore

        # cached state
        self._motion_status = MotionStatus.UNKNOWN
        self._ra_dec = None
        self._alt_az = None
        self._off_ra = None
        self._off_dec = None
        self._off_alt = None
        self._off_az = None

        # cached interfaces — populated in open()
        self._interfaces: list[type] = []

        # before first update, disable myself
        self.setEnabled(False)

        # move widgets
        self._MOVE_WIDGETS = {
            COORDS.EQUITORIAL: self.pageMoveEquatorial,
            COORDS.HORIZONTAL: self.pageMoveHorizontal,
            COORDS.HELIOGRAPHIC_STONYHURST: self.pageMoveHeliographicStonyhurst,
            COORDS.HELIOPROJECTIVE_RADIAL: self.pageMoveHelioprojectiveRadial,
            COORDS.HELIOPROJECTIVE_MUPSI: self.pageMoveHelioprojectiveMuPsi,
            COORDS.ORBIT_ELEMENTS: self.pageMoveOrbitElements,
        }

        # calculate dest coordinates
        self._DEST_CALC = {
            COORDS.EQUITORIAL: self._calc_dest_equatorial,
            COORDS.HORIZONTAL: self._calc_dest_horizontal,
            COORDS.HELIOGRAPHIC_STONYHURST: self._calc_dest_heliographic_stonyhurst,
            COORDS.HELIOPROJECTIVE_RADIAL: self._calc_dest_helioprojective_radial,
            COORDS.HELIOPROJECTIVE_MUPSI: self._calc_dest_helioprojective_radial,
            COORDS.ORBIT_ELEMENTS: self._calc_dest_orbit_elements,
        }

        # button colors
        self.colorize_button(self.buttonInit, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonPark, QtCore.Qt.GlobalColor.yellow)
        self.colorize_button(self.buttonStop, QtCore.Qt.GlobalColor.red)
        self.colorize_button(self.buttonMove, QtCore.Qt.GlobalColor.blue)
        self.colorize_button(self.buttonSetAltOffset, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonSetAzOffset, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonSetRaOffset, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonSetDecOffset, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonResetHorizontalOffsets, QtCore.Qt.GlobalColor.yellow)
        self.colorize_button(self.buttonResetEquatorialOffsets, QtCore.Qt.GlobalColor.yellow)
        self.colorize_button(self.buttonSimbadQuery, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonJplHorizonsQuery, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonHorizonsQuery, QtCore.Qt.GlobalColor.green)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.buttonMove.clicked.connect(self.move)
        self.buttonSimbadQuery.clicked.connect(self._query_simbad)
        self.buttonJplHorizonsQuery.clicked.connect(self._query_jpl_horizons)
        self.comboSolarSystemBody.currentTextChanged.connect(self._select_solar_system)
        self.buttonHorizonsQuery.clicked.connect(self._query_horizons)
        self.spinMoveAlt.editingFinished.connect(self._calc_dest_horizontal)
        self.spinMoveAz.valueChanged.connect(self._calc_dest_horizontal)
        self.textMoveRA.editingFinished.connect(self._calc_dest_equatorial)
        self.textMoveDec.editingFinished.connect(self._calc_dest_equatorial)
        self.spinMoveHGSLat.valueChanged.connect(self._calc_dest_heliographic_stonyhurst)
        self.spinMoveHGSLat.valueChanged.connect(self._calc_dest_heliographic_stonyhurst)
        self.spinMoveHelioprojectiveRadialMu.valueChanged.connect(self._calc_dest_helioprojective_radial)
        self.spinMoveHelioprojectiveRadialPsi.valueChanged.connect(self._calc_dest_helioprojective_radial)
        self.comboMoveType.currentIndexChanged.connect(self.select_coord_type)

        self.buttonInit.clicked.connect(self._init_telescope)
        self.buttonPark.clicked.connect(self._park_telescope)
        self.buttonStop.clicked.connect(self._stop_telescope)
        self.buttonSetAltOffset.clicked.connect(self._set_offset)
        self.buttonSetAzOffset.clicked.connect(self._set_offset)
        self.buttonSetRaOffset.clicked.connect(self._set_offset)
        self.buttonSetDecOffset.clicked.connect(self._set_offset)
        self.buttonResetHorizontalOffsets.clicked.connect(self._set_offset)
        self.buttonResetEquatorialOffsets.clicked.connect(self._set_offset)

    # pyrefly: ignore [bad-override]
    async def open(self, **kwargs: Any) -> None:
        await BaseWidget.open(self, **kwargs)
        await self.compassmovewidget.open(**kwargs)
        self.compassmovewidget.show_extract_button(CompassMoveWidget, f'Offset "{self.module}"')

        # cache interfaces for sync methods (move, update_gui, etc.)
        self._interfaces = await self.comm.get_interfaces(self.module)

        # add coord types
        if IPointingRaDec in self._interfaces:
            self.comboMoveType.addItem(COORDS.EQUITORIAL.value)
        if IPointingAltAz in self._interfaces:
            self.comboMoveType.addItem(COORDS.HORIZONTAL.value)
        if IPointingHGS in self._interfaces or IPointingHelioprojective in self._interfaces:
            self.comboMoveType.addItem(COORDS.HELIOGRAPHIC_STONYHURST.value)
            self.comboMoveType.addItem(COORDS.HELIOPROJECTIVE_RADIAL.value)
            self.comboMoveType.addItem(COORDS.HELIOPROJECTIVE_MUPSI.value)
        if self.comboMoveType.count() > 0:
            self.comboMoveType.setCurrentIndex(0)

        # offsets
        self.groupEquatorialOffsets.setVisible(IOffsetsRaDec in self._interfaces)
        self.groupHorizontalOffsets.setVisible(IOffsetsAltAz in self._interfaces)

        # fill sidebar
        if IFilters in self._interfaces:
            await self.add_to_sidebar(self.create_widget(FilterWidget, module=self.module))
        if IFocuser in self._interfaces:
            await self.add_to_sidebar(self.create_widget(FocusWidget, module=self.module))
        if ITemperatures in self._interfaces:
            await self.add_to_sidebar(self.create_widget(TemperaturesWidget, module=self.module))

        # init coord type
        self.select_coord_type()

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IMotion, self._on_motion_state)
        if IPointingRaDec in self._interfaces:
            await self.comm.subscribe_state(self.module, IPointingRaDec, self._on_radec_state)
        if IPointingAltAz in self._interfaces:
            await self.comm.subscribe_state(self.module, IPointingAltAz, self._on_altaz_state)
        if IOffsetsRaDec in self._interfaces:
            await self.comm.subscribe_state(self.module, IOffsetsRaDec, self._on_offsets_radec_state)
        if IOffsetsAltAz in self._interfaces:
            await self.comm.subscribe_state(self.module, IOffsetsAltAz, self._on_offsets_altaz_state)

    # -------------------------------------------------------------------------
    # State callbacks
    # -------------------------------------------------------------------------

    def _on_motion_state(self, state: MotionState) -> None:
        self._motion_status = state.status
        self.signal_update_gui.emit()

    def _on_radec_state(self, state: RaDecState) -> None:
        if self.observer is not None:
            self._ra_dec = SkyCoord(
                ra=state.ra * u.deg,  # type: ignore[attr-defined]
                dec=state.dec * u.deg,  # type: ignore[attr-defined]
                frame="icrs",
                location=self.observer.location,
                obstime=Time.now(),
            )
        else:
            self._ra_dec = None
        self.signal_update_gui.emit()

    def _on_altaz_state(self, state: AltAzState) -> None:
        if self.observer is not None:
            self._alt_az = SkyCoord(
                alt=state.alt * u.deg,  # type: ignore[attr-defined]
                az=state.az * u.deg,  # type: ignore[attr-defined]
                frame="altaz",
                location=self.observer.location,
                obstime=Time.now(),
            )
        else:
            self._alt_az = None
        self.signal_update_gui.emit()

    def _on_offsets_radec_state(self, state: RaDecOffsetState) -> None:
        self._off_ra = state.ra
        self._off_dec = state.dec
        if self._ra_dec is not None:
            self._off_alt, self._off_az = self._offset_radec_to_altaz(self._off_ra, self._off_dec)
        else:
            self._off_alt, self._off_az = None, None
        self.signal_update_gui.emit()

    def _on_offsets_altaz_state(self, state: AltAzOffsetState) -> None:
        self._off_alt = state.alt
        self._off_az = state.az
        if self._alt_az is not None:
            self._off_ra, self._off_dec = self._offset_altaz_to_radec(self._off_alt, self._off_az)
        else:
            self._off_ra, self._off_dec = None, None
        self.signal_update_gui.emit()

    # -------------------------------------------------------------------------
    # Coordinate helpers
    # -------------------------------------------------------------------------

    def _offset_altaz_to_radec(self, alt: float, az: float) -> tuple[float, float]:
        if self._alt_az is None:
            raise ValueError("No Alt/Az coordinates available.")
        p0 = self._alt_az.icrs
        # pyrefly: ignore [missing-attribute]
        p1 = self._alt_az.spherical_offsets_by(az * u.degree, alt * u.degree).icrs
        p0 = SkyCoord(ra=p0.ra, dec=p0.dec, frame="icrs")
        p1 = SkyCoord(ra=p1.ra, dec=p1.dec, frame="icrs")
        dra, ddec = p0.spherical_offsets_to(p1)
        return float(dra.degree), float(ddec.degree)

    def _offset_radec_to_altaz(self, ra: float, dec: float) -> tuple[float, float]:
        if self._ra_dec is None or self.observer is None:
            raise ValueError("No RA/Dec coordinates available.")
        altaz = AltAz(location=self.observer.location, obstime=self._ra_dec.obstime)
        p0 = self._ra_dec.transform_to(altaz)
        # pyrefly: ignore [missing-attribute]
        p1 = self._ra_dec.spherical_offsets_by(ra * u.degree, dec * u.degree).transform_to(altaz)
        daz, dalt = p0.spherical_offsets_to(p1)
        return float(dalt.degree), float(daz.degree)

    # -------------------------------------------------------------------------
    # GUI update
    # -------------------------------------------------------------------------

    def update_gui(self) -> None:
        self.setEnabled(True)

        self.labelStatus.setText(self._motion_status.upper())

        self.buttonInit.setEnabled(self._motion_status == MotionStatus.PARKED)
        self.buttonPark.setEnabled(
            self._motion_status
            not in [
                MotionStatus.PARKED,
                MotionStatus.ERROR,
                MotionStatus.PARKING,
                MotionStatus.INITIALIZING,
            ]
        )
        self.buttonStop.setEnabled(self._motion_status in [MotionStatus.SLEWING, MotionStatus.TRACKING])
        initialized = self._motion_status in [
            MotionStatus.SLEWING,
            MotionStatus.TRACKING,
            MotionStatus.IDLE,
            MotionStatus.POSITIONED,
        ]
        self.buttonMove.setEnabled(initialized)
        self.compassmovewidget.setEnabled(initialized)
        self.buttonSetAltOffset.setEnabled(initialized)
        self.buttonSetAzOffset.setEnabled(initialized)
        self.buttonSetRaOffset.setEnabled(initialized)
        self.buttonSetDecOffset.setEnabled(initialized)
        self.buttonResetHorizontalOffsets.setEnabled(initialized)
        self.buttonResetEquatorialOffsets.setEnabled(initialized)

        if self._ra_dec is not None and np.isfinite(self._ra_dec.ra.deg) and np.isfinite(self._ra_dec.dec.deg):
            ra_h = float(self._ra_dec.ra.hour)
            h, rem = divmod(ra_h, 1)
            m, rem = divmod(rem * 60, 1)
            self.labelCurRA.setText(f"{int(h):02d}:{int(m):02d}:{rem * 60:06.3f}")
            dec_d = float(self._ra_dec.dec.deg)
            sign = "+" if dec_d >= 0 else "-"
            d, rem = divmod(abs(dec_d), 1)
            m, rem = divmod(rem * 60, 1)
            self.labelCurDec.setText(f"{sign}{int(d):02d}:{int(m):02d}:{rem * 60:06.3f}")
        else:
            self.labelCurRA.setText("N/A")
            self.labelCurDec.setText("N/A")
        if self._alt_az is not None:
            self.labelCurAlt.setText("%.3f°" % self._alt_az.alt.degree)
            self.labelCurAz.setText("%.3f°" % self._alt_az.az.degree)
        else:
            self.labelCurAlt.setText("N/A")
            self.labelCurAz.setText("N/A")

        if IOffsetsRaDec in self._interfaces:
            self.textOffsetRA.setText("N/A" if self._off_ra is None else '%.2f"' % (self._off_ra * 3600.0,))
            self.textOffsetDec.setText("N/A" if self._off_dec is None else '%.2f"' % (self._off_dec * 3600.0,))
        if IOffsetsAltAz in self._interfaces:
            self.textOffsetAlt.setText("N/A" if self._off_alt is None else '%.2f"' % (self._off_alt * 3600.0,))
            self.textOffsetAz.setText("N/A" if self._off_az is None else '%.2f"' % (self._off_az * 3600.0,))

    # -------------------------------------------------------------------------
    # Move command (stays sync — uses QInputDialog + branching)
    # -------------------------------------------------------------------------

    # pyrefly: ignore [bad-override]
    def move(self) -> None:
        text = self.comboMoveType.currentText()
        coord = COORDS(text)

        if coord == COORDS.EQUITORIAL:
            ra = self.textMoveRA.text()
            dec = self.textMoveDec.text()
            try:
                # pyrefly: ignore [missing-attribute]
                coords = SkyCoord(ra + " " + dec, frame=ICRS, unit=(u.hour, u.deg))
            except ValueError:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Invalid coordinates.")
                return
            if IPointingRaDec in self._interfaces:
                self.run_background(self._do_move_radec, float(coords.ra.degree), float(coords.dec.degree))
            else:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Telescope does not support equatorial coordinates.")

        elif coord == COORDS.HORIZONTAL:
            alt = self.spinMoveAlt.value()
            az = self.spinMoveAz.value()
            if IPointingAltAz in self._interfaces:
                self.run_background(self._do_move_altaz, alt, az)
            else:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Telescope does not support horizontal coordinates.")

        elif coord == COORDS.HELIOGRAPHIC_STONYHURST:
            lon = self.spinMoveHGSLon.value()
            lat = self.spinMoveHGSLat.value()
            if IPointingHGS in self._interfaces:
                self.run_background(self._do_move_hgs, lon, lat)
            else:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Telescope does not support stonyhurst coordinates.")

        elif coord == COORDS.HELIOPROJECTIVE_RADIAL:
            theta_x = self.spinMoveHelioProjectiveRadialTx.value() / 3600.0
            theta_y = self.spinMoveHelioProjectiveRadialTy.value() / 3600.0
            if IPointingHelioprojective in self._interfaces:
                self.run_background(self._do_move_helioprojective, theta_x, theta_y)
            else:
                QtWidgets.QMessageBox.critical(
                    self, "pyobs", "Telescope does not support helioprojective radial coordinates."
                )

        elif coord == COORDS.HELIOPROJECTIVE_MUPSI:
            mu = self.spinMoveHelioprojectiveRadialMu.value()
            psi = np.deg2rad(self.spinMoveHelioprojectiveRadialPsi.value())
            alpha = np.arccos(mu)
            dsun = get_sun(Time.now()).distance
            # pyrefly: ignore [missing-attribute]
            rsun = astropy.constants.R_sun
            theta = np.arctan(rsun * np.sin(alpha) / (dsun - (rsun * mu)))
            tx = -theta * np.sin(psi)
            ty = theta * np.cos(psi)
            heliproj = SkyCoord(tx, ty, obstime=Time.now(), frame=Helioprojective, observer="earth")

            if IPointingHelioprojective in self._interfaces:
                self.run_background(self._do_move_helioprojective, heliproj.Tx.degree, heliproj.Ty.degree)
            elif IPointingHGS in self._interfaces:
                stony = heliproj.transform_to(HeliographicStonyhurst)
                # pyrefly: ignore [missing-attribute]
                lon, lat = float(stony.lon.to(u.degree).value), float(stony.lat.to(u.degree).value)
                self.run_background(self._do_move_hgs, lon, lat)
            else:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Telescope does not support Mu/Psi coordinates.")

    async def _do_move_radec(self, ra: float, dec: float) -> None:
        async with self.comm.proxy(self.module, IPointingRaDec) as proxy:
            await proxy.move_radec(ra, dec)

    async def _do_move_altaz(self, alt: float, az: float) -> None:
        async with self.comm.proxy(self.module, IPointingAltAz) as proxy:
            await proxy.move_altaz(alt, az)

    async def _do_move_hgs(self, lon: float, lat: float) -> None:
        async with self.comm.proxy(self.module, IPointingHGS) as proxy:
            await proxy.move_hgs_lon_lat(lon, lat)

    async def _do_move_helioprojective(self, tx: float, ty: float) -> None:
        async with self.comm.proxy(self.module, IPointingHelioprojective) as proxy:
            await proxy.move_helioprojective(tx, ty)

    # -------------------------------------------------------------------------
    # Motion control slots
    # -------------------------------------------------------------------------

    @qasync.asyncSlot()  # type: ignore
    async def _init_telescope(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.init()

    @qasync.asyncSlot()  # type: ignore
    async def _park_telescope(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.park()

    @qasync.asyncSlot()  # type: ignore
    async def _stop_telescope(self) -> None:
        async with self.comm.proxy(self.module, IMotion) as proxy:
            await proxy.stop_motion("ITelescope")

    # -------------------------------------------------------------------------
    # Offset slots (must stay sync — uses self.sender())
    # -------------------------------------------------------------------------

    @QtCore.Slot()  # type: ignore
    def _set_offset(self) -> None:
        if self.sender() == self.buttonResetHorizontalOffsets:
            asyncio.create_task(self._do_set_offsets_altaz(0.0, 0.0))
        elif self.sender() == self.buttonResetEquatorialOffsets:
            asyncio.create_task(self._do_set_offsets_radec(0.0, 0.0))
        else:
            new_value, ok = QtWidgets.QInputDialog.getDouble(self, "Set offset", 'New offset ["]', 0, -9999, 9999)
            if ok:
                if self.sender() == self.buttonSetAltOffset:
                    asyncio.create_task(self._do_set_offsets_altaz(new_value / 3600.0, self._off_az or 0.0))
                elif self.sender() == self.buttonSetAzOffset:
                    asyncio.create_task(self._do_set_offsets_altaz(self._off_alt or 0.0, new_value / 3600.0))
                elif self.sender() == self.buttonSetRaOffset:
                    asyncio.create_task(self._do_set_offsets_radec(new_value / 3600.0, self._off_dec or 0.0))
                elif self.sender() == self.buttonSetDecOffset:
                    asyncio.create_task(self._do_set_offsets_radec(self._off_ra or 0.0, new_value / 3600.0))

    async def _do_set_offsets_altaz(self, alt: float, az: float) -> None:
        async with self.comm.proxy(self.module, IOffsetsAltAz) as proxy:
            await proxy.set_offsets_altaz(alt, az)

    async def _do_set_offsets_radec(self, ra: float, dec: float) -> None:
        async with self.comm.proxy(self.module, IOffsetsRaDec) as proxy:
            await proxy.set_offsets_radec(ra, dec)

    # -------------------------------------------------------------------------
    # Coordinate lookup helpers (unchanged)
    # -------------------------------------------------------------------------

    def _query_simbad(self) -> None:
        from astroquery.simbad import Simbad

        self.comboSolarSystemBody.setCurrentText("")
        self.textJplHorizonsName.clear()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        result = Simbad.query_object(self.textSimbadName.text())
        QtWidgets.QApplication.restoreOverrideCursor()
        if result is None:
            QtWidgets.QMessageBox.critical(self, "Simbad", "No result found")
            return
        for r in result:
            # pyrefly: ignore [missing-attribute]
            c = SkyCoord(r["ra"] * u.deg, r["dec"] * u.deg, frame="icrs")
            ra, dec = c.to_string("hmsdms").split(" ")
            self.textMoveRA.setText(ra)
            self.textMoveDec.setText(dec)
        self._calc_dest_equatorial(clear=False)

    def _query_jpl_horizons(self) -> None:
        from astroquery.jplhorizons import Horizons

        self.comboSolarSystemBody.setCurrentText("")
        self.textSimbadName.clear()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        try:
            obj = Horizons(id=self.textJplHorizonsName.text(), location=None, epochs=Time.now().jd)
            eph = obj.ephemerides()
        except InvalidQueryError:
            QtWidgets.QMessageBox.critical(self, "JPL Horizons", "No result found")
            return
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "JPL Horizons", "Invalid result")
            return
        finally:
            QtWidgets.QApplication.restoreOverrideCursor()
        # pyrefly: ignore [missing-attribute]
        coord = SkyCoord(eph["RA"][0] * u.deg, eph["DEC"][0] * u.deg, frame="icrs")
        # pyrefly: ignore [missing-attribute]
        self.textMoveRA.setText(coord.ra.to_string(unit=u.hour, sep=" "))
        self.textMoveDec.setText(coord.dec.to_string(sep=" "))
        self._calc_dest_equatorial(clear=False)

    def _select_solar_system(self, body: str) -> None:
        from astropy.coordinates import solar_system_ephemeris, get_body

        if body == "" or self.observer is None:
            return
        self.textSimbadName.clear()
        self.textJplHorizonsName.clear()
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.CursorShape.WaitCursor)
        with solar_system_ephemeris.set("builtin"):
            body_coords = get_body(body, Time.now(), self.observer.location)
        QtWidgets.QApplication.restoreOverrideCursor()
        # pyrefly: ignore [missing-attribute]
        self.textMoveRA.setText(body_coords.ra.to_string(unit=u.hour, sep=" ", precision=2))
        self.textMoveDec.setText(body_coords.dec.to_string(sep=" ", precision=2))
        self._calc_dest_equatorial(clear=False)

    def _query_horizons(self) -> None:
        from astroquery.jplhorizons import Horizons

        try:
            obj = Horizons(id=self.textHorizonsName.text(), location=None, epochs=Time.now().jd)
        except InvalidQueryError:
            QtWidgets.QMessageBox.critical(self, "MPC", "No result found")
            return
        try:
            eph = obj.elements()
        except ValueError:
            pass

        self.spinOrbitElementsEcc.setValue(eph["e"][0])
        self.spinOrbitElementsIncl.setValue(eph["incl"][0])
        self.spinOrbitElementsSemiMajorAxis.setValue(eph["a"][0])
        self.spinOrbitElementsMA.setValue(eph["M"][0])
        self.spinOrbitElementsOmega.setValue(eph["Omega"][0])
        self.spinOrbitElementsPerifocus.setValue(eph["w"][0])
        self.spinOrbitElementsEpoch.setValue(eph["datetime_jd"][0])

    def _show_dest_coords(self, ra: str = "N/A", dec: str = "N/A", alt: str = "N/A", az: str = "N/A") -> None:
        self.textDestRA.setText(ra if isinstance(ra, str) else ra.to_string(u.hour, sep=":"))
        self.textDestDec.setText(dec if isinstance(dec, str) else dec.to_string(sep=":"))
        self.textDestAlt.setText(alt if isinstance(alt, str) else "%.2f°" % alt.degree)
        self.textDestAz.setText(az if isinstance(az, str) else "%.2f°" % az.degree)

    def _calc_dest_horizontal(self) -> None:
        if self.observer is None:
            raise ValueError("No observer set.")
        alt_az = SkyCoord(
            # pyrefly: ignore [missing-attribute]
            alt=self.spinMoveAlt.value() * u.deg,
            # pyrefly: ignore [missing-attribute]
            az=self.spinMoveAz.value() * u.deg,
            frame=AltAz,
            location=self.observer.location,
            obstime=Time.now(),
        )
        ra_dec = alt_az.icrs
        self._show_dest_coords(ra_dec.ra, ra_dec.dec, alt_az.alt, alt_az.az)

    def _calc_dest_equatorial(self, clear: bool = True) -> None:
        if self.observer is None:
            raise ValueError("No observer set.")
        if clear:
            self.textSimbadName.clear()
            self.comboSolarSystemBody.setCurrentText("")
            self.textJplHorizonsName.clear()
        try:
            ra_dec = SkyCoord(
                self.textMoveRA.text() + " " + self.textMoveDec.text(),
                frame=ICRS,
                # pyrefly: ignore [missing-attribute]
                unit=(u.hour, u.deg),
            )
        except ValueError:
            self._show_dest_coords()
            return
        alt_az = self.observer.altaz(Time.now(), ra_dec)
        self._show_dest_coords(ra_dec.ra, ra_dec.dec, alt_az.alt, alt_az.az)

    def _calc_dest_heliographic_stonyhurst(self) -> None:
        if self.observer is None:
            raise ValueError("No observer set.")
        sun = self.observer.sun_altaz(Time.now())
        sun_radec = sun.icrs
        self._show_dest_coords(sun_radec.ra, sun_radec.dec, sun.alt, sun.az)

    def _calc_dest_helioprojective_radial(self) -> None:
        if self.observer is None:
            return
        sun = self.observer.sun_altaz(Time.now())
        sun_radec = sun.icrs
        self._show_dest_coords(sun_radec.ra, sun_radec.dec, sun.alt, sun.az)

    def _calc_dest_orbit_elements(self) -> None:
        pass

    def select_coord_type(self) -> None:
        text = self.comboMoveType.currentText()
        try:
            coord = COORDS(text)
        except ValueError:
            return
        self.stackedMove.setCurrentWidget(self._MOVE_WIDGETS[coord])
        self._DEST_CALC[coord]()
