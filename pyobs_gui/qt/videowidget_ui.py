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
from PySide6.QtWidgets import (QApplication, QComboBox, QDoubleSpinBox, QFormLayout,
    QFrame, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QSizePolicy, QSpacerItem, QSpinBox,
    QVBoxLayout, QWidget)

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

        self.groupLiveView = QGroupBox(self.frame)
        self.groupLiveView.setObjectName(u"groupLiveView")
        self.formLayoutLiveView = QFormLayout(self.groupLiveView)
        self.formLayoutLiveView.setObjectName(u"formLayoutLiveView")
        self.labelMode = QLabel(self.groupLiveView)
        self.labelMode.setObjectName(u"labelMode")

        self.formLayoutLiveView.setWidget(0, QFormLayout.ItemRole.LabelRole, self.labelMode)

        self.comboMode = QComboBox(self.groupLiveView)
        self.comboMode.setObjectName(u"comboMode")

        self.formLayoutLiveView.setWidget(0, QFormLayout.ItemRole.FieldRole, self.comboMode)

        self.labelStretch = QLabel(self.groupLiveView)
        self.labelStretch.setObjectName(u"labelStretch")

        self.formLayoutLiveView.setWidget(1, QFormLayout.ItemRole.LabelRole, self.labelStretch)

        self.comboStretch = QComboBox(self.groupLiveView)
        self.comboStretch.setObjectName(u"comboStretch")

        self.formLayoutLiveView.setWidget(1, QFormLayout.ItemRole.FieldRole, self.comboStretch)

        self.labelCuts = QLabel(self.groupLiveView)
        self.labelCuts.setObjectName(u"labelCuts")

        self.formLayoutLiveView.setWidget(2, QFormLayout.ItemRole.LabelRole, self.labelCuts)

        self.comboCuts = QComboBox(self.groupLiveView)
        self.comboCuts.setObjectName(u"comboCuts")

        self.formLayoutLiveView.setWidget(2, QFormLayout.ItemRole.FieldRole, self.comboCuts)

        self.labelLo = QLabel(self.groupLiveView)
        self.labelLo.setObjectName(u"labelLo")

        self.formLayoutLiveView.setWidget(3, QFormLayout.ItemRole.LabelRole, self.labelLo)

        self.spinLo = QDoubleSpinBox(self.groupLiveView)
        self.spinLo.setObjectName(u"spinLo")
        self.spinLo.setDecimals(2)
        self.spinLo.setMinimum(-1000000000.000000000000000)
        self.spinLo.setMaximum(1000000000.000000000000000)
        self.spinLo.setValue(0.500000000000000)

        self.formLayoutLiveView.setWidget(3, QFormLayout.ItemRole.FieldRole, self.spinLo)

        self.labelHi = QLabel(self.groupLiveView)
        self.labelHi.setObjectName(u"labelHi")

        self.formLayoutLiveView.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelHi)

        self.spinHi = QDoubleSpinBox(self.groupLiveView)
        self.spinHi.setObjectName(u"spinHi")
        self.spinHi.setDecimals(2)
        self.spinHi.setMinimum(-1000000000.000000000000000)
        self.spinHi.setMaximum(1000000000.000000000000000)
        self.spinHi.setValue(99.500000000000000)

        self.formLayoutLiveView.setWidget(4, QFormLayout.ItemRole.FieldRole, self.spinHi)

        self.labelQuality = QLabel(self.groupLiveView)
        self.labelQuality.setObjectName(u"labelQuality")

        self.formLayoutLiveView.setWidget(5, QFormLayout.ItemRole.LabelRole, self.labelQuality)

        self.spinQuality = QSpinBox(self.groupLiveView)
        self.spinQuality.setObjectName(u"spinQuality")
        self.spinQuality.setMinimum(0)
        self.spinQuality.setMaximum(95)
        self.spinQuality.setValue(0)

        self.formLayoutLiveView.setWidget(5, QFormLayout.ItemRole.FieldRole, self.spinQuality)

        self.labelMaxRate = QLabel(self.groupLiveView)
        self.labelMaxRate.setObjectName(u"labelMaxRate")

        self.formLayoutLiveView.setWidget(6, QFormLayout.ItemRole.LabelRole, self.labelMaxRate)

        self.spinMaxRate = QDoubleSpinBox(self.groupLiveView)
        self.spinMaxRate.setObjectName(u"spinMaxRate")
        self.spinMaxRate.setDecimals(1)
        self.spinMaxRate.setMinimum(0.000000000000000)
        self.spinMaxRate.setMaximum(60.000000000000000)
        self.spinMaxRate.setValue(5.000000000000000)

        self.formLayoutLiveView.setWidget(6, QFormLayout.ItemRole.FieldRole, self.spinMaxRate)


        self.verticalLayout_2.addWidget(self.groupLiveView)

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
        self.groupLiveView.setTitle(QCoreApplication.translate("VideoWidget", u"Live view", None))
        self.labelMode.setText(QCoreApplication.translate("VideoWidget", u"Mode:", None))
        self.labelStretch.setText(QCoreApplication.translate("VideoWidget", u"Stretch:", None))
        self.labelCuts.setText(QCoreApplication.translate("VideoWidget", u"Cuts:", None))
        self.labelLo.setText(QCoreApplication.translate("VideoWidget", u"Lo:", None))
        self.labelHi.setText(QCoreApplication.translate("VideoWidget", u"Hi:", None))
        self.labelQuality.setText(QCoreApplication.translate("VideoWidget", u"Quality:", None))
        self.spinQuality.setSpecialValueText(QCoreApplication.translate("VideoWidget", u"default", None))
        self.labelMaxRate.setText(QCoreApplication.translate("VideoWidget", u"Max rate:", None))
        self.spinMaxRate.setSpecialValueText(QCoreApplication.translate("VideoWidget", u"unlimited", None))
        self.spinMaxRate.setSuffix(QCoreApplication.translate("VideoWidget", u" fps", None))
    # retranslateUi

