import asyncio
from enum import Enum

import numpy as np
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5 import QtWidgets, QtCore
from astropy.coordinates import SkyCoord, ICRS, AltAz, get_sun
import astropy.units as u
import logging
from astroquery.exceptions import InvalidQueryError
import astropy.constants

from pyobs.events import MotionStatusChangedEvent, Event
from pyobs.interfaces import IPointingRaDec, IPointingAltAz, IPointingHGS, IOffsetsRaDec, \
    IOffsetsAltAz, IFilters, IFocuser, ITemperatures
from pyobs.utils.enums import MotionStatus
from pyobs.utils.time import Time
from pyobs_gui.widgetfilter import WidgetFilter
from pyobs_gui.widgetfocus import WidgetFocus
from pyobs_gui.widgettemperatures import WidgetTemperatures
from .qt.widgettelescope import Ui_WidgetTelescope
from .basewidget import BaseWidget


log = logging.getLogger(__name__)


class COORDS(Enum):
    EQUITORIAL = 'Equitorial'
    HORIZONTAL = 'Horizontal'
    ORBIT_ELEMENTS = 'Orbit Elements'
    HELIOGRAPHIC_STONYHURST = 'Heliographic Stonyhurst'
    HELIOPROJECTIVE_RADIAL = 'Helioprojective Radial'


class WidgetTelescope(BaseWidget, Ui_WidgetTelescope):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs):
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
            COORDS.ORBIT_ELEMENTS: self.pageMoveOrbitElements
        }

        # calculate dest coordinates
        self._DEST_CALC = {
            COORDS.EQUITORIAL: self._calc_dest_equatorial,
            COORDS.HORIZONTAL: self._calc_dest_horizontal,
            COORDS.HELIOGRAPHIC_STONYHURST: self._calc_dest_heliographic_stonyhurst,
            COORDS.HELIOPROJECTIVE_RADIAL: self._calc_dest_helioprojective_radial,
            COORDS.ORBIT_ELEMENTS: self._calc_dest_orbit_elements
        }

        # add coord types
        if isinstance(self.module, IPointingRaDec):
            self.comboMoveType.addItem(COORDS.EQUITORIAL.value)
            #self.comboMoveType.addItem(COORDS.ORBIT_ELEMENTS.value)
        if isinstance(self.module, IPointingAltAz):
            self.comboMoveType.addItem(COORDS.HORIZONTAL.value)
        if isinstance(self.module, IPointingHGS):
            self.comboMoveType.addItem(COORDS.HELIOGRAPHIC_STONYHURST.value)
            self.comboMoveType.addItem(COORDS.HELIOPROJECTIVE_RADIAL.value)
        if self.comboMoveType.count() > 0:
            self.comboMoveType.setCurrentIndex(0)

        # offsets
        self.groupEquatorialOffsets.setVisible(isinstance(self.module, IOffsetsRaDec))
        self.groupHorizontalOffsets.setVisible(isinstance(self.module, IOffsetsAltAz))

        # plot
        #self.figure = plt.figure()
        #self.plot = VisPlot(self.figure, self.environment)
        #self.canvas = FigureCanvas(self.figure)
        #self.widgetPlot.setLayout(QtWidgets.QVBoxLayout())
        #self.widgetPlot.layout().addWidget(self.canvas)
        #self.first = True

        # button colors
        self.colorize_button(self.buttonInit, QtCore.Qt.green)
        self.colorize_button(self.buttonPark, QtCore.Qt.yellow)
        self.colorize_button(self.buttonStop, QtCore.Qt.red)
        self.colorize_button(self.buttonMove, QtCore.Qt.blue)
        self.colorize_button(self.buttonOffsetEast, QtCore.Qt.blue)
        self.colorize_button(self.buttonOffsetNorth, QtCore.Qt.blue)
        self.colorize_button(self.buttonOffsetSouth, QtCore.Qt.blue)
        self.colorize_button(self.buttonOffsetWest, QtCore.Qt.blue)
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

    async def open(self):
        """Open widget."""
        await BaseWidget.open(self)

        # subscribe to events
        await self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

        # fill sidebar
        if isinstance(self.module, IFilters):
            self.add_to_sidebar(self.create_widget(WidgetFilter, module=self.module))
        if isinstance(self.module, IFocuser):
            self.add_to_sidebar(self.create_widget(WidgetFocus, module=self.module))
        if isinstance(self.module, ITemperatures):
            self.add_to_sidebar(self.create_widget(WidgetTemperatures, module=self.module))

        # init coord type
        self.select_coord_type()

    async def _init(self):
        # get variables
        self._motion_status = await self.module.get_motion_status()
        await self._update()

    async def _update(self):
        now = Time.now()

        # get RA/Dec
        try:
            ra, dec = await self.module.get_radec()
            self._ra_dec = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs',
                                    location=self.observer.location, obstime=now)
        except:
            self._ra_dec = None

        # get Alt/Az
        try:
            alt, az = await self.module.get_altaz()
            self._alt_az = SkyCoord(alt=alt * u.deg, az=az * u.deg, frame='altaz',
                                    location=self.observer.location, obstime=now)
        except:
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
            self._off_ra, self._off_dec, self._off_alt, self._off_az = None, None, None, None

        # signal GUI update
        self.signal_update_gui.emit()

    def _offset_altaz_to_radec(self, alt, az):
        # convert to ra/dec
        p0 = self._alt_az.icrs
        p1 = SkyCoord(alt=(self._alt_az.alt.degree + alt) * u.deg,
                      az=(self._alt_az.az.degree + az) * u.deg, frame='altaz',
                      location=self.observer.location, obstime=self._alt_az.obstime).icrs
        return float(p1.ra.degree - p0.ra.degree), float(p1.dec.degree - p0.dec.degree)

    def _offset_radec_to_altaz(self, ra, dec):
        # convert to alt/az
        p0 = self._ra_dec.transform_to(AltAz)
        p1 = SkyCoord(ra=(self._ra_dec.ra.degree + ra) * u.deg,
                      dec=(self._ra_dec.dec.degree + dec) * u.deg, frame='icrs',
                      location=self.observer.location, obstime=self._ra_dec.obstime).transform_to(AltAz)
        return float(p1.alt.degree - p0.alt.degree), float(p1.az.degree - p0.az.degree)

    def update_gui(self):
        # enable myself
        self.setEnabled(True)

        # show motion status
        self.labelStatus.setText(self._motion_status.value.upper())

        # (de)activate buttons
        self.buttonInit.setEnabled(self._motion_status == MotionStatus.PARKED)
        self.buttonPark.setEnabled(self._motion_status not in [MotionStatus.PARKED, MotionStatus.ERROR,
                                                               MotionStatus.PARKING, MotionStatus.INITIALIZING])
        self.buttonStop.setEnabled(self._motion_status in [MotionStatus.SLEWING, MotionStatus.TRACKING])
        initialized = self._motion_status in [MotionStatus.SLEWING, MotionStatus.TRACKING,
                                              MotionStatus.IDLE, MotionStatus.POSITIONED]
        self.buttonMove.setEnabled(initialized)
        self.buttonOffsetNorth.setEnabled(initialized)
        self.buttonOffsetSouth.setEnabled(initialized)
        self.buttonOffsetEast.setEnabled(initialized)
        self.buttonOffsetWest.setEnabled(initialized)
        self.buttonSetAltOffset.setEnabled(initialized)
        self.buttonSetAzOffset.setEnabled(initialized)
        self.buttonSetRaOffset.setEnabled(initialized)
        self.buttonSetDecOffset.setEnabled(initialized)
        self.buttonResetHorizontalOffsets.setEnabled(initialized)
        self.buttonResetEquatorialOffsets.setEnabled(initialized)

        # coordinates
        if self._ra_dec is not None:
            self.labelCurRA.setText(self._ra_dec.ra.to_string(unit=u.hour, sep=':', precision=3))
            self.labelCurDec.setText(self._ra_dec.dec.to_string(unit=u.deg, sep=':', precision=3))
        else:
            self.labelCurRA.setText('N/A')
            self.labelCurDec.setText('N/A')
        if self._alt_az is not None:
            self.labelCurAlt.setText('%.3f°' % self._alt_az.alt.degree)
            self.labelCurAz.setText('%.3f°' % self._alt_az.az.degree)
        else:
            self.labelCurAlt.setText('N/A')
            self.labelCurAz.setText('N/A')

        # offsets
        if isinstance(self.module, IOffsetsRaDec):
            self.textOffsetRA.setText('N/A' if self._off_ra is None else '%.2f"' % (self._off_ra * 3600.,))
            self.textOffsetDec.setText('N/A' if self._off_dec is None else '%.2f"' % (self._off_dec * 3600.,))
        if isinstance(self.module, IOffsetsAltAz):
            self.textOffsetAlt.setText('N/A' if self._off_alt is None else '%.2f"' % (self._off_alt * 3600.,))
            self.textOffsetAz.setText('N/A' if self._off_az is None else '%.2f"' % (self._off_az * 3600.,))

    @pyqtSlot(name='on_buttonMove_clicked')
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
                coords = SkyCoord(ra + ' ' + dec, frame=ICRS, unit=(u.hour, u.deg))
            except ValueError:
                # could not create coordinates
                QtWidgets.QMessageBox.critical(self, 'pyobs', 'Invalid coordinates.')
                return

            # start thread with move
            if isinstance(self.module, IPointingRaDec):
                self.run_background(self.module.move_radec, float(coords.ra.degree), float(coords.dec.degree))
            else:
                QtWidgets.QMessageBox.critical(self, 'pyobs', 'Telescope does not support equatorial coordinates.')

        elif coord == COORDS.HORIZONTAL:
            # get alt and az
            alt = self.spinMoveAlt.value()
            az = self.spinMoveAz.value()

            # move
            if isinstance(self.module, IPointingAltAz):
                self.run_background(self.module.move_altaz, alt, az)
            else:
                QtWidgets.QMessageBox.critical(self, 'pyobs', 'Telescope does not support horizontal coordinates.')

        elif coord == COORDS.HELIOGRAPHIC_STONYHURST:
            # get lat and lon
            lon = self.spinMoveHGSLon.value()
            lat = self.spinMoveHGSLat.value()

            # move
            if isinstance(self.module, IPointingHGS):
                self.run_background(self.module.move_hgs_lon_lat, lon, lat)
            else:
                QtWidgets.QMessageBox.critical(self, 'pyobs', 'Telescope does not support stonyhurst coordinates.')

        elif coord == COORDS.HELIOPROJECTIVE_RADIAL:
            # get mu and psi
            mu = self.spinMoveHelioprojectiveRadialMu.value()
            psi = self.spinMoveHelioprojectiveRadialPsi.value()

            # to stonyhurst lat/lon
            alpha = np.arccos(mu)
            dsun = get_sun(Time.now()).distance  # distance earth <-> sun
            rsun = astropy.constants.R_sun  # radius of sun

            # get the angle between target and the line between earth and sun
            # from the triangle defined by the distance between earth and sun, the
            # distance between target and sun and the angle included by them
            theta = np.arctan(rsun * np.sin(alpha) / (dsun - (rsun * mu)))

            # calculate helio projective cartesian coordinates
            lon = float((-theta * np.sin(psi)).value)
            lat = float((theta * np.cos(psi)).value)

            # move
            if isinstance(self.module, IPointingHGS):
                self.run_background(self.module.move_hgs_lon_lat, lon, lat)
            else:
                QtWidgets.QMessageBox.critical(self, 'pyobs', 'Telescope does not support stonyhurst coordinates.')

    async def _on_motion_status_changed(self, event: Event, sender: str):
        """Called when motion status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name or not isinstance(event, MotionStatusChangedEvent):
            return False

        # store new status
        if 'ITelescope' in event.interfaces:
            self._motion_status = event.interfaces['ITelescope']
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()
        return True

    @pyqtSlot(name='on_buttonSimbadQuery_clicked')
    def _query_simbad(self):
        """Takes the object name from the text box, queries simbad, and fills the RA/Dec inputs with the result."""
        from astroquery.simbad import Simbad

        # clear solar system and JPL Horizons
        self.comboSolarSystemBody.setCurrentText('')
        self.textJplHorizonsName.clear()

        # wait cursor
        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)

        # query
        result = Simbad.query_object(self.textSimbadName.text())

        # restore cursor
        QtWidgets.QApplication.restoreOverrideCursor()

        # check it
        if result is None:
            QtWidgets.QMessageBox.critical(self, 'Simbad', 'No result found')
            return

        # always use first result
        for r in result:
            # set it
            self.textMoveRA.setText(r['RA'])
            self.textMoveDec.setText(r['DEC'])

        # update destination
        self._calc_dest_equatorial(clear=False)

    @pyqtSlot(name='on_buttonJplHorizonsQuery_clicked')
    def _query_jpl_horizons(self):
        """Takes the object name from the text box, queries JPL Horizons, and fills the RA/Dec inputs with the result."""
        from astroquery.jplhorizons import Horizons

        # clear solar system and simbad
        self.comboSolarSystemBody.setCurrentText('')
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
            QtWidgets.QMessageBox.critical(self, 'JPL Horizons', 'No result found')
            return
        except ValueError:
            QtWidgets.QMessageBox.critical(self, 'JPL Horizons', 'Invalid result')
            return
        finally:
            # restore cursor
            QtWidgets.QApplication.restoreOverrideCursor()

        # always use first result
        coord = SkyCoord(eph['RA'][0] * u.deg, eph['DEC'][0] * u.deg, frame='icrs')
        self.textMoveRA.setText(coord.ra.to_string(unit=u.hour, sep=' '))
        self.textMoveDec.setText(coord.dec.to_string(sep=' '))

        # update destination
        self._calc_dest_equatorial(clear=False)

    @pyqtSlot(str, name='on_comboSolarSystemBody_currentTextChanged')
    def _select_solar_system(self, body: str):
        """Set RA/Dec for selected solar system body."""
        from astropy.coordinates import solar_system_ephemeris, get_body

        # nothing?
        if body == '':
            return

        # clear simbad and JPL
        self.textSimbadName.clear()
        self.textJplHorizonsName.clear()

        QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
        with solar_system_ephemeris.set('builtin'):
            # get coordinates
            body = get_body(body, Time.now(), self.observer.location)
        QtWidgets.QApplication.restoreOverrideCursor()

        # set them
        self.textMoveRA.setText(body.ra.to_string(unit=u.hour, sep=' ', precision=2))
        self.textMoveDec.setText(body.dec.to_string(sep=' ', precision=2))

        # update destination
        self._calc_dest_equatorial(clear=False)

    @pyqtSlot(name='on_buttonHorizonsQuery_clicked')
    def _query_horizons(self):
        """Takes the object name from the text box, queries Horizons, and fills the RA/Dec inputs with the result."""
        from astroquery.jplhorizons import Horizons

        # query
        try:
            obj = Horizons(id=self.textHorizonsName.text(), location=None, epochs=Time.now().jd)
            #result = MPC.get_ephemeris(, location=self.observer.location)
        except InvalidQueryError:
            QtWidgets.QMessageBox.critical(self, 'MPC', 'No result found')
            return

        print(obj)
        print(obj.uri)
        try:
            eph = obj.elements()
        except ValueError:
            pass
        print(eph)
        print(eph.columns)
        print(obj.uri)

        self.spinOrbitElementsEcc.setValue(eph['e'][0])
        self.spinOrbitElementsIncl.setValue(eph['incl'][0])
        self.spinOrbitElementsSemiMajorAxis.setValue(eph['a'][0])
        self.spinOrbitElementsMA.setValue(eph['M'][0])
        self.spinOrbitElementsOmega.setValue(eph['Omega'][0])
        self.spinOrbitElementsPerifocus.setValue(eph['w'][0])
        self.spinOrbitElementsEpoch.setValue(eph['datetime_jd'][0])
        return

        # to coordinates
        coord = SkyCoord.guess_from_table(result)[0]

        # set it
        self.textTrackRA.setText(coord.ra.to_string(u.hour, sep=':'))
        self.textTrackDec.setText(coord.dec.to_string(sep=':'))

    def _show_dest_coords(self, ra: str = 'N/A', dec: str = 'N/A', alt: str = 'N/A', az: str = 'N/A'):
        self.textDestRA.setText(ra if isinstance(ra, str) else ra.to_string(u.hour, sep=':'))
        self.textDestDec.setText(dec if isinstance(dec, str) else dec.to_string(sep=':'))
        self.textDestAlt.setText(alt if isinstance(alt, str) else '%.2f°' % alt.degree)
        self.textDestAz.setText(az if isinstance(az, str) else '%.2f°' % az.degree)

    @pyqtSlot(name='on_spinMoveAlt_editingFinished')
    @pyqtSlot(name='on_spinMoveAz_editingFinished')
    def _calc_dest_horizontal(self):
        """Called, whenever Alt/Az input changes. Calculates destination."""

        # create SkyCoord
        alt_az = SkyCoord(alt=self.spinMoveAlt.value() * u.deg, az=self.spinMoveAz.value() * u.deg, frame=AltAz,
                          location=self.observer.location, obstime=Time.now())

        # to ra/dec
        ra_dec = alt_az.icrs

        # display
        self._show_dest_coords(ra_dec.ra, ra_dec.dec, alt_az.alt, alt_az.az)

    @pyqtSlot(name='on_textMoveRA_editingFinished')
    @pyqtSlot(name='on_textMoveDec_editingFinished')
    def _calc_dest_equatorial(self, clear: bool = True):
        """Called, whenever RA/Dec input changes. Calculates destination."""

        # reset fields
        if clear:
            self.textSimbadName.clear()
            self.comboSolarSystemBody.setCurrentText('')
            self.textJplHorizonsName.clear()

        # parse RA/Dec
        try:
            ra_dec = SkyCoord(self.textMoveRA.text() + ' ' + self.textMoveDec.text(),
                              frame=ICRS, unit=(u.hour, u.deg))
        except ValueError:
            # on error, show it
            self._show_dest_coords()
            return

        # to alt/az
        alt_az = self.observer.altaz(Time.now(), ra_dec)

        # display
        self._show_dest_coords(ra_dec.ra, ra_dec.dec, alt_az.alt, alt_az.az)

    @pyqtSlot(name='on_spinMoveHGSLat_valueChanged')
    @pyqtSlot(name='on_spinMoveHGSLat_valueChanged')
    def _calc_dest_heliographic_stonyhurst(self):
        # get sun
        sun = self.observer.sun_altaz(Time.now())
        sun_radec = sun.icrs

        # display
        self._show_dest_coords(sun_radec.ra, sun_radec.dec, sun.alt, sun.az)

    @pyqtSlot(name='on_spinMoveHelioprojectiveRadialMu_valueChanged')
    @pyqtSlot(name='on_spinMoveHelioprojectiveRadialPsi_valueChanged')
    def _calc_dest_helioprojective_radial(self):
        # get sun
        sun = self.observer.sun_altaz(Time.now())
        sun_radec = sun.icrs

        # display
        self._show_dest_coords(sun_radec.ra, sun_radec.dec, sun.alt, sun.az)

    def _calc_dest_orbit_elements(self):
        pass

    @pyqtSlot(int, name='on_comboMoveType_currentIndexChanged')
    def select_coord_type(self):
        # get coordinate system
        text = self.comboMoveType.currentText()
        coord = COORDS(text)

        # set page and visibility
        self.stackedMove.setCurrentWidget(self._MOVE_WIDGETS[coord])
        self._DEST_CALC[coord]()

    @pyqtSlot(name='on_buttonInit_clicked')
    def _init_telescope(self):
        self.run_background(self.module.init)

    @pyqtSlot(name='on_buttonPark_clicked')
    def _park_telescope(self):
        self.run_background(self.module.park)

    @pyqtSlot(name='on_buttonStop_clicked')
    def _stop_telescope(self):
        self.run_background(lambda: self.module.stop_motion('ITelescope'))

    @pyqtSlot(name='on_buttonSetAltOffset_clicked')
    @pyqtSlot(name='on_buttonSetAzOffset_clicked')
    @pyqtSlot(name='on_buttonSetRaOffset_clicked')
    @pyqtSlot(name='on_buttonSetDecOffset_clicked')
    @pyqtSlot(name='on_buttonResetHorizontalOffsets_clicked')
    @pyqtSlot(name='on_buttonResetEquatorialOffsets_clicked')
    def _set_offset(self):
        """Asks user for new offsets and sets it."""

        # first all the reset buttons
        if self.sender() == self.buttonResetHorizontalOffsets:
            self.run_background(self.module.set_offsets_altaz, 0., 0)
        elif self.sender() == self.buttonResetEquatorialOffsets:
            self.run_background(self.module.set_offsets_radec, 0, 0.)
        else:
            # now the sets, ask for value
            new_value, ok = QtWidgets.QInputDialog.getDouble(self, 'Set offset', 'New offset ["]', 0, -9999, 9999)
            if ok:
                if self.sender() == self.buttonSetAltOffset:
                    self.run_background(self.module.set_offsets_altaz, new_value / 3600., self._off_az)
                elif self.sender() == self.buttonSetAzOffset:
                    self.run_background(self.module.set_offsets_altaz, self._off_alt, new_value / 3600.)
                elif self.sender() == self.buttonSetRaOffset:
                    self.run_background(self.module.set_offsets_radec, new_value / 3600., self._off_dec)
                elif self.sender() == self.buttonSetDecOffset:
                    self.run_background(self.module.set_offsets_radec, self._off_ra, new_value / 3600.)

    @pyqtSlot(name='on_buttonOffsetNorth_clicked')
    @pyqtSlot(name='on_buttonOffsetSouth_clicked')
    @pyqtSlot(name='on_buttonOffsetEast_clicked')
    @pyqtSlot(name='on_buttonOffsetWest_clicked')
    def _move_offset(self):
        # get current offsets
        off_ra, off_dec = self._off_ra, self._off_dec

        # new offset
        user_offset = self.spinOffset.value() / 3600.

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
        if isinstance(self.module, IOffsetsRaDec):
            self.run_background(self.module.set_offsets_radec, off_ra, off_dec)
        elif isinstance(self.module, IOffsetsAltAz):
            off_alt, off_az = self._offset_radec_to_altaz(off_ra, off_dec)
            self.run_background(self.module.set_offsets_altaz, off_alt, off_az)
        else:
            raise ValueError
