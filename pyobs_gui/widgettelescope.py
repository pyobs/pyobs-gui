import threading
from PyQt5.QtCore import pyqtSignal
from astroplan import Observer
from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u
import logging
from astroquery.simbad import Simbad

from pyobs.comm import Comm
from pyobs.events import MotionStatusChangedEvent
from pyobs.interfaces import ITelescope, IFilters, IFocuser, ITemperatures
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
        self._motion_status = None
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
        self.butTrack.clicked.connect(self.move_ra_dec)
        self.butMove.clicked.connect(self.move_alt_az)
        self.butInit.clicked.connect(lambda: self.run_async(self.module.init))
        self.butPark.clicked.connect(lambda: self.run_async(self.module.park))
        self.textTrackRA.textChanged.connect(self._calc_track_alt_az)
        self.textTrackDec.textChanged.connect(self._calc_track_alt_az)
        self.buttonSimbadQuery.clicked.connect(self._query_simbad)

        # subscribe to events
        self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)

        # fill sidebar
        if isinstance(self.module, IFilters):
            self.add_to_sidebar(WidgetFilter(module, comm))
        if isinstance(self.module, IFocuser):
            self.add_to_sidebar(WidgetFocus(module, comm))
        if isinstance(self.module, ITemperatures):
            self.add_to_sidebar(WidgetTemperatures(module, comm))

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

    def move_ra_dec(self):
        # get ra and dec
        ra = self.textTrackRA.text()
        dec = self.textTrackDec.text()
        coords = SkyCoord(ra + ' ' + dec, frame=ICRS, unit=(u.hour, u.deg))

        # start thread with move
        self.run_async(self.module.track_radec, coords.ra.degree, coords.dec.degree)

        # plot it
        #self.plot.plot(coords)

    def move_alt_az(self):
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
        self._motion_status = event.current

        # trigger GUI update
        self.signal_update_gui.emit()

    def _query_simbad(self):
        """Takes the object name from the text box, queries simbad, and fills the RA/Dec inputs with the result."""

        # query
        result = Simbad.query_object(self.textSimbadName.text())

        # always use first result
        for r in result:
            # set it
            self.textTrackRA.setText(r['RA'])
            self.textTrackDec.setText(r['DEC'])
            self.textSimbadName.setText(r['MAIN_ID'].decode('utf-8'))

    def _calc_track_alt_az(self):
        """Called, whenever RA/Dec input changes. Calculates destination Alt/Az."""

        # get ra and dec
        ra = self.textTrackRA.text()
        dec = self.textTrackDec.text()

        # parse it
        try:
            ra_dec = SkyCoord(ra + ' ' + dec, frame=ICRS, unit=(u.hour, u.deg))
        except ValueError:
            # on error, show it
            self.textTrackAlt.setText('N/A')
            self.textTrackAz.setText('N/A')
            return

        # to alt/az
        alt_az = self.observer.altaz(Time.now(), ra_dec)

        # display
        self.textTrackAlt.setText('%.2f°' % alt_az.alt.degree)
        self.textTrackAz.setText('%.2f°' % alt_az.az.degree)
