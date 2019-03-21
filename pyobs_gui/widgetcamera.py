import threading
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import aplpy

from pyobs.events import ExposureStatusChangedEvent
from pyobs.interfaces import ICamera, ICameraBinning, ICameraWindow
from pyobs.vfs import VirtualFileSystem
from .qt.widgetcamera import Ui_WidgetCamera


class WidgetCamera(QtWidgets.QWidget, Ui_WidgetCamera):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, vfs, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: ICamera
        self.comm = comm        # type: Comm
        self.vfs = vfs          # type: VirtualFileSystem

        # variables
        self.image_filename = None
        self.image = None
        self.status = None
        self.exposure_status = ICamera.ExposureStatus.IDLE
        self.exposures_left = 0
        self.exposure_time_left = 0
        self.exposure_progress = 0

        # set exposure types
        image_types = [t.name for t in ICamera.ImageType]
        self.comboImageType.addItems(image_types)

        # before first update, disable mys
        self.setEnabled(False)

        # hide groups, if necessary
        self.groupWindowing.setVisible(isinstance(self.module, ICameraWindow))
        self.groupBinning.setVisible(isinstance(self.module, ICameraBinning))

        # add image panel
        self.figure = plt.figure()
        self.canvas = FigureCanvas(self.figure)
        self.canvasToolbar = NavigationToolbar2QT(self.canvas, self.frame)
        self.canvasLayout = QtWidgets.QVBoxLayout(self.frame)
        self.canvasLayout.addWidget(self.canvasToolbar)
        self.canvasLayout.addWidget(self.canvas)

        # update thread
        self._update_thread = None
        self._update_thread_event = None

        # connect signals
        self.butFullFrame.clicked.connect(self.set_full_frame)
        self.comboImageType.currentTextChanged.connect(self.image_type_changed)
        self.butExpose.clicked.connect(self.expose)
        self.butAbort.clicked.connect(self.abort)
        self.signal_update_gui.connect(self.update_gui)

        # initial values
        self.set_full_frame()
        self.comboImageType.setCurrentIndex(image_types.index('OBJECT'))

        # subscribe to events
        self.comm.register_event(ExposureStatusChangedEvent, self._exposure_status_changed)

    def enter(self):
        # create event for update thread to close
        self._update_thread_event = threading.Event()

        # start update thread
        self._update_thread = threading.Thread(target=self._update)
        self._update_thread.start()

        # get status
        self.exposure_status = ICamera.ExposureStatus(self.module.get_exposure_status())
        self.update_gui()

    def leave(self):
        # stop thread
        self._update_thread_event.set()
        self._update_thread.join()
        self._update_thread = None
        self._update_thread_event = None

    def set_full_frame(self):
        if isinstance(self.module, ICameraWindow):
            # get full frame
            left, top, width, height = self.module.get_full_frame()

            # set it
            self.spinWindowLeft.setValue(left)
            self.spinWindowTop.setValue(top)
            self.spinWindowWidth.setValue(width)
            self.spinWindowHeight.setValue(height)

    def image_type_changed(self, image_type):
        if image_type == 'BIAS':
            self.spinExpTime.setValue(0)
            self.spinExpTime.setEnabled(False)
        else:
            self.spinExpTime.setEnabled(True)

    def expose(self):
        # start thread for exposure
        threading.Thread(target=self._expose).start()

    def _expose(self):
        # set binning
        if isinstance(self.module, ICameraBinning):
            binx, biny = self.spinBinningX.value(), self.spinBinningY.value()
            try:
                self.module.set_binning(binx, biny)
            except:
                #QMessageBox.information(self, 'Error', 'Could not set binning.')
                return
        else:
            binx, biny = 1, 1

        # set window
        if isinstance(self.module, ICameraWindow):
            left, top = self.spinWindowLeft.value(), self.spinWindowTop.value()
            width, height = self.spinWindowWidth.value(), self.spinWindowHeight.value()
            try:
                self.module.set_window(left, top, width * binx, height * biny)
            except:
                #QMessageBox.information(self, 'Error', 'Could not set window.')
                return

        # get image type
        image_type = ICamera.ImageType(self.comboImageType.currentText().lower())

        # do exposure(s)
        try:
            filename = self.module.expose(self.spinExpTime.value(), image_type, self.spinCount.value())
            self.image = self.vfs.download_fits_image(filename)
            self.signal_update_gui.emit()

        except:
            #QMessageBox.information(self, 'Error', 'Could not take image.')
            return

    def plot(self):
        """Show image."""

        # clear figure
        self.figure.clf()

        # plot image
        gc = aplpy.FITSFigure(self.image, figure=self.figure)
        gc.show_colorscale(cmap='gist_heat', stretch='arcsinh')

        # show it
        self.canvas.draw()
        
    def abort(self):
        """Abort exposure."""

        # do we have a status?
        if self.status is None:
            return

        # got exposures left?
        if self.status['ICamera']['ExposuresLeft'] > 1:
            self.module.abort_sequence()
        else:
            self.module.abort()

    def _update(self):
        while not self._update_thread_event.is_set():
            try:
                # are we exposing?
                if self.exposure_status == ICamera.ExposureStatus.EXPOSING:
                    # get camera status
                    self.exposures_left = self.module.get_exposures_left()
                    self.exposure_time_left = self.module.get_exposure_time_left()
                    self.exposure_progress = self.module.get_exposure_progress()

                    # signal GUI update
                    self.signal_update_gui.emit()
            except:
                pass

            # sleep a little
            self._update_thread_event.wait(1)

    def update_gui(self):
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # enable/disable buttons
        self.butExpose.setEnabled(self.exposure_status == ICamera.ExposureStatus.IDLE)
        self.butAbort.setEnabled(self.exposure_status != ICamera.ExposureStatus.IDLE)

        # set abort text
        if self.exposures_left > 1:
            self.butAbort.setText('Abort sequence')
        else:
            self.butAbort.setText('Abort exposure')

        # set progress
        msg = ''
        if self.exposure_status == ICamera.ExposureStatus.IDLE:
            self.progressExposure.setValue(0)
            msg = 'IDLE'
        elif self.exposure_status == ICamera.ExposureStatus.EXPOSING:
            self.progressExposure.setValue(self.exposure_progress)
            msg = 'EXPOSING %.1fs' % (self.exposure_time_left / 1000.,)
        elif self.exposure_status == ICamera.ExposureStatus.READOUT:
            self.progressExposure.setValue(100)
            msg = 'READOUT'

        # set message
        self.labelStatus.setText(msg)

        # exposures left
        if self.exposures_left > 0:
            self.labelExposuresLeft.setText('%d exposure(s) left' % self.exposures_left)
        else:
            self.labelExposuresLeft.setText('')

        # trigger plot
        if self.image is not None:
            # plot image
            self.plot()

            # reset it
            self.image = None

    def _exposure_status_changed(self, event: ExposureStatusChangedEvent, sender: str):
        """Called when exposure status of module changed.

        Args:
            event: Status change event.
            sender: Name of sender.
        """

        # store new status
        self.exposure_status = event.current
        print(event.last, event.current)

        # trigger GUI update
        self.signal_update_gui.emit()
