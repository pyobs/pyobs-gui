import threading
from PyQt5.QtCore import pyqtSignal
from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import logging

from pyobs.events import FilterChangedEvent, MotionStatusChangedEvent
from pyobs.interfaces import ITelescope, IFilters, IFocuser
from pyobs_gui.visplot import VisPlot
from .qt.widgettelescope import Ui_WidgetTelescope
from .basewidget import BaseWidget


log = logging.getLogger(__name__)


class WidgetTelescope(BaseWidget, Ui_WidgetTelescope):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, environment, parent=None):
        BaseWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: ITelescope, IFilters, IFocuser
        self.comm = comm  # type: Comm
        self.environment = environment  # type: Environment

        # variables
        self._motion_status = None
        self._ra_dec = None
        self._alt_az = None
        self._focus = None
        self._filter = None

        # before first update, disable mys
        self.setEnabled(False)

        # update thread
        self._update_thread = None
        self._update_thread_event = None

        # get all filters
        if isinstance(self.module, IFilters):
            self.comboFilter.addItems(self.module.list_filters())

        # plot
        self.figure = plt.figure()
        self.plot = VisPlot(self.figure, self.environment)
        self.canvas = FigureCanvas(self.figure)
        self.groupStatus.layout().addWidget(self.canvas)
        self.first = True

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butTrack.clicked.connect(self.track)
        self.butMove.clicked.connect(self.move)
        self.butInit.clicked.connect(lambda: self.run_async(self.module.init))
        self.butPark.clicked.connect(lambda: self.run_async(self.module.park))
        self.butSetFocus.clicked.connect(lambda: self.run_async(self.module.set_focus,
                                                                self.spinFocus.value()))
        self.butSetFilter.clicked.connect(lambda: self.run_async(self.module.set_filter,
                                                                 self.comboFilter.currentText()))

        # subscribe to events
        self.comm.register_event(MotionStatusChangedEvent, self._on_motion_status_changed)
        self.comm.register_event(FilterChangedEvent, self._on_filter_changed)


    def enter(self):
        # create event for update thread to close
        self._update_thread_event = threading.Event()

        # start update thread
        self._update_thread = threading.Thread(target=self._update)
        self._update_thread.start()

        # get variables
        self._motion_status = self.module.get_motion_status()
        self._fetch_coordinates()
        if isinstance(self.module, IFilters):
            self._filter = self.module.get_filter()
        if isinstance(self.module, IFocuser):
            self._focus = self.module.get_focus()

    def leave(self):
        # stop thread
        self._update_thread_event.set()
        self._update_thread.join()
        self._update_thread = None
        self._update_thread_event = None

    def _fetch_coordinates(self):
        # get RA/Dec
        ra, dec = self.module.get_ra_dec()
        self._ra_dec = SkyCoord(ra=ra * u.deg, dec=dec * u.deg, frame='icrs')

        # get Alt/Az
        alt, az = self.module.get_alt_az()
        self._alt_az = SkyCoord(alt=alt * u.deg, az=az * u.deg, frame='altaz')

    def _update(self):
        while not self._update_thread_event.is_set():
            try:
                # get coordinates
                self._fetch_coordinates()

                # and focus
                if isinstance(self.module, IFocuser):
                    self._focus = self.module.get_focus()


                # signal GUI update
                self.signal_update_gui.emit()
            except:
                log.exception('Error')
                pass

            # sleep a little
            self._update_thread_event.wait(1)

    def update_gui(self):
        # enable myself
        self.setEnabled(True)

        # show motion status
        self.labelStatus.setText(self._motion_status.value.upper())

        # plot
        if self.first:
            self.plot.plot(self._ra_dec)
            self.canvas.draw()
            self.first = False

        # show them
        self.labelCurRA.setText(self._ra_dec.ra.to_string(unit=u.hour, sep=':', precision=3))
        self.labelCurDec.setText(self._ra_dec.dec.to_string(unit=u.deg, sep=':', precision=3))
        self.labelCurAlt.setText('%.3f' % self._alt_az.alt.degree)
        self.labelCurAz.setText('%.3f' % self._alt_az.az.degree)

        # filter
        if self._filter:
            self.labelCurFilter.setText(self._filter)

        # focus
        if self._focus:
            self.labelCurFocus.setText('%.3f' % self._focus)

    def track(self):
        # get ra and dec
        ra = self.textTrackRA.text()
        dec = self.textTrackDec.text()
        coords = SkyCoord(ra + ' ' + dec, frame=ICRS, unit=(u.hour, u.deg))

        # start thread with move
        self.run_async(self.module.track, coords.ra.degree, coords.dec.degree)

        # plot it
        self.plot.plot(coords)

    def move(self):
        # get alt and az
        alt = self.spinMoveAlt.value()
        az = self.spinMoveAz.value()

        # move
        self.run_async(self.module.move, alt, az)

    def _on_motion_status_changed(self, event: MotionStatusChangedEvent, sender: str):
        """Called when motion status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # store new status
        self._motion_status = event.current

        # trigger GUI update
        self.signal_update_gui.emit()


    def _on_filter_changed(self, event: FilterChangedEvent, sender: str):
        """Called when filter changed.

        Args:
            event: Filter change event.
            sender: Name of sender.
        """

        # store new filter
        self._filter = event.filter

        # trigger GUI update
        self.signal_update_gui.emit()
