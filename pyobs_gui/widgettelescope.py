import threading
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from astropy.coordinates import SkyCoord
import astropy.units as u

from pyobs.interfaces import ITelescope
from .qt.widgettelescope import Ui_WidgetTelescope


class WidgetTelescope(QtWidgets.QWidget, Ui_WidgetTelescope):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: ITelescope

        # variables
        self.status = None

        # update thread
        self._update_thread = None
        self._update_thread_event = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

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
            self._update_thread_event.wait(0.5)

    def update_gui(self):
        # get coordinates
        pos = self.status['ITelescope']['Position']
        ra_dec = SkyCoord(ra=pos['RA'] * u.deg, dec=pos['Dec'] * u.deg, frame='icrs')

        # show them
        self.labelCurRA.setText(ra_dec.ra.to_string(unit=u.hour, sep=':', precision=3))
        self.labelCurDec.setText(ra_dec.dec.to_string(unit=u.deg, sep=':', precision=3))
        self.labelCurAlt.setText('%.3f' % pos['Alt'])
        self.labelCurAz.setText('%.3f' % pos['Az'])
