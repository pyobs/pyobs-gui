# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetweather.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_widgetWeather(object):
    def setupUi(self, widgetWeather):
        if not widgetWeather.objectName():
            widgetWeather.setObjectName("widgetWeather")
        widgetWeather.resize(972, 782)
        self.verticalLayout_2 = QVBoxLayout(widgetWeather)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.frameCurrent = QFrame(widgetWeather)
        self.frameCurrent.setObjectName("frameCurrent")
        self.frameCurrent.setFrameShape(QFrame.StyledPanel)
        self.frameCurrent.setFrameShadow(QFrame.Raised)
        self.horizontalLayout = QHBoxLayout(self.frameCurrent)
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.verticalLayout_2.addWidget(self.frameCurrent)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.frameSensor = QFrame(widgetWeather)
        self.frameSensor.setObjectName("frameSensor")
        self.frameSensor.setFrameShape(QFrame.StyledPanel)
        self.frameSensor.setFrameShadow(QFrame.Raised)
        self.verticalLayout = QVBoxLayout(self.frameSensor)
        self.verticalLayout.setObjectName("verticalLayout")

        self.horizontalLayout_2.addWidget(self.frameSensor)

        self.framePlot = QFrame(widgetWeather)
        self.framePlot.setObjectName("framePlot")
        self.framePlot.setFrameShape(QFrame.StyledPanel)
        self.framePlot.setFrameShadow(QFrame.Raised)

        self.horizontalLayout_2.addWidget(self.framePlot)

        self.horizontalLayout_2.setStretch(1, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout_2.setStretch(1, 1)

        self.retranslateUi(widgetWeather)

        QMetaObject.connectSlotsByName(widgetWeather)

    # setupUi

    def retranslateUi(self, widgetWeather):
        widgetWeather.setWindowTitle(QCoreApplication.translate("widgetWeather", "Form", None))

    # retranslateUi
