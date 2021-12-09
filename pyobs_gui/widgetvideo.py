import asyncio
import logging
from urllib.parse import urlparse

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import pyqtSlot, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QTcpSocket

from pyobs.interfaces import IExposureTime, IImageType, IImageFormat
from pyobs.utils.enums import ImageFormat, ImageType
from pyobs.vfs import HttpFile
from pyobs_gui.basewidget import BaseWidget

from .qt.widgetvideo import Ui_WidgetVideo
from .widgetdatadisplay import WidgetDataDisplay

log = logging.getLogger(__name__)


class ScaledLabel(QtWidgets.QLabel):
    def __init__(self, *args, **kwargs):
        QtWidgets.QLabel.__init__(self)
        self._pixmap = None
        self.setMinimumSize(QtCore.QSize(10, 10))

    def setPixmap(self, pixmap):
        self._pixmap = pixmap
        scaled = pixmap.scaled(self.width(), self.height(), QtCore.Qt.KeepAspectRatio)
        QtWidgets.QLabel.setPixmap(self, scaled)

    def resizeEvent(self, event):
        if self._pixmap is not None:
            self.setPixmap(self._pixmap)


class WidgetVideo(BaseWidget, Ui_WidgetVideo):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # store
        self.host = None
        self.port = None
        self.path = None
        self.exposures_left = 0

        # add live view
        self.widgetLiveView = ScaledLabel()
        self.frameLiveView.layout().addWidget(self.widgetLiveView)

        # add camera widget
        self.widgetDataDisplay = self.create_widget(WidgetDataDisplay, module=self.module)
        self.frameImageGrabber.layout().addWidget(self.widgetDataDisplay)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

        # before first update, disable mys
        self.setEnabled(False)

        # init buffer
        self.buffer = b''

        # socket
        self.socket = QTcpSocket()
        self.socket.readyRead.connect(self._received_data)

        # set exposure types
        image_types = sorted([it.name for it in ImageType])
        self.comboImageType.addItems(image_types)
        self.comboImageType.setCurrentText('OBJECT')

        # hide single controls, if necessary
        self.labelImageType.setVisible(isinstance(self.module, IImageType))
        self.comboImageType.setVisible(isinstance(self.module, IImageType))
        self.labelExpTime.setVisible(isinstance(self.module, IExposureTime))
        self.spinExpTime.setVisible(isinstance(self.module, IExposureTime))

        # initial values
        self.comboImageType.setCurrentIndex(image_types.index('OBJECT'))

    async def _init(self):
        # get video stream URL and open it
        video_path = await self.module.get_video()
        video_file = self.vfs.open_file(video_path, 'r')

        # we heed a HttpFile
        if not isinstance(video_file, HttpFile):
            log.error('VFS path to video of module %s must be an HttpFile.', self.module.name)
            return

        # analyse URL
        o = urlparse(video_file.url)

        # scheme must be http
        # TODO: how to do HTTPS?
        if o.scheme != 'http':
            log.error('URL scheme to video of module %s must be HTTP.', self.module.name)
            return

        # get info
        (self.host, self.port) = tuple(o.netloc.split(':')) if ':' in o.netloc else (o.netloc, 80)
        self.path = o.path

        # get initial values
        if isinstance(self.module, IExposureTime):
            self.spinExpTime.setValue(await self.module.get_exposure_time())

        # update GUI
        self.signal_update_gui.emit()

    async def _showEvent(self, event: QtGui.QShowEvent) -> None:
        # call base
        await BaseWidget._showEvent(self, event)

        # connect socket
        if self.host is not None:
            self.socket.connectToHost(self.host, int(self.port))
            self.socket.write(b'GET %s HTTP/1.1\r\n\r\n' % bytes(self.path, 'UTF-8'))

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # call base
        BaseWidget.hideEvent(self, event)

        # disconnect socket
        self.socket.disconnectFromHost()

    def update_gui(self):
        """Update the GUI."""

        # enable myself
        self.setEnabled(True)

        # enable/disable buttons
        self.buttonAbort.setEnabled(self.exposures_left > 0)

        # exposures left
        if self.exposures_left > 0:
            self.labelExposuresLeft.setText('%d exposure(s) left' % self.exposures_left)
        else:
            self.labelExposuresLeft.setText('')

    def _received_data(self):
        boundary = b'--jpgboundary\r\n'
        self.buffer += bytes(self.socket.readAll())
        while boundary in self.buffer:
            # find boundary
            pos = self.buffer.find(boundary)

            # find end of header
            frame = self.buffer[:pos]

            # remove from buffer
            self.buffer = self.buffer[pos + len(boundary):]

            # find end of frame
            image_data = frame[frame.find(b'\r\n\r\n') + 4:]

            # to pixmap and show it
            qp = QPixmap()
            qp.loadFromData(image_data)
            self.widgetLiveView.setPixmap(qp)

    @pyqtSlot(name='on_buttonGrabImage_clicked')
    def grab_image(self):
        # set image format
        if isinstance(self.module, IImageFormat):
            image_format = ImageFormat[self.comboImageFormat.currentText()]
            self.module.set_image_format(image_format)

        # set initial image count
        self.exposures_left = self.spinCount.value()

        # signal GUI update
        self.signal_update_gui.emit()

        # start exposures
        asyncio.create_task(self._expose_thread_func())

    async def _expose_thread_func(self):
        # get image type
        image_type = ImageType(self.comboImageType.currentText().lower())

        # do exposure(s)
        while self.exposures_left > 0:
            # set image type
            if isinstance(self.module, IImageType):
                await self.module.set_image_type(image_type)

            # expose
            broadcast = self.checkBroadcast.isChecked()
            await self.widgetDataDisplay.grab_data(broadcast, image_type)

            # decrement number of exposures left
            self.exposures_left -= 1

            # signal GUI update
            self.signal_update_gui.emit()

    @pyqtSlot(name='on_buttonAbort_clicked')
    def abort_sequence(self):
        self.exposures_left = 0

    @pyqtSlot(float, name='on_spinExpTime_valueChanged')
    def exposure_time_changed(self):
        # get exp_time
        exp_time = self.spinExpTime.value()

        # set it
        if isinstance(self.module, IExposureTime):
            asyncio.create_task(self.module.set_exposure_time(exp_time))


__all__ = ['WidgetVideo']
