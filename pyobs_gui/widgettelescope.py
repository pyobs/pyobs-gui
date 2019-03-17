import threading
from PyQt5.QtCore import pyqtSignal
from astropy.coordinates import SkyCoord, ICRS
import astropy.units as u
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from pyobs.interfaces import ITelescope, IFilters, IFocuser
from pyobs_gui.visplot import VisPlot
from .qt.widgettelescope import Ui_WidgetTelescope
from .basewidget import BaseWidget


class WidgetTelescope(BaseWidget, Ui_WidgetTelescope):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, environment, parent=None):
        BaseWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: ITelescope, IFilters, IFocuser
        self.environment = environment  # type: Environment

        # variables
        self.status = None

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

    def enter(self):
        # create event for update thread to close
        self._update_thread_event = threading.Event()

        # start update thread
        self._update_thread = threading.Thread(target=self._update)
        self._update_thread.start()

    def leave(self):
        # stop thread
        self._update_thread_event.set()
        self._update_thread.join()
        self._update_thread = None
        self._update_thread_event = None

    def _update(self):
        while not self._update_thread_event.is_set():
            try:
                # get camera status
                self.status = self.module.status()

                # signal GUI update
                self.signal_update_gui.emit()
            except:
                pass

            # sleep a little
            self._update_thread_event.wait(1)

    def update_gui(self):
        # enable myself
        self.setEnabled(True)

        # show motion status
        self.labelStatus.setText(self.status['ITelescope']['Status'].upper())

        # get coordinates
        pos = self.status['ITelescope']['Position']
        ra_dec = SkyCoord(ra=pos['RA'] * u.deg, dec=pos['Dec'] * u.deg, frame='icrs')

        # plot
        if self.first:
            self.plot.plot(ra_dec)
            self.canvas.draw()
            self.first = False

        # show them
        self.labelCurRA.setText(ra_dec.ra.to_string(unit=u.hour, sep=':', precision=3))
        self.labelCurDec.setText(ra_dec.dec.to_string(unit=u.deg, sep=':', precision=3))
        self.labelCurAlt.setText('%.3f' % pos['Alt'])
        self.labelCurAz.setText('%.3f' % pos['Az'])

        # filter
        if isinstance(self.module, IFilters):
            self.labelCurFilter.setText(self.status['IFilter']['Filter'])

        # focus
        if isinstance(self.module, IFocuser):
            self.labelCurFocus.setText('%.3f' % self.status['IFocuser']['Focus'])

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
