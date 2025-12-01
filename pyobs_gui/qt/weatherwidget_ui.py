# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'weatherwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_WeatherWidget(object):
    def setupUi(self, WeatherWidget):
        if not WeatherWidget.objectName():
            WeatherWidget.setObjectName(u"WeatherWidget")
        WeatherWidget.resize(719, 552)
        self.verticalLayout_2 = QVBoxLayout(WeatherWidget)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frameCurrent = QFrame(WeatherWidget)
        self.frameCurrent.setObjectName(u"frameCurrent")
        self.frameCurrent.setFrameShape(QFrame.Shape.StyledPanel)
        self.frameCurrent.setFrameShadow(QFrame.Shadow.Raised)
        self.horizontalLayout = QHBoxLayout(self.frameCurrent)
        self.horizontalLayout.setObjectName(u"horizontalLayout")

        self.verticalLayout_2.addWidget(self.frameCurrent)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frameSensor = QFrame(WeatherWidget)
        self.frameSensor.setObjectName(u"frameSensor")
        self.frameSensor.setFrameShape(QFrame.Shape.StyledPanel)
        self.frameSensor.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout = QVBoxLayout(self.frameSensor)
        self.verticalLayout.setObjectName(u"verticalLayout")

        self.horizontalLayout_2.addWidget(self.frameSensor)

        self.framePlot = QFrame(WeatherWidget)
        self.framePlot.setObjectName(u"framePlot")
        self.framePlot.setFrameShape(QFrame.Shape.StyledPanel)
        self.framePlot.setFrameShadow(QFrame.Shadow.Raised)

        self.horizontalLayout_2.addWidget(self.framePlot)

        self.horizontalLayout_2.setStretch(1, 1)

        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.verticalLayout_2.setStretch(1, 1)

        self.retranslateUi(WeatherWidget)

        QMetaObject.connectSlotsByName(WeatherWidget)
    # setupUi

    def retranslateUi(self, WeatherWidget):
        WeatherWidget.setWindowTitle(QCoreApplication.translate("WeatherWidget", u"Form", None))
    # retranslateUi

