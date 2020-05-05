# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetweather.ui'
#
# Created by: PyQt5 UI code generator 5.13.0
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_widgetWeather(object):
    def setupUi(self, widgetWeather):
        widgetWeather.setObjectName("widgetWeather")
        widgetWeather.resize(972, 782)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(widgetWeather)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frameCurrent = QtWidgets.QFrame(widgetWeather)
        self.frameCurrent.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameCurrent.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameCurrent.setObjectName("frameCurrent")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.frameCurrent)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_2.addWidget(self.frameCurrent)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frameSensor = QtWidgets.QFrame(widgetWeather)
        self.frameSensor.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frameSensor.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frameSensor.setObjectName("frameSensor")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.frameSensor)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2.addWidget(self.frameSensor)
        self.framePlot = QtWidgets.QFrame(widgetWeather)
        self.framePlot.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.framePlot.setFrameShadow(QtWidgets.QFrame.Raised)
        self.framePlot.setObjectName("framePlot")
        self.horizontalLayout_2.addWidget(self.framePlot)
        self.horizontalLayout_2.setStretch(1, 1)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout_2.setStretch(1, 1)

        self.retranslateUi(widgetWeather)
        QtCore.QMetaObject.connectSlotsByName(widgetWeather)

    def retranslateUi(self, widgetWeather):
        _translate = QtCore.QCoreApplication.translate
        widgetWeather.setWindowTitle(_translate("widgetWeather", "Form"))
