import logging
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtNetwork import QTcpSocket

from pyobs.interfaces import ICamera
from pyobs.vfs import VirtualFileSystem
from pyobs_gui.basewidget import BaseWidget


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


class WidgetWebcam(BaseWidget):
    def __init__(self, module, comm, vfs, parent=None):
        BaseWidget.__init__(self, parent=parent)

        # store
        self.module = module    # type: ICamera
        self.comm = comm        # type: Comm
        self.vfs = vfs          # type: VirtualFileSystem

        # set up ui
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.video = ScaledLabel()
        layout.addWidget(self.video)

        # init buffer
        self.buffer = b''
        self.socket = QTcpSocket()

    def showEvent(self, event: QtGui.QShowEvent) -> None:
        # connect socket
        self.socket.connectToHost("localhost", 37077)
        self.socket.readyRead.connect(self._received_data)
        self.socket.write(b'GET /video.mjpg HTTP/1.1\r\n\r\n')

        # call base
        BaseWidget.showEvent(self, event)

    def hideEvent(self, event: QtGui.QHideEvent) -> None:
        # disconnect socket
        self.socket.disconnect()

        # call base
        BaseWidget.hideEvent(self, event)

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
            self.video.setPixmap(qp)
