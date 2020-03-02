import threading

import astroquery
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from PyQt5 import QtWidgets
from astroplan import Observer
from astropy.coordinates import SkyCoord, ICRS, AltAz
import astropy.units as u
import logging

from astroquery.exceptions import InvalidQueryError
from astroquery.simbad import Simbad
from astroquery.mpc import MPC

from pyobs.comm import Comm
from pyobs.events import MotionStatusChangedEvent
from pyobs.interfaces import ITelescope, IFilters, IFocuser, ITemperatures, IMotion
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

        # before first update, disable mys
        self.setEnabled(False)

        # plot
        #self.figure = plt.figure()
        #self.plot = VisPlot(self.figure, self.environment)
        #self.canvas = FigureCanvas(self.figure)
        #self.widgetPlot.setLayout(QtWidgets.QVBoxLayout())
        #self.widgetPlot.layout().addWidget(self.canvas)
        #self.first = True

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        #self.butTrack.clicked.connect(self.move_ra_dec)
        #self.butMove.clicked.connect(self.move_alt_az)
        #self.butInit.clicked.connect(lambda: self.run_async(self.module.init))
        #self.butPark.clicked.connect(lambda: self.run_async(self.module.park))
        #self.textTrackRA.textChanged.connect(self._calc_track_alt_az)
        #self.textTrackDec.textChanged.connect(self._calc_track_alt_az)
        #self.buttonSimbadQuery.clicked.connect(self._query_simbad)
        #self.buttonMpcQuery.clicked.connect(self._query_mpc)

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
        self._fetch_coordinates()
        self.signal_update_gui.emit()

    def _fetch_coordinates(self):
        # get RA/Dec
        try:
            ra, dec = self.module.get_radec().wait()
            self._ra_dec = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')
        except:
            self._ra_dec = None

        # get Alt/Az
        try:
            alt, az = self.module.get_altaz().wait()
            self._alt_az = SkyCoord(alt=alt * u.deg, az=az * u.deg, frame='altaz')
        except:
            self._alt_az = None

    def _update(self):
        # get coordinates
        self._fetch_coordinates()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self):
        # enable myself
        self.setEnabled(True)

        # show motion status
        self.labelStatus.setText(self._motion_status.value.upper())

        # plot
        #if self.first:
        #    self.plot.plot(self._ra_dec)
        #    self.canvas.draw()
        #    self.first = False

        # show them
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
            self.run_async(self.module.track_radec, float(coords.ra.degree), float(coords.dec.degree))

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
