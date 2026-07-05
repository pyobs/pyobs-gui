# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'acquisitionwidget.ui'
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

class Ui_AcquisitionWidget(object):
    def setupUi(self, AcquisitionWidget):
        if not AcquisitionWidget.objectName():
            AcquisitionWidget.setObjectName(u"AcquisitionWidget")
        AcquisitionWidget.resize(350, 420)
        self.verticalLayout = QVBoxLayout(AcquisitionWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.framePlot = QFrame(AcquisitionWidget)
        self.framePlot.setObjectName(u"framePlot")
        self.framePlot.setFrameShape(QFrame.Shape.NoFrame)
        self.framePlot.setFrameShadow(QFrame.Shadow.Raised)

        self.verticalLayout.addWidget(self.framePlot)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.buttonAcquire = QPushButton(AcquisitionWidget)
        self.buttonAcquire.setObjectName(u"buttonAcquire")

        self.horizontalLayout.addWidget(self.buttonAcquire)

        self.buttonAbort = QPushButton(AcquisitionWidget)
        self.buttonAbort.setObjectName(u"buttonAbort")

        self.horizontalLayout.addWidget(self.buttonAbort)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.labelStatus = QLineEdit(AcquisitionWidget)
        self.labelStatus.setObjectName(u"labelStatus")
        self.labelStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelStatus.setReadOnly(True)

        self.verticalLayout.addWidget(self.labelStatus)

        self.groupBox = QGroupBox(AcquisitionWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.labelResultRa = QLineEdit(self.groupBox)
        self.labelResultRa.setObjectName(u"labelResultRa")
        self.labelResultRa.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelResultRa.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.labelResultRa)

        self.label_2 = QLabel(self.groupBox)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.labelResultDec = QLineEdit(self.groupBox)
        self.labelResultDec.setObjectName(u"labelResultDec")
        self.labelResultDec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelResultDec.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.labelResultDec)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.labelResultAlt = QLineEdit(self.groupBox)
        self.labelResultAlt.setObjectName(u"labelResultAlt")
        self.labelResultAlt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelResultAlt.setReadOnly(True)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.labelResultAlt)

        self.label_4 = QLabel(self.groupBox)
        self.label_4.setObjectName(u"label_4")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.labelResultAz = QLineEdit(self.groupBox)
        self.labelResultAz.setObjectName(u"labelResultAz")
        self.labelResultAz.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelResultAz.setReadOnly(True)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.labelResultAz)

        self.labelOffsetType = QLabel(self.groupBox)
        self.labelOffsetType.setObjectName(u"labelOffsetType")

        self.formLayout.setWidget(4, QFormLayout.ItemRole.LabelRole, self.labelOffsetType)

        self.labelResultOffset = QLineEdit(self.groupBox)
        self.labelResultOffset.setObjectName(u"labelResultOffset")
        self.labelResultOffset.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelResultOffset.setReadOnly(True)

        self.formLayout.setWidget(4, QFormLayout.ItemRole.FieldRole, self.labelResultOffset)


        self.verticalLayout.addWidget(self.groupBox)

        self.verticalLayout.setStretch(0, 1)
        QWidget.setTabOrder(self.buttonAcquire, self.buttonAbort)
        QWidget.setTabOrder(self.buttonAbort, self.labelStatus)

        self.retranslateUi(AcquisitionWidget)

        QMetaObject.connectSlotsByName(AcquisitionWidget)
    # setupUi

    def retranslateUi(self, AcquisitionWidget):
        AcquisitionWidget.setWindowTitle(QCoreApplication.translate("AcquisitionWidget", u"Form", None))
        self.buttonAcquire.setText(QCoreApplication.translate("AcquisitionWidget", u"Acquire target", None))
        self.buttonAbort.setText(QCoreApplication.translate("AcquisitionWidget", u"Abort", None))
        self.groupBox.setTitle(QCoreApplication.translate("AcquisitionWidget", u"Result", None))
        self.label.setText(QCoreApplication.translate("AcquisitionWidget", u"RA:", None))
        self.label_2.setText(QCoreApplication.translate("AcquisitionWidget", u"Dec:", None))
        self.label_3.setText(QCoreApplication.translate("AcquisitionWidget", u"Alt:", None))
        self.label_4.setText(QCoreApplication.translate("AcquisitionWidget", u"Az:", None))
        self.labelOffsetType.setText(QCoreApplication.translate("AcquisitionWidget", u"Offset:", None))
    # retranslateUi

