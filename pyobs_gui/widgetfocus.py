import threading
import logging
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import IFocuser
from .qt.widgetfocus import Ui_WidgetFocus


log = logging.getLogger(__name__)


class WidgetFocus(QtWidgets.QWidget, Ui_WidgetFocus):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: IFocuser
        self.comm = comm        # type: Comm

        # variables
        self._focus = None
        self._update_thread_event = None
        self._update_thread = None

        # connect signals
        self.signal_update_gui.connect(self.update_gui)
        self.butSetFocus.clicked.connect(lambda: self.run_async(self.module.set_focus,
                                                                self.spinFocus.value()))

        # initial values
        threading.Thread(target=self._init).start()

    def _init(self):
        # get current filter
        self._focus = self.module.get_focus()
        self.signal_update_gui.emit()

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
                # get focus
                self._focus = self.module.get_focus()

                # signal GUI update
                self.signal_update_gui.emit()

            except:
                log.exception('Error')
                pass

            # sleep a little
            self._update_thread_event.wait(1)

    def update_gui(self):
        # enable myself and set filter
        self.setEnabled(True)
        self.labelCurFocus.setText('%.3f' % self._focus)
