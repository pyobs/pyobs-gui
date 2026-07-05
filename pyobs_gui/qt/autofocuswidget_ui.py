# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'autofocuswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QFrame,
    QGroupBox, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QSizePolicy, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_AutoFocusWidget(object):
    def setupUi(self, AutoFocusWidget):
        if not AutoFocusWidget.objectName():
            AutoFocusWidget.setObjectName(u"AutoFocusWidget")
        AutoFocusWidget.resize(350, 350)
        self.verticalLayout = QVBoxLayout(AutoFocusWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.framePlot = QFrame(AutoFocusWidget)
        self.framePlot.setObjectName(u"framePlot")
        self.framePlot.setFrameShape(QFrame.Shape.NoFrame)
        self.framePlot.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.framePlot)

        self.groupBox = QGroupBox(AutoFocusWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.spinCount = QSpinBox(self.groupBox)
        self.spinCount.setObjectName(u"spinCount")
        self.spinCount.setMinimum(1)
        self.spinCount.setMaximum(20)
        self.spinCount.setValue(5)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.spinCount)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.spinStep = QDoubleSpinBox(self.groupBox)
        self.spinStep.setObjectName(u"spinStep")
        self.spinStep.setDecimals(3)
        self.spinStep.setMinimum(0.001000000000000)
        self.spinStep.setMaximum(10.000000000000000)
        self.spinStep.setValue(0.100000000000000)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinStep)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.spinExposureTime = QDoubleSpinBox(self.groupBox)
        self.spinExposureTime.setObjectName(u"spinExposureTime")
        self.spinExposureTime.setDecimals(1)
        self.spinExposureTime.setMinimum(0.100000000000000)
        self.spinExposureTime.setMaximum(3600.000000000000000)
        self.spinExposureTime.setValue(2.000000000000000)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.spinExposureTime)


        self.verticalLayout.addWidget(self.groupBox)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.buttonRunAutoFocus = QPushButton(AutoFocusWidget)
        self.buttonRunAutoFocus.setObjectName(u"buttonRunAutoFocus")

        self.horizontalLayout.addWidget(self.buttonRunAutoFocus)

        self.buttonAbort = QPushButton(AutoFocusWidget)
        self.buttonAbort.setObjectName(u"buttonAbort")

        self.horizontalLayout.addWidget(self.buttonAbort)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.labelStatus = QLineEdit(AutoFocusWidget)
        self.labelStatus.setObjectName(u"labelStatus")
        self.labelStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelStatus.setReadOnly(True)

        self.verticalLayout.addWidget(self.labelStatus)

        self.verticalLayout.setStretch(0, 1)
        QWidget.setTabOrder(self.spinCount, self.spinStep)
        QWidget.setTabOrder(self.spinStep, self.spinExposureTime)
        QWidget.setTabOrder(self.spinExposureTime, self.buttonRunAutoFocus)
        QWidget.setTabOrder(self.buttonRunAutoFocus, self.buttonAbort)
        QWidget.setTabOrder(self.buttonAbort, self.labelStatus)

        self.retranslateUi(AutoFocusWidget)

        QMetaObject.connectSlotsByName(AutoFocusWidget)
    # setupUi

    def retranslateUi(self, AutoFocusWidget):
        AutoFocusWidget.setWindowTitle(QCoreApplication.translate("AutoFocusWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("AutoFocusWidget", u"Auto Focus", None))
        self.label.setText(QCoreApplication.translate("AutoFocusWidget", u"Count:", None))
        self.label_2.setText(QCoreApplication.translate("AutoFocusWidget", u"Step:", None))
        self.spinStep.setSuffix(QCoreApplication.translate("AutoFocusWidget", u" mm", None))
        self.label_3.setText(QCoreApplication.translate("AutoFocusWidget", u"Exposure time:", None))
        self.spinExposureTime.setSuffix(QCoreApplication.translate("AutoFocusWidget", u" s", None))
        self.buttonRunAutoFocus.setText(QCoreApplication.translate("AutoFocusWidget", u"Run auto-focus", None))
        self.buttonAbort.setText(QCoreApplication.translate("AutoFocusWidget", u"Abort", None))
    # retranslateUi

