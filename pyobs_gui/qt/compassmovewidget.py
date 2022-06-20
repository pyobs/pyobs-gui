from PyQt5 import QtWidgets, uic


class CompassMoveWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        uic.loadUi("compassmovewidget.ui", self)
