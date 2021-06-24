import logging
from urllib.parse import urlparse

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QTcpSocket

from pyobs.comm import Comm
from pyobs.interfaces import ICamera, IVideo
from pyobs.vfs import VirtualFileSystem, HttpFile
from pyobs_gui.basewidget import BaseWidget

from .qt.widgetvideo import Ui_WidgetVideo
from .widgetcamera import WidgetCamera

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
    def __init__(self, module: IVideo, comm: Comm, vfs: VirtualFileSystem, parent=None):
        BaseWidget.__init__(self, parent=parent)
        self.setupUi(self)

        # store
        self.module = module
        self.comm = comm
        self.vfs = vfs
        self.host = None
        self.port = None
        self.path = None

        # add live view
        self.widgetLiveView = ScaledLabel()
        self.tabLiveView.layout().addWidget(self.widgetLiveView)

        # add camera widget
        self.widgetCamera = WidgetCamera(module, comm, vfs)
        self.tabFitsImage.layout().addWidget(self.widgetCamera)

        # init buffer
        self.buffer = b''

        # socket
        self.socket = QTcpSocket()
        self.socket.readyRead.connect(self._received_data)

    def _init(self):
        # init camera widget
        self.widgetCamera._init()

        # get video stream URL and open it
        video_path = self.module.get_video().wait()
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

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        # call base
        BaseWidget.showEvent(self, event)

        # connect socket
        if self.host is not None:
            self.socket.connectToHost(self.host, int(self.port))
            self.socket.write(b'GET %s HTTP/1.1\r\n\r\n' % bytes(self.path, 'UTF-8'))

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # call base
        BaseWidget.hideEvent(self, event)

        # disconnect socket
        self.socket.disconnectFromHost()

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


__all__ = ['WidgetVideo']
