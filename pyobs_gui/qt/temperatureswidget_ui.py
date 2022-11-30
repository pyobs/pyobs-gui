# -*- coding: utf-8 -*-

# Form implementation generated from ..reading ui file 'temperatureswidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_TemperaturesWidget(object):
    def setupUi(self, TemperaturesWidget):
        TemperaturesWidget.setObjectName("TemperaturesWidget")
        TemperaturesWidget.resize(271, 193)
        self.verticalLayout = QtWidgets.QVBoxLayout(TemperaturesWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(TemperaturesWidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frame = QtWidgets.QFrame(self.groupBox)
        self.frame.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setObjectName("frame")
        self.formLayout = QtWidgets.QFormLayout(self.frame)
        self.formLayout.setObjectName("formLayout")
        self.verticalLayout_2.addWidget(self.frame)
        self.buttonPlotTemps = QtWidgets.QToolButton(self.groupBox)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonPlotTemps.sizePolicy().hasHeightForWidth())
        self.buttonPlotTemps.setSizePolicy(sizePolicy)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/resources/chart-line-solid.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonPlotTemps.setIcon(icon)
        self.buttonPlotTemps.setToolButtonStyle(QtCore.Qt.ToolButtonTextBesideIcon)
        self.buttonPlotTemps.setObjectName("buttonPlotTemps")
        self.verticalLayout_2.addWidget(self.buttonPlotTemps)
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(TemperaturesWidget)
        QtCore.QMetaObject.connectSlotsByName(TemperaturesWidget)

    def retranslateUi(self, TemperaturesWidget):
        _translate = QtCore.QCoreApplication.translate
        TemperaturesWidget.setWindowTitle(_translate("TemperaturesWidget", "Form"))
        self.groupBox.setTitle(_translate("TemperaturesWidget", "Temperatures"))
        self.buttonPlotTemps.setText(_translate("TemperaturesWidget", "Plot && log temperatures"))
from . import resources_rc
