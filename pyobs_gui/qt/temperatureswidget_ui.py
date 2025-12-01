# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'temperatureswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QFrame, QGroupBox,
    QSizePolicy, QToolButton, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_TemperaturesWidget(object):
    def setupUi(self, TemperaturesWidget):
        if not TemperaturesWidget.objectName():
            TemperaturesWidget.setObjectName(u"TemperaturesWidget")
        TemperaturesWidget.resize(269, 164)
        self.verticalLayout = QVBoxLayout(TemperaturesWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox = QGroupBox(TemperaturesWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.frame = QFrame(self.groupBox)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QFrame.Shadow.Plain)
        self.formLayout = QFormLayout(self.frame)
        self.formLayout.setObjectName(u"formLayout")

        self.verticalLayout_2.addWidget(self.frame)

        self.buttonPlotTemps = QToolButton(self.groupBox)
        self.buttonPlotTemps.setObjectName(u"buttonPlotTemps")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.buttonPlotTemps.sizePolicy().hasHeightForWidth())
        self.buttonPlotTemps.setSizePolicy(sizePolicy)
        icon = QIcon()
        icon.addFile(u":/resources/chart-line-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonPlotTemps.setIcon(icon)
        self.buttonPlotTemps.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.verticalLayout_2.addWidget(self.buttonPlotTemps)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(TemperaturesWidget)

        QMetaObject.connectSlotsByName(TemperaturesWidget)
    # setupUi

    def retranslateUi(self, TemperaturesWidget):
        TemperaturesWidget.setWindowTitle(QCoreApplication.translate("TemperaturesWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("TemperaturesWidget", u"Temperatures", None))
        self.buttonPlotTemps.setText(QCoreApplication.translate("TemperaturesWidget", u"Plot && log temperatures", None))
    # retranslateUi

