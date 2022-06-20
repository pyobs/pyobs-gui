from PyQt5 import QtWidgets, uic


class DataDisplayWidget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        QtWidgets.QWidget.__init__(self, *args, **kwargs)
        uic.loadUi("datadisplaywidget.ui", self)
