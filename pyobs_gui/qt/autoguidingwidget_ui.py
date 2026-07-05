# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'autoguidingwidget.ui'
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
    QHBoxLayout, QLabel, QLineEdit, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

from ..modifiedmixin import ModifiedDoubleSpinBox
from ..watchedlabel import WatchedLabel

class Ui_AutoGuidingWidget(object):
    def setupUi(self, AutoGuidingWidget):
        if not AutoGuidingWidget.objectName():
            AutoGuidingWidget.setObjectName(u"AutoGuidingWidget")
        AutoGuidingWidget.resize(320, 220)
        self.verticalLayout = QVBoxLayout(AutoGuidingWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.framePlot = QFrame(AutoGuidingWidget)
        self.framePlot.setObjectName(u"framePlot")
        self.framePlot.setFrameShape(QFrame.Shape.NoFrame)
        self.framePlot.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.framePlot)

        self.groupBox = QGroupBox(AutoGuidingWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.verticalLayout_2 = QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.buttonStart = QPushButton(self.groupBox)
        self.buttonStart.setObjectName(u"buttonStart")

        self.horizontalLayout.addWidget(self.buttonStart)

        self.buttonStop = QPushButton(self.groupBox)
        self.buttonStop.setObjectName(u"buttonStop")

        self.horizontalLayout.addWidget(self.buttonStop)


        self.verticalLayout_2.addLayout(self.horizontalLayout)

        self.labelLoopState = QLineEdit(self.groupBox)
        self.labelLoopState.setObjectName(u"labelLoopState")
        self.labelLoopState.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelLoopState.setReadOnly(True)

        self.verticalLayout_2.addWidget(self.labelLoopState)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelExposureTime = WatchedLabel(self.groupBox)
        self.labelExposureTime.setObjectName(u"labelExposureTime")
        self.labelExposureTime.setFrameShape(QFrame.Shape.NoFrame)

        self.horizontalLayout_2.addWidget(self.labelExposureTime)

        self.spinExposureTime = ModifiedDoubleSpinBox(self.groupBox)
        self.spinExposureTime.setObjectName(u"spinExposureTime")
        self.spinExposureTime.setDecimals(1)
        self.spinExposureTime.setMinimum(0.100000000000000)
        self.spinExposureTime.setMaximum(3600.000000000000000)

        self.horizontalLayout_2.addWidget(self.spinExposureTime)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.labelOffset = QLineEdit(self.groupBox)
        self.labelOffset.setObjectName(u"labelOffset")
        self.labelOffset.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelOffset.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.labelOffset)


        self.verticalLayout_2.addLayout(self.formLayout)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalLayout.setStretch(0, 1)
        QWidget.setTabOrder(self.buttonStart, self.buttonStop)
        QWidget.setTabOrder(self.buttonStop, self.spinExposureTime)

        self.retranslateUi(AutoGuidingWidget)

        QMetaObject.connectSlotsByName(AutoGuidingWidget)
    # setupUi

    def retranslateUi(self, AutoGuidingWidget):
        AutoGuidingWidget.setWindowTitle(QCoreApplication.translate("AutoGuidingWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("AutoGuidingWidget", u"Auto Guiding", None))
        self.buttonStart.setText(QCoreApplication.translate("AutoGuidingWidget", u"Start", None))
        self.buttonStop.setText(QCoreApplication.translate("AutoGuidingWidget", u"Stop", None))
        self.label.setText(QCoreApplication.translate("AutoGuidingWidget", u"Exposure time:", None))
        self.labelExposureTime.setText(QCoreApplication.translate("AutoGuidingWidget", u"-", None))
        self.spinExposureTime.setSuffix(QCoreApplication.translate("AutoGuidingWidget", u" s", None))
        self.label_2.setText(QCoreApplication.translate("AutoGuidingWidget", u"Last offset:", None))
    # retranslateUi

