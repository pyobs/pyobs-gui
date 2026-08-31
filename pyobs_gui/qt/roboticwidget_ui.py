# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'roboticwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QSizePolicy,
    QSpacerItem, QVBoxLayout, QWidget)

class Ui_RoboticWidget(object):
    def setupUi(self, RoboticWidget):
        if not RoboticWidget.objectName():
            RoboticWidget.setObjectName(u"RoboticWidget")
        RoboticWidget.resize(400, 420)
        self.verticalLayout = QVBoxLayout(RoboticWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.buttonStart = QPushButton(RoboticWidget)
        self.buttonStart.setObjectName(u"buttonStart")

        self.horizontalLayout.addWidget(self.buttonStart)

        self.buttonStop = QPushButton(RoboticWidget)
        self.buttonStop.setObjectName(u"buttonStop")

        self.horizontalLayout.addWidget(self.buttonStop)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.labelStatus = QLineEdit(RoboticWidget)
        self.labelStatus.setObjectName(u"labelStatus")
        self.labelStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelStatus.setReadOnly(True)

        self.verticalLayout.addWidget(self.labelStatus)

        self.groupCurrent = QGroupBox(RoboticWidget)
        self.groupCurrent.setObjectName(u"groupCurrent")
        self.formCurrent = QFormLayout(self.groupCurrent)
        self.formCurrent.setObjectName(u"formCurrent")
        self.label_1 = QLabel(self.groupCurrent)
        self.label_1.setObjectName(u"label_1")

        self.formCurrent.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_1)

        self.textCurrentName = QLineEdit(self.groupCurrent)
        self.textCurrentName.setObjectName(u"textCurrentName")
        self.textCurrentName.setReadOnly(True)

        self.formCurrent.setWidget(0, QFormLayout.ItemRole.FieldRole, self.textCurrentName)

        self.label_2 = QLabel(self.groupCurrent)
        self.label_2.setObjectName(u"label_2")

        self.formCurrent.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.textCurrentTarget = QLineEdit(self.groupCurrent)
        self.textCurrentTarget.setObjectName(u"textCurrentTarget")
        self.textCurrentTarget.setReadOnly(True)

        self.formCurrent.setWidget(1, QFormLayout.ItemRole.FieldRole, self.textCurrentTarget)

        self.label_3 = QLabel(self.groupCurrent)
        self.label_3.setObjectName(u"label_3")

        self.formCurrent.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.textCurrentObsnum = QLineEdit(self.groupCurrent)
        self.textCurrentObsnum.setObjectName(u"textCurrentObsnum")
        self.textCurrentObsnum.setReadOnly(True)

        self.formCurrent.setWidget(2, QFormLayout.ItemRole.FieldRole, self.textCurrentObsnum)

        self.label_4 = QLabel(self.groupCurrent)
        self.label_4.setObjectName(u"label_4")

        self.formCurrent.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.textCurrentStart = QLineEdit(self.groupCurrent)
        self.textCurrentStart.setObjectName(u"textCurrentStart")
        self.textCurrentStart.setReadOnly(True)

        self.formCurrent.setWidget(3, QFormLayout.ItemRole.FieldRole, self.textCurrentStart)

        self.label_5 = QLabel(self.groupCurrent)
        self.label_5.setObjectName(u"label_5")

        self.formCurrent.setWidget(4, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.textCurrentEta = QLineEdit(self.groupCurrent)
        self.textCurrentEta.setObjectName(u"textCurrentEta")
        self.textCurrentEta.setReadOnly(True)

        self.formCurrent.setWidget(4, QFormLayout.ItemRole.FieldRole, self.textCurrentEta)


        self.verticalLayout.addWidget(self.groupCurrent)

        self.groupNext = QGroupBox(RoboticWidget)
        self.groupNext.setObjectName(u"groupNext")
        self.formNext = QFormLayout(self.groupNext)
        self.formNext.setObjectName(u"formNext")
        self.label_6 = QLabel(self.groupNext)
        self.label_6.setObjectName(u"label_6")

        self.formNext.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.textNextName = QLineEdit(self.groupNext)
        self.textNextName.setObjectName(u"textNextName")
        self.textNextName.setReadOnly(True)

        self.formNext.setWidget(0, QFormLayout.ItemRole.FieldRole, self.textNextName)

        self.label_7 = QLabel(self.groupNext)
        self.label_7.setObjectName(u"label_7")

        self.formNext.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.textNextTarget = QLineEdit(self.groupNext)
        self.textNextTarget.setObjectName(u"textNextTarget")
        self.textNextTarget.setReadOnly(True)

        self.formNext.setWidget(1, QFormLayout.ItemRole.FieldRole, self.textNextTarget)

        self.label_8 = QLabel(self.groupNext)
        self.label_8.setObjectName(u"label_8")

        self.formNext.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.textNextStart = QLineEdit(self.groupNext)
        self.textNextStart.setObjectName(u"textNextStart")
        self.textNextStart.setReadOnly(True)

        self.formNext.setWidget(2, QFormLayout.ItemRole.FieldRole, self.textNextStart)

        self.label_9 = QLabel(self.groupNext)
        self.label_9.setObjectName(u"label_9")

        self.formNext.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.textCantRunReason = QLineEdit(self.groupNext)
        self.textCantRunReason.setObjectName(u"textCantRunReason")
        self.textCantRunReason.setReadOnly(True)

        self.formNext.setWidget(3, QFormLayout.ItemRole.FieldRole, self.textCantRunReason)


        self.verticalLayout.addWidget(self.groupNext)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)

        QWidget.setTabOrder(self.buttonStart, self.buttonStop)

        self.retranslateUi(RoboticWidget)

        QMetaObject.connectSlotsByName(RoboticWidget)
    # setupUi

    def retranslateUi(self, RoboticWidget):
        RoboticWidget.setWindowTitle(QCoreApplication.translate("RoboticWidget", u"Form", None))
        self.buttonStart.setText(QCoreApplication.translate("RoboticWidget", u"Start", None))
        self.buttonStop.setText(QCoreApplication.translate("RoboticWidget", u"Stop", None))
        self.groupCurrent.setTitle(QCoreApplication.translate("RoboticWidget", u"Current task", None))
        self.label_1.setText(QCoreApplication.translate("RoboticWidget", u"Name:", None))
        self.label_2.setText(QCoreApplication.translate("RoboticWidget", u"Target:", None))
        self.label_3.setText(QCoreApplication.translate("RoboticWidget", u"Obsnum:", None))
        self.label_4.setText(QCoreApplication.translate("RoboticWidget", u"Started:", None))
        self.label_5.setText(QCoreApplication.translate("RoboticWidget", u"ETA:", None))
        self.groupNext.setTitle(QCoreApplication.translate("RoboticWidget", u"Next up", None))
        self.label_6.setText(QCoreApplication.translate("RoboticWidget", u"Name:", None))
        self.label_7.setText(QCoreApplication.translate("RoboticWidget", u"Target:", None))
        self.label_8.setText(QCoreApplication.translate("RoboticWidget", u"Start:", None))
        self.label_9.setText(QCoreApplication.translate("RoboticWidget", u"Waiting for:", None))
    # retranslateUi

