# -*- coding: utf-8 -*-

# Form implementation generated from ..reading ui file 'temperaturesplotwidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TemperaturesPlotWidget(object):
    def setupUi(self, TemperaturesPlotWidget):
        TemperaturesPlotWidget.setObjectName("TemperaturesPlotWidget")
        TemperaturesPlotWidget.resize(515, 293)
        self.verticalLayout = QtWidgets.QVBoxLayout(TemperaturesPlotWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.frame = QtWidgets.QFrame(TemperaturesPlotWidget)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout.addWidget(self.frame)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label = QtWidgets.QLabel(TemperaturesPlotWidget)
        self.label.setObjectName("label")
        self.horizontalLayout.addWidget(self.label)
        self.comboShow = QtWidgets.QComboBox(TemperaturesPlotWidget)
        self.comboShow.setObjectName("comboShow")
        self.horizontalLayout.addWidget(self.comboShow)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.checkLogFile = QtWidgets.QCheckBox(TemperaturesPlotWidget)
        self.checkLogFile.setObjectName("checkLogFile")
        self.horizontalLayout.addWidget(self.checkLogFile)
        self.lineLogFile = QtWidgets.QLineEdit(TemperaturesPlotWidget)
        self.lineLogFile.setReadOnly(True)
        self.lineLogFile.setObjectName("lineLogFile")
        self.horizontalLayout.addWidget(self.lineLogFile)
        self.buttonPickFile = QtWidgets.QToolButton(TemperaturesPlotWidget)
        self.buttonPickFile.setObjectName("buttonPickFile")
        self.horizontalLayout.addWidget(self.buttonPickFile)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout.setStretch(0, 1)

        self.retranslateUi(TemperaturesPlotWidget)
        QtCore.QMetaObject.connectSlotsByName(TemperaturesPlotWidget)

    def retranslateUi(self, TemperaturesPlotWidget):
        _translate = QtCore.QCoreApplication.translate
        TemperaturesPlotWidget.setWindowTitle(_translate("TemperaturesPlotWidget", "Form"))
        self.label.setText(_translate("TemperaturesPlotWidget", "Show:"))
        self.checkLogFile.setText(_translate("TemperaturesPlotWidget", "Log file:"))
        self.buttonPickFile.setText(_translate("TemperaturesPlotWidget", "..."))
