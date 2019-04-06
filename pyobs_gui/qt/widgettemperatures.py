# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgettemperatures.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WidgetTemperatures(object):
    def setupUi(self, WidgetTemperatures):
        WidgetTemperatures.setObjectName("WidgetTemperatures")
        WidgetTemperatures.resize(307, 63)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetTemperatures)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(WidgetTemperatures)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.verticalLayout.addWidget(self.groupBox)

        self.retranslateUi(WidgetTemperatures)
        QtCore.QMetaObject.connectSlotsByName(WidgetTemperatures)

    def retranslateUi(self, WidgetTemperatures):
        _translate = QtCore.QCoreApplication.translate
        WidgetTemperatures.setWindowTitle(_translate("WidgetTemperatures", "Form"))
        self.groupBox.setTitle(_translate("WidgetTemperatures", "Temperatures"))

