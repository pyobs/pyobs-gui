import threading
from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QMessageBox
from matplotlib.backends.backend_qt5 import NavigationToolbar2QT
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
import aplpy

from pytel.interfaces import ICamera, ICameraBinning, ICameraWindow
from .qt.widgetcamera import Ui_WidgetCamera


class WidgetCamera(QtWidgets.QWidget, Ui_WidgetCamera):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, parent=None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setupUi(self)
        self.module = module    # type: ICamera

        # variables
        self.image_filename = None
        self.image = None
        self.status = None

        # set exposure types
        image_types = [t.name for t in ICamera.ImageType]
        self.comboImageType.addItems(image_types)

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

    def set_full_frame(self):
        # get full frame
        frame = self.module.get_full_frame()

        # set it
        self.spinWindowLeft.setValue(frame['left'])
        self.spinWindowTop.setValue(frame['top'])
        self.spinWindowWidth.setValue(frame['width'])
        self.spinWindowHeight.setValue(frame['height'])

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

        # do exposure(s)
        try:
            filename = self.module.expose(self.spinExpTime.value(), self.comboImageType.currentText().lower(),
                                          self.spinCount.value())
        except:
            #QMessageBox.information(self, 'Error', 'Could not take image.')
            return

    def plot(self):
        # clear figure
        print("plot")
        self.figure.clf()

        # plot image
        gc = aplpy.FITSFigure(self.image, figure=self.figure)
        gc.show_colorscale(cmap='gist_heat', stretch='arcsinh')

        # show it
        self.canvas.draw()
        
    def abort(self):
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
                # get camera status
                self.status = self.module.status()

                # signal GUI update
                self.signal_update_gui.emit()
            except:
                pass

            # sleep a little
            self._update_thread_event.wait(0.5)

    def update_gui(self):
        # enable/disable buttons
        self.butExpose.setEnabled(self.status['ICamera']['Status'] == 'idle')
        self.butAbort.setEnabled(self.status['ICamera']['Status'] != 'idle')

        # set abort text
        if self.status['ICamera']['ExposuresLeft'] > 1:
            self.butAbort.setText('Abort sequence')
        else:
            self.butAbort.setText('Abort exposure')

        # set progress
        if self.status['ICamera']['Status'] == 'idle':
            self.progressExposure.setValue(0)
            msg = 'IDLE'
        elif self.status['ICamera']['Status'] == 'exposing':
            self.progressExposure.setValue(self.status['ICamera']['Progress'])
            msg = 'EXPOSING %.1fs' % (self.status['ICamera']['ExposureTimeLeft'] / 1000.,)
        elif self.status['ICamera']['Status'] == 'readout':
            self.progressExposure.setValue(100)
            msg = 'READOUT'

        # set message
        self.labelStatus.setText(msg)

        # exposures left
        if self.status['ICamera']['ExposuresLeft'] > 0:
            self.labelExposuresLeft.setText('%d exposure(s) left' % self.status['ICamera']['ExposuresLeft'])
        else:
            self.labelExposuresLeft.setText('')

        # image
        if self.image_filename != self.status['ICamera']['LastImage']:
            # set it
            self.image_filename = self.status['ICamera']['LastImage']

            # download image
            from pytel.vfs import VirtualFileSystem
            vfs = VirtualFileSystem(
                roots={'cache': {'class': 'pytel.vfs.HttpFile', 'upload': 'http://localhost:37075',
                                 'download': 'http://localhost:37075'}})
            self.image = vfs.download_fits_image(self.image_filename)

            # trigger plot
            self.plot()
