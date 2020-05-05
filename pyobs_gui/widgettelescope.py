import threading

import astroquery
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5 import QtWidgets, QtCore, QtGui
from astroplan import Observer
from astropy.coordinates import SkyCoord, ICRS, AltAz
import astropy.units as u
import logging

from astroquery.exceptions import InvalidQueryError
from astroquery.simbad import Simbad
from astroquery.mpc import MPC

from pyobs.comm import Comm
from pyobs.events import MotionStatusChangedEvent
from pyobs.interfaces import ITelescope, IFilters, IFocuser, ITemperatures, IMotion, IAltAzOffsets, IRaDecOffsets
from pyobs.utils.time import Time
from pyobs_gui.widgetfilter import WidgetFilter
from pyobs_gui.widgetfocus import WidgetFocus
from pyobs_gui.widgettemperatures import WidgetTemperatures
from .qt.widgettelescope import Ui_WidgetTelescope
from .basewidget import BaseWidget


log = logging.getLogger(__name__)


class WidgetTelescope(BaseWidget, Ui_WidgetTelescope):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, observer, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update)
        self.setupUi(self)
        self.module = module    # type: (ITelescope, IFilters, IFocuser)
        self.comm = comm  # type: Comm
        self.observer = observer  # type: Observer

        # variables
        self._motion_status = IMotion.Status.UNKNOWN
        self._ra_dec = None
        self._alt_az = None
        self._off_ra = None
        self._off_dec = None
        self._off_alt = None
        self._off_az = None

        # before first update, disable mys
        self.setEnabled(False)

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
        self.colorize_button(self.buttonResetAltOffset, QtCore.Qt.yellow)
        self.colorize_button(self.buttonResetAzOffset, QtCore.Qt.yellow)
        self.colorize_button(self.buttonResetRaOffset, QtCore.Qt.yellow)
        self.colorize_button(self.buttonResetDecOffset, QtCore.Qt.yellow)
        self.colorize_button(self.buttonSimbadQuery, QtCore.Qt.green)
        self.colorize_button(self.buttonMpcQuery, QtCore.Qt.green)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

        # subscribe to events
        self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

        # fill sidebar
        if isinstance(self.module, IFilters):
            self.add_to_sidebar(WidgetFilter(module, comm))
        if isinstance(self.module, IFocuser):
            self.add_to_sidebar(WidgetFocus(module, comm))
        if isinstance(self.module, ITemperatures):
            self.add_to_sidebar(WidgetTemperatures(module, comm))

        # init coord type
        self.select_coord_type()

    def _init(self):
        # get variables
        self._motion_status = self.module.get_motion_status().wait()
        self._update()

    def _update(self):
        now = Time.now()
        
        # get RA/Dec
        try:
            ra, dec = self.module.get_radec().wait()
            self._ra_dec = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs',
                                    location=self.observer.location, obstime=now)
        except:
            self._ra_dec = None

        # get Alt/Az
        try:
            alt, az = self.module.get_altaz().wait()
            self._alt_az = SkyCoord(alt=alt * u.deg, az=az * u.deg, frame='altaz',
                                    location=self.observer.location, obstime=now)
        except:
            self._alt_az = None

        # get offsets
        self._off_ra, self._off_dec, self._off_alt, self._off_az = None, None, None, None
        if isinstance(self.module, IAltAzOffsets) and self._alt_az is not None:
            # get offsets
            self._off_alt, self._off_az = self.module.get_altaz_offsets().wait()

            # convert to ra/dec
            self._off_ra, self._off_dec = self._offset_altaz_to_radec(self._off_alt, self._off_az)

        elif isinstance(self.module, IRaDecOffsets) and self._ra_dec is not None:
            # get offsets
            self._off_ra, self._off_dec = self.module.get_radec_offsets().wait()

            # convert to alt/az
            self._off_alt, self._off_az = self._offset_radec_to_altaz(self._off_ra, self._off_dec)

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
        self.buttonInit.setEnabled(self._motion_status == IMotion.Status.PARKED)
        self.buttonPark.setEnabled(self._motion_status not in [IMotion.Status.PARKED, IMotion.Status.ERROR,
                                                               IMotion.Status.PARKING, IMotion.Status.INITIALIZING])
        self.buttonStop.setEnabled(self._motion_status in [IMotion.Status.SLEWING, IMotion.Status.TRACKING])
        initialized = self._motion_status in [IMotion.Status.SLEWING, IMotion.Status.TRACKING,
                                              IMotion.Status.IDLE, IMotion.Status.POSITIONED]
        self.buttonMove.setEnabled(initialized)
        self.buttonOffsetNorth.setEnabled(initialized)
        self.buttonOffsetSouth.setEnabled(initialized)
        self.buttonOffsetEast.setEnabled(initialized)
        self.buttonOffsetWest.setEnabled(initialized)
        self.buttonSetAltOffset.setEnabled(initialized)
        self.buttonSetAzOffset.setEnabled(initialized)
        self.buttonSetRaOffset.setEnabled(initialized)
        self.buttonSetDecOffset.setEnabled(initialized)
        self.buttonResetAltOffset.setEnabled(initialized)
        self.buttonResetAzOffset.setEnabled(initialized)
        self.buttonResetRaOffset.setEnabled(initialized)
        self.buttonResetDecOffset.setEnabled(initialized)

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
        self.textOffsetRA.setText('N/A' if self._off_ra is None else '%.2f"' % (self._off_ra * 3600.,))
        self.textOffsetDec.setText('N/A' if self._off_dec is None else '%.2f"' % (self._off_dec * 3600.,))
        self.textOffsetAlt.setText('N/A' if self._off_alt is None else '%.2f"' % (self._off_alt * 3600.,))
        self.textOffsetAz.setText('N/A' if self._off_az is None else '%.2f"' % (self._off_az * 3600.,))
        radec_enabled = isinstance(self.module, IRaDecOffsets)
        self.buttonSetRaOffset.setVisible(radec_enabled)
        self.buttonSetDecOffset.setVisible(radec_enabled)
        self.buttonResetRaOffset.setVisible(radec_enabled)
        self.buttonResetDecOffset.setVisible(radec_enabled)
        altaz_enabled = isinstance(self.module, IAltAzOffsets)
        self.buttonSetAltOffset.setVisible(altaz_enabled)
        self.buttonSetAzOffset.setVisible(altaz_enabled)
        self.buttonResetAltOffset.setVisible(altaz_enabled)
        self.buttonResetAzOffset.setVisible(altaz_enabled)

    @pyqtSlot(name='on_buttonMove_clicked')
    def move(self):
        # coordinate type
        coord_type = self.comboMoveType.currentIndex()

        # what do we do?
        if coord_type == 0:
            # get ra and dec
            ra = self.textMoveRA.text()
            dec = self.textMoveDec.text()
            coords = SkyCoord(ra + ' ' + dec, frame=ICRS, unit=(u.hour, u.deg))

            # start thread with move
            self.run_async(self.module.move_radec, float(coords.ra.degree), float(coords.dec.degree))

        elif coord_type == 1:
            # get alt and az
            alt = self.spinMoveAlt.value()
            az = self.spinMoveAz.value()

            # move
            self.run_async(self.module.move_altaz, alt, az)

    def _on_motion_status_changed(self, event: MotionStatusChangedEvent, sender: str):
        """Called when motion status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # ignore events from wrong sender
        if sender != self.module.name:
            return

        # store new status
        if 'ITelescope' in event.interfaces:
            self._motion_status = event.interfaces['ITelescope']
        else:
            self._motion_status = event.status

        # trigger GUI update
        self.signal_update_gui.emit()

    @pyqtSlot(name='on_buttonSimbadQuery_clicked')
    def _query_simbad(self):
        """Takes the object name from the text box, queries simbad, and fills the RA/Dec inputs with the result."""

        # query
        result = Simbad.query_object(self.textSimbadName.text())

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
        self._calc_dest_equatorial()

    @pyqtSlot(name='on_buttonMpcQuery_clicked')
    def _query_mpc(self):
        """Takes the object name from the text box, queries Horizons, and fills the RA/Dec inputs with the result."""

        # query
        try:
            result = MPC.get_ephemeris(self.textMpcName.text(), location=self.observer.location)
        except InvalidQueryError:
            QtWidgets.QMessageBox.critical(self, 'MPC', 'No result found')
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
    def _calc_dest_equatorial(self):
        """Called, whenever RA/Dec input changes. Calculates destination."""

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

    @pyqtSlot(int, name='on_comboMoveType_currentIndexChanged')
    def select_coord_type(self):
        # get index
        idx = self.comboMoveType.currentIndex()

        # pages
        pages = {
            0: self.pageMoveEquatorial,
            1: self.pageMoveHorizontal,
            2: self.pageMoveSolarSystem
        }

        # destination coordinates?
        coords = {
            0: self._calc_dest_equatorial,
            1: self._calc_dest_horizontal,
            2: self._calc_dest_equatorial
        }

        # set page and visibility
        self.stackedMove.setCurrentWidget(pages[idx])
        coords[idx]()

    @pyqtSlot(name='on_buttonInit_clicked')
    def _init_telescope(self):
        self.run_async(self.module.init)

    @pyqtSlot(name='on_buttonPark_clicked')
    def _park_telescope(self):
        self.run_async(self.module.park)

    @pyqtSlot(name='on_buttonStop_clicked')
    def _stop_telescope(self):
        self.run_async(lambda: self.module.stop_motion('ITelescope'))

    @pyqtSlot(name='on_buttonSetAltOffset_clicked')
    @pyqtSlot(name='on_buttonResetAltOffset_clicked')
    @pyqtSlot(name='on_buttonSetAzOffset_clicked')
    @pyqtSlot(name='on_buttonResetAzOffset_clicked')
    @pyqtSlot(name='on_buttonSetRaOffset_clicked')
    @pyqtSlot(name='on_buttonResetRaOffset_clicked')
    @pyqtSlot(name='on_buttonSetDecOffset_clicked')
    @pyqtSlot(name='on_buttonResetDecOffset_clicked')
    def _set_offset(self):
        """Asks user for new offsets and sets it."""

        # first all the reset buttons
        if self.sender() == self.buttonResetAltOffset:
            self.run_async(self.module.set_altaz_offsets, 0., self._off_az)
        elif self.sender() == self.buttonResetAzOffset:
            self.run_async(self.module.set_altaz_offsets, self._off_alt, 0.)
        elif self.sender() == self.buttonResetRaOffset:
            self.run_async(self.module.set_radec_offsets, 0., self._off_dec)
        elif self.sender() == self.buttonResetDecOffset:
            self.run_async(self.module.set_radec_offsets, self._off_ra, 0.)
        else:
            # now the sets, ask for value
            new_value, ok = QtWidgets.QInputDialog.getDouble(self, 'Set offset', 'New offset ["]', 0, 0, 999)
            if ok:
                if self.sender() == self.buttonSetAltOffset:
                    self.run_async(self.module.set_altaz_offsets, new_value / 3600., self._off_az)
                elif self.sender() == self.buttonSetAzOffset:
                    self.run_async(self.module.set_altaz_offsets, self._off_alt, new_value / 3600.)
                elif self.sender() == self.buttonSetRaOffset:
                    self.run_async(self.module.set_radec_offsets, new_value / 3600., self._off_dec)
                elif self.sender() == self.buttonSetDecOffset:
                    self.run_async(self.module.set_radec_offsets, self._off_ra, new_value / 3600.)

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
        if isinstance(self.module, IRaDecOffsets):
            self.run_async(self.module.set_radec_offsets, off_ra, off_dec)
        elif isinstance(self.module, IAltAzOffsets):
            off_alt, off_az = self._offset_radec_to_altaz(off_ra, off_dec)
            self.run_async(self.module.set_altaz_offsets, off_alt, off_az)
        else:
            raise ValueError
