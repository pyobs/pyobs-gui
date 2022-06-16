from PyQt5 import QtWidgets, uic


class CameraWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        uic.loadUi("camerawidget.ui", self)
