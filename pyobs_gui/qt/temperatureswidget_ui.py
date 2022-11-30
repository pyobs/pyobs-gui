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
        TemperaturesWidget.resize(307, 63)
        self.verticalLayout = QtWidgets.QVBoxLayout(TemperaturesWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(TemperaturesWidget)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(TemperaturesWidget)
        QtCore.QMetaObject.connectSlotsByName(TemperaturesWidget)

    def retranslateUi(self, TemperaturesWidget):
        _translate = QtCore.QCoreApplication.translate
        TemperaturesWidget.setWindowTitle(_translate("TemperaturesWidget", "Form"))
        self.groupBox.setTitle(_translate("TemperaturesWidget", "Temperatures"))
