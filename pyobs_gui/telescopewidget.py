from enum import Enum
from typing import Any, Tuple, Optional, Union, Dict, List

import numpy as np
from PyQt5 import QtWidgets, QtCore
from astroplan import Observer
from astropy.coordinates import SkyCoord, ICRS, AltAz, get_sun
import astropy.units as u
import logging
from astroquery.exceptions import InvalidQueryError
import astropy.constants
from sunpy.coordinates.frames import Helioprojective, HeliographicStonyhurst

from pyobs.comm import Proxy, Comm
from pyobs.events import MotionStatusChangedEvent, Event
from pyobs.interfaces import (
    IPointingRaDec,
    IPointingAltAz,
    IPointingHelioprojective,
    IPointingHGS,
    IOffsetsRaDec,
    IOffsetsAltAz,
    IFilters,
    IFocuser,
    ITemperatures,
    IMotion,
)
from pyobs.utils.enums import MotionStatus
from pyobs.utils.time import Time
from pyobs.vfs import VirtualFileSystem
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


class TelescopeWidget(QtWidgets.QWidget, BaseWidget, Ui_TelescopeWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, **kwargs)
        self.setupUi(self)

        # variables
        self._motion_status = MotionStatus.UNKNOWN
        self._ra_dec = None
        self._alt_az = None
        self._off_ra = None
        self._off_dec = None
        self._off_alt = None
        self._off_az = None

        # before first update, disable mys
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

        # plot
        # self.figure = plt.figure()
        # self.plot = VisPlot(self.figure, self.environment)
        # self.canvas = FigureCanvas(self.figure)
        # self.widgetPlot.setLayout(QtWidgets.QVBoxLayout())
        # self.widgetPlot.layout().addWidget(self.canvas)
        # self.first = True

        # button colors
        self.colorize_button(self.buttonInit, QtCore.Qt.green)
        self.colorize_button(self.buttonPark, QtCore.Qt.yellow)
        self.colorize_button(self.buttonStop, QtCore.Qt.red)
        self.colorize_button(self.buttonMove, QtCore.Qt.blue)
        self.colorize_button(self.buttonSetAltOffset, QtCore.Qt.green)
        self.colorize_button(self.buttonSetAzOffset, QtCore.Qt.green)
        self.colorize_button(self.buttonSetRaOffset, QtCore.Qt.green)
        self.colorize_button(self.buttonSetDecOffset, QtCore.Qt.green)
        self.colorize_button(self.buttonResetHorizontalOffsets, QtCore.Qt.yellow)
        self.colorize_button(self.buttonResetEquatorialOffsets, QtCore.Qt.yellow)
        self.colorize_button(self.buttonSimbadQuery, QtCore.Qt.green)
        self.colorize_button(self.buttonJplHorizonsQuery, QtCore.Qt.green)
        self.colorize_button(self.buttonHorizonsQuery, QtCore.Qt.green)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def open(
        self,
        modules: Optional[List[Proxy]] = None,
        comm: Optional[Comm] = None,
        observer: Optional[Observer] = None,
        vfs: Optional[Union[VirtualFileSystem, Dict[str, Any]]] = None,
    ) -> None:
        """Open module."""
        await BaseWidget.open(self, modules=modules, comm=comm, observer=observer, vfs=vfs)
        await self.compassmovewidget.open(modules=modules, comm=comm, observer=observer, vfs=vfs)
        self.compassmovewidget.show_extract_button(CompassMoveWidget, f'Offset "{modules[0].name}"')

        # subscribe to events
        if self.comm is not None:
            await self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

        # add coord types
        if isinstance(self.module, IPointingRaDec):
            self.comboMoveType.addItem(COORDS.EQUITORIAL.value)
            # self.comboMoveType.addItem(COORDS.ORBIT_ELEMENTS.value)
        if isinstance(self.module, IPointingAltAz):
            self.comboMoveType.addItem(COORDS.HORIZONTAL.value)
        if isinstance(self.module, IPointingHGS) or isinstance(self.module, IPointingHelioprojective):
            self.comboMoveType.addItem(COORDS.HELIOGRAPHIC_STONYHURST.value)
            self.comboMoveType.addItem(COORDS.HELIOPROJECTIVE_RADIAL.value)
            self.comboMoveType.addItem(COORDS.HELIOPROJECTIVE_MUPSI.value)
        if self.comboMoveType.count() > 0:
            self.comboMoveType.setCurrentIndex(0)

        # offsets
        self.groupEquatorialOffsets.setVisible(isinstance(self.module, IOffsetsRaDec))
        self.groupHorizontalOffsets.setVisible(isinstance(self.module, IOffsetsAltAz))

        # fill sidebar
        if isinstance(self.module, IFilters):
            await self.add_to_sidebar(self.create_widget(FilterWidget, module=self.module))
        if isinstance(self.module, IFocuser):
            await self.add_to_sidebar(self.create_widget(FocusWidget, module=self.module))
        if isinstance(self.module, ITemperatures):
            await self.add_to_sidebar(self.create_widget(TemperaturesWidget, module=self.module))

        # init coord type
        self.select_coord_type()

    async def _init(self) -> None:
        # get variables
        if isinstance(self.module, IMotion):
            self._motion_status = await self.module.get_motion_status()
        await self._update()

    async def _update(self) -> None:
        now = Time.now()

        # get RA/Dec
        if isinstance(self.module, IPointingRaDec):
            ra, dec = await self.module.get_radec()
            self._ra_dec = SkyCoord(
                ra=ra * u.deg,
                dec=dec * u.deg,
                frame="icrs",
                location=self.observer.location,
                obstime=now,
            )
        else:
            self._ra_dec = None

        # get Alt/Az
        if isinstance(self.module, IPointingAltAz):
            alt, az = await self.module.get_altaz()
            self._alt_az = SkyCoord(
                alt=alt * u.deg,
                az=az * u.deg,
                frame="altaz",
                location=self.observer.location,
                obstime=now,
            )
        else:
            self._alt_az = None

        # get offsets
        if isinstance(self.module, IOffsetsAltAz) and self._alt_az is not None:
            # get offsets
            self._off_alt, self._off_az = await self.module.get_offsets_altaz()

            # convert to ra/dec
            self._off_ra, self._off_dec = self._offset_altaz_to_radec(self._off_alt, self._off_az)

        elif isinstance(self.module, IOffsetsRaDec) and self._ra_dec is not None:
            # get offsets
            self._off_ra, self._off_dec = await self.module.get_offsets_radec()

            # convert to alt/az
            self._off_alt, self._off_az = self._offset_radec_to_altaz(self._off_ra, self._off_dec)
        else:
            self._off_ra, self._off_dec, self._off_alt, self._off_az = (
                None,
                None,
                None,
                None,
            )

        # signal GUI update
        self.signal_update_gui.emit()

    def _offset_altaz_to_radec(self, alt: float, az: float) -> Tuple[float, float]:
        # convert to ra/dec
        p0 = self._alt_az.icrs
        p1 = self._alt_az.spherical_offsets_by(az * u.degree, alt * u.degree).icrs
        # astropy hot-fix
        p0 = SkyCoord(ra=p0.ra, dec=p0.dec, frame="icrs")
        p1 = SkyCoord(ra=p1.ra, dec=p1.dec, frame="icrs")
        # offset
        dra, ddec = p0.spherical_offsets_to(p1)
        return float(dra.degree), float(ddec.degree)

    def _offset_radec_to_altaz(self, ra: float, dec: float) -> Tuple[float, float]:
        # convert to alt/az
        altaz = AltAz(
            location=self.observer.location,
            obstime=self._ra_dec.obstime,
        )
        p0 = self._ra_dec.transform_to(altaz)
        p1 = self._ra_dec.spherical_offsets_by(ra * u.degree, dec * u.degree).transform_to(altaz)
        daz, dalt = p0.spherical_offsets_to(p1)
        return float(dalt.degree), float(daz.degree)

    def update_gui(self) -> None:
        # enable myself
        self.setEnabled(True)

        # show motion status
        self.labelStatus.setText(self._motion_status.value.upper())

        # (de)activate buttons
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

        # coordinates
        if self._ra_dec is not None:
            self.labelCurRA.setText(self._ra_dec.ra.to_string(unit=u.hour, sep=":", precision=3))
            self.labelCurDec.setText(self._ra_dec.dec.to_string(unit=u.deg, sep=":", precision=3))
        else:
            self.labelCurRA.setText("N/A")
            self.labelCurDec.setText("N/A")
        if self._alt_az is not None:
            self.labelCurAlt.setText("%.3f°" % self._alt_az.alt.degree)
            self.labelCurAz.setText("%.3f°" % self._alt_az.az.degree)
        else:
            self.labelCurAlt.setText("N/A")
            self.labelCurAz.setText("N/A")

        # offsets
        if isinstance(self.module, IOffsetsRaDec):
            self.textOffsetRA.setText("N/A" if self._off_ra is None else '%.2f"' % (self._off_ra * 3600.0,))
            self.textOffsetDec.setText("N/A" if self._off_dec is None else '%.2f"' % (self._off_dec * 3600.0,))
        if isinstance(self.module, IOffsetsAltAz):
            self.textOffsetAlt.setText("N/A" if self._off_alt is None else '%.2f"' % (self._off_alt * 3600.0,))
            self.textOffsetAz.setText("N/A" if self._off_az is None else '%.2f"' % (self._off_az * 3600.0,))

    @QtCore.pyqtSlot(name="on_buttonMove_clicked")
    def move(self) -> None:
        # get coordinate system
        text = self.comboMoveType.currentText()
        coord = COORDS(text)

        # what do we do?
        if coord == COORDS.EQUITORIAL:
            # get ra and dec
            ra = self.textMoveRA.text()
            dec = self.textMoveDec.text()
            try:
                coords = SkyCoord(ra + " " + dec, frame=ICRS, unit=(u.hour, u.deg))
            except ValueError:
                # could not create coordinates
                QtWidgets.QMessageBox.critical(self, "pyobs", "Invalid coordinates.")
                return

            # start task with move
            if isinstance(self.module, IPointingRaDec):
                self.run_background(
                    self.module.move_radec,
                    float(coords.ra.degree),
                    float(coords.dec.degree),
                )
            else:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Telescope does not support equatorial coordinates.")

        elif coord == COORDS.HORIZONTAL:
            # get alt and az
            alt = self.spinMoveAlt.value()
            az = self.spinMoveAz.value()

            # move
            if isinstance(self.module, IPointingAltAz):
                self.run_background(self.module.move_altaz, alt, az)
            else:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Telescope does not support horizontal coordinates.")

        elif coord == COORDS.HELIOGRAPHIC_STONYHURST:
            # get lat and lon
            lon = self.spinMoveHGSLon.value()
            lat = self.spinMoveHGSLat.value()

            # move
            if isinstance(self.module, IPointingHGS):
                self.run_background(self.module.move_hgs_lon_lat, lon, lat)
            else:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Telescope does not support stonyhurst coordinates.")

        elif coord == COORDS.HELIOPROJECTIVE_RADIAL:
            # get theta x/y in degrees
            theta_x = self.spinMoveHelioProjectiveRadialTx.value() / 3600.0
            theta_y = self.spinMoveHelioProjectiveRadialTy.value() / 3600.0

            # move
            if isinstance(self.module, IPointingHelioprojective):
                # run it
                self.run_background(self.module.move_helioprojective, theta_x, theta_y)

            else:
                QtWidgets.QMessageBox.critical(
                    self, "pyobs", "Telescope does not support helioprojective radial coordinates."
                )

        elif coord == COORDS.HELIOPROJECTIVE_MUPSI:
            # get mu and psi (in rad)
            mu = self.spinMoveHelioprojectiveRadialMu.value()
            psi = np.deg2rad(self.spinMoveHelioprojectiveRadialPsi.value())

            # to stonyhurst lat/lon
            alpha = np.arccos(mu)
            dsun = get_sun(Time.now()).distance  # distance earth <-> sun
            rsun = astropy.constants.R_sun  # radius of sun

            # get the angle between target and the line between earth and sun
            # from the triangle defined by the distance between earth and sun, the
            # distance between target and sun and the angle included by them
            theta = np.arctan(rsun * np.sin(alpha) / (dsun - (rsun * mu)))

            # calculate helio projective cartesian coordinates
            tx = -theta * np.sin(psi)
            ty = theta * np.cos(psi)
            heliproj = SkyCoord(tx, ty, obstime=Time.now(), frame=Helioprojective, observer="earth")

            # move
            if isinstance(self.module, IPointingHelioprojective):
                # run it
                self.run_background(self.module.move_helioprojective, heliproj.Tx.degree, heliproj.Ty.degree)

            elif isinstance(self.module, IPointingHGS):
                # alternatively, convert helio projective coordinates to Heliographic Stonyhurst
                stony = heliproj.transform_to(HeliographicStonyhurst)
                lon, lat = float(stony.lon.to(u.degree).value), float(stony.lat.to(u.degree).value)

                # run it
                self.run_background(self.module.move_hgs_lon_lat, lon, lat)
            else:
                QtWidgets.QMessageBox.critical(self, "pyobs", "Telescope does not support Mu/Psi coordinates.")

    async def _on_motion_status_changed(self, event: Event, sender: str) -> bool:
        """Called when motion status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name or not isinstance(event, MotionStatusChangedEvent):
            return False

        # store new status
        if "ITelescope" in event.interfaces:
            self._motion_status = event.interfaces["ITelescope"]
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()
        return True

    @QtCore.pyqtSlot(name="on_buttonSimbadQuery_clicked")
    def _query_simbad(self) -> None:
        """Takes the object name from the text box, queries simbad, and fills the RA/Dec inputs with the result."""
        from astroquery.simbad import Simbad

        # clear solar system and JPL Horizons
        self.comboSolarSystemBody.setCurrentText("")
        self.textJplHorizonsName.clear()

        # wait cursor
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        # query
        result = Simbad.query_object(self.textSimbadName.text())

        # restore cursor
        QtWidgets.QApplication.restoreOverrideCursor()

        # check it
        if result is None:
            QtWidgets.QMessageBox.critical(self, "Simbad", "No result found")
            return

        # always use first result
        for r in result:
            # set it
            self.textMoveRA.setText(r["RA"])
            self.textMoveDec.setText(r["DEC"])

        # update destination
        self._calc_dest_equatorial(clear=False)

    @QtCore.pyqtSlot(name="on_buttonJplHorizonsQuery_clicked")
    def _query_jpl_horizons(self) -> None:
        """Takes the object name from the text box, queries JPL Horizons, and fills the RA/Dec inputs with the result."""
        from astroquery.jplhorizons import Horizons

        # clear solar system and simbad
        self.comboSolarSystemBody.setCurrentText("")
        self.textSimbadName.clear()

        # wait cursor
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        # query
        try:
            # query
            obj = Horizons(id=self.textJplHorizonsName.text(), location=None, epochs=Time.now().jd)

            # get ephemerides
            eph = obj.ephemerides()

        except InvalidQueryError:
            QtWidgets.QMessageBox.critical(self, "JPL Horizons", "No result found")
            return
        except ValueError:
            QtWidgets.QMessageBox.critical(self, "JPL Horizons", "Invalid result")
            return
        finally:
            # restore cursor
            QtWidgets.QApplication.restoreOverrideCursor()

        # always use first result
        coord = SkyCoord(eph["RA"][0] * u.deg, eph["DEC"][0] * u.deg, frame="icrs")
        self.textMoveRA.setText(coord.ra.to_string(unit=u.hour, sep=" "))
        self.textMoveDec.setText(coord.dec.to_string(sep=" "))

        # update destination
        self._calc_dest_equatorial(clear=False)

    @QtCore.pyqtSlot(str, name="on_comboSolarSystemBody_currentTextChanged")
    def _select_solar_system(self, body: str) -> None:
        """Set RA/Dec for selected solar system body."""
        from astropy.coordinates import solar_system_ephemeris, get_body

        # nothing?
        if body == "":
            return

        # clear simbad and JPL
        self.textSimbadName.clear()
        self.textJplHorizonsName.clear()

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        with solar_system_ephemeris.set("builtin"):
            # get coordinates
            body = get_body(body, Time.now(), self.observer.location)
        QtWidgets.QApplication.restoreOverrideCursor()

        # set them
        self.textMoveRA.setText(body.ra.to_string(unit=u.hour, sep=" ", precision=2))
        self.textMoveDec.setText(body.dec.to_string(sep=" ", precision=2))

        # update destination
        self._calc_dest_equatorial(clear=False)

    @QtCore.pyqtSlot(name="on_buttonHorizonsQuery_clicked")
    def _query_horizons(self) -> None:
        """Takes the object name from the text box, queries Horizons, and fills the RA/Dec inputs with the result."""
        from astroquery.jplhorizons import Horizons

        # query
        try:
            obj = Horizons(id=self.textHorizonsName.text(), location=None, epochs=Time.now().jd)
            # result = MPC.get_ephemeris(, location=self.observer.location)
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
        return

        # to coordinates
        coord = SkyCoord.guess_from_table(result)[0]

        # set it
        self.textTrackRA.setText(coord.ra.to_string(u.hour, sep=":"))
        self.textTrackDec.setText(coord.dec.to_string(sep=":"))

    def _show_dest_coords(self, ra: str = "N/A", dec: str = "N/A", alt: str = "N/A", az: str = "N/A") -> None:
        self.textDestRA.setText(ra if isinstance(ra, str) else ra.to_string(u.hour, sep=":"))
        self.textDestDec.setText(dec if isinstance(dec, str) else dec.to_string(sep=":"))
        self.textDestAlt.setText(alt if isinstance(alt, str) else "%.2f°" % alt.degree)
        self.textDestAz.setText(az if isinstance(az, str) else "%.2f°" % az.degree)

    @QtCore.pyqtSlot(name="on_spinMoveAlt_editingFinished")
    @QtCore.pyqtSlot(name="on_spinMoveAz_editingFinished")
    def _calc_dest_horizontal(self) -> None:
        """Called, whenever Alt/Az input changes. Calculates destination."""

        # create SkyCoord
        alt_az = SkyCoord(
            alt=self.spinMoveAlt.value() * u.deg,
            az=self.spinMoveAz.value() * u.deg,
            frame=AltAz,
            location=self.observer.location,
            obstime=Time.now(),
        )

        # to ra/dec
        ra_dec = alt_az.icrs

        # display
        self._show_dest_coords(ra_dec.ra, ra_dec.dec, alt_az.alt, alt_az.az)

    @QtCore.pyqtSlot(name="on_textMoveRA_editingFinished")
    @QtCore.pyqtSlot(name="on_textMoveDec_editingFinished")
    def _calc_dest_equatorial(self, clear: bool = True) -> None:
        """Called, whenever RA/Dec input changes. Calculates destination."""

        # reset fields
        if clear:
            self.textSimbadName.clear()
            self.comboSolarSystemBody.setCurrentText("")
            self.textJplHorizonsName.clear()

        # parse RA/Dec
        try:
            ra_dec = SkyCoord(
                self.textMoveRA.text() + " " + self.textMoveDec.text(),
                frame=ICRS,
                unit=(u.hour, u.deg),
            )
        except ValueError:
            # on error, show it
            self._show_dest_coords()
            return

        # to alt/az
        alt_az = self.observer.altaz(Time.now(), ra_dec)

        # display
        self._show_dest_coords(ra_dec.ra, ra_dec.dec, alt_az.alt, alt_az.az)

    @QtCore.pyqtSlot(name="on_spinMoveHGSLat_valueChanged")
    @QtCore.pyqtSlot(name="on_spinMoveHGSLat_valueChanged")
    def _calc_dest_heliographic_stonyhurst(self) -> None:
        # get sun
        sun = self.observer.sun_altaz(Time.now())
        sun_radec = sun.icrs

        # display
        self._show_dest_coords(sun_radec.ra, sun_radec.dec, sun.alt, sun.az)

    @QtCore.pyqtSlot(name="on_spinMoveHelioprojectiveRadialMu_valueChanged")
    @QtCore.pyqtSlot(name="on_spinMoveHelioprojectiveRadialPsi_valueChanged")
    def _calc_dest_helioprojective_radial(self) -> None:
        # get sun
        sun = self.observer.sun_altaz(Time.now())
        sun_radec = sun.icrs

        # display
        self._show_dest_coords(sun_radec.ra, sun_radec.dec, sun.alt, sun.az)

    def _calc_dest_orbit_elements(self) -> None:
        pass

    @QtCore.pyqtSlot(int, name="on_comboMoveType_currentIndexChanged")
    def select_coord_type(self) -> None:
        # get coordinate system
        text = self.comboMoveType.currentText()
        try:
            coord = COORDS(text)
        except ValueError:
            # just ignore it
            return

        # set page and visibility
        self.stackedMove.setCurrentWidget(self._MOVE_WIDGETS[coord])
        self._DEST_CALC[coord]()

    @QtCore.pyqtSlot(name="on_buttonInit_clicked")
    def _init_telescope(self) -> None:
        if isinstance(self.module, IMotion):
            self.run_background(self.module.init)

    @QtCore.pyqtSlot(name="on_buttonPark_clicked")
    def _park_telescope(self) -> None:
        if isinstance(self.module, IMotion):
            self.run_background(self.module.park)

    @QtCore.pyqtSlot(name="on_buttonStop_clicked")
    def _stop_telescope(self) -> None:
        if isinstance(self.module, IMotion):
            self.run_background(lambda: self.module.stop_motion("ITelescope"))

    @QtCore.pyqtSlot(name="on_buttonSetAltOffset_clicked")
    @QtCore.pyqtSlot(name="on_buttonSetAzOffset_clicked")
    @QtCore.pyqtSlot(name="on_buttonSetRaOffset_clicked")
    @QtCore.pyqtSlot(name="on_buttonSetDecOffset_clicked")
    @QtCore.pyqtSlot(name="on_buttonResetHorizontalOffsets_clicked")
    @QtCore.pyqtSlot(name="on_buttonResetEquatorialOffsets_clicked")
    def _set_offset(self) -> None:
        """Asks user for new offsets and sets it."""

        # first all the reset buttons
        if self.sender() == self.buttonResetHorizontalOffsets:
            self.run_background(self.module.set_offsets_altaz, 0.0, 0)
        elif self.sender() == self.buttonResetEquatorialOffsets:
            self.run_background(self.module.set_offsets_radec, 0, 0.0)
        else:
            # now the sets, ask for value
            new_value, ok = QtWidgets.QInputDialog.getDouble(self, "Set offset", 'New offset ["]', 0, -9999, 9999)
            if ok:
                if self.sender() == self.buttonSetAltOffset:
                    self.run_background(self.module.set_offsets_altaz, new_value / 3600.0, self._off_az)
                elif self.sender() == self.buttonSetAzOffset:
                    self.run_background(self.module.set_offsets_altaz, self._off_alt, new_value / 3600.0)
                elif self.sender() == self.buttonSetRaOffset:
                    self.run_background(self.module.set_offsets_radec, new_value / 3600.0, self._off_dec)
                elif self.sender() == self.buttonSetDecOffset:
                    self.run_background(self.module.set_offsets_radec, self._off_ra, new_value / 3600.0)
