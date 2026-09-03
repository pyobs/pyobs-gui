# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'videowidget.ui'
##
## Created by: Qt User Interface Compiler version 6.11.2
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QFrame,
    QGridLayout, QGroupBox, QHBoxLayout, QLabel,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_VideoWidget(object):
    def setupUi(self, VideoWidget):
        if not VideoWidget.objectName():
            VideoWidget.setObjectName(u"VideoWidget")
        VideoWidget.resize(618, 530)
        self.horizontalLayout = QHBoxLayout(VideoWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame = QFrame(VideoWidget)
        self.frame.setObjectName(u"frame")
        self.frame.setFrameShape(QFrame.Shape.StyledPanel)
        self.frame.setFrameShadow(QFrame.Shadow.Raised)
        self.verticalLayout_2 = QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.groupExposure = QGroupBox(self.frame)
        self.groupExposure.setObjectName(u"groupExposure")
        self.formLayout = QFormLayout(self.groupExposure)
        self.formLayout.setObjectName(u"formLayout")
        self.spinExpTime = QDoubleSpinBox(self.groupExposure)
        self.spinExpTime.setObjectName(u"spinExpTime")
        self.spinExpTime.setDecimals(6)
        self.spinExpTime.setMaximum(999.000000000000000)
        self.spinExpTime.setValue(1.000000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinExpTime)

        self.labelExpTime = QLabel(self.groupExposure)
        self.labelExpTime.setObjectName(u"labelExpTime")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelExpTime)


        self.verticalLayout_2.addWidget(self.groupExposure)

        self.groupGain = QGroupBox(self.frame)
        self.groupGain.setObjectName(u"groupGain")
        self.gridLayout = QGridLayout(self.groupGain)
        self.gridLayout.setObjectName(u"gridLayout")
        self.label_11 = QLabel(self.groupGain)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout.addWidget(self.label_11, 0, 0, 1, 1)

        self.spinGain = QDoubleSpinBox(self.groupGain)
        self.spinGain.setObjectName(u"spinGain")

        self.gridLayout.addWidget(self.spinGain, 0, 1, 1, 1)


        self.verticalLayout_2.addWidget(self.groupGain)

        self.verticalSpacer = QSpacerItem(20, 340, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)


        self.horizontalLayout.addWidget(self.frame)

        self.frameLiveView = QWidget(VideoWidget)
        self.frameLiveView.setObjectName(u"frameLiveView")
        self.verticalLayout_4 = QVBoxLayout(self.frameLiveView)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")

        self.horizontalLayout.addWidget(self.frameLiveView)

        self.horizontalLayout.setStretch(1, 1)

        self.retranslateUi(VideoWidget)

        QMetaObject.connectSlotsByName(VideoWidget)
    # setupUi

    def retranslateUi(self, VideoWidget):
        VideoWidget.setWindowTitle(QCoreApplication.translate("VideoWidget", u"Form", None))
        self.groupExposure.setTitle("")
        self.spinExpTime.setSuffix(QCoreApplication.translate("VideoWidget", u" s", None))
        self.labelExpTime.setText(QCoreApplication.translate("VideoWidget", u"ExpTime:", None))
        self.groupGain.setTitle("")
        self.label_11.setText(QCoreApplication.translate("VideoWidget", u"Gain:", None))
    # retranslateUi

