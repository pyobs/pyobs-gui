# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'modewidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QLabel,
    QLineEdit, QSizePolicy, QVBoxLayout, QWidget)
from . import resources_rc

class Ui_ModeWidget(object):
    def setupUi(self, ModeWidget):
        if not ModeWidget.objectName():
            ModeWidget.setObjectName(u"ModeWidget")
        ModeWidget.resize(229, 87)
        self.verticalLayout = QVBoxLayout(ModeWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox = QGroupBox(ModeWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.label_11 = QLabel(self.groupBox)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.textStatus = QLineEdit(self.groupBox)
        self.textStatus.setObjectName(u"textStatus")
        self.textStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textStatus.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.textStatus)


        self.verticalLayout.addWidget(self.groupBox)


        self.retranslateUi(ModeWidget)

        QMetaObject.connectSlotsByName(ModeWidget)
    # setupUi

    def retranslateUi(self, ModeWidget):
        ModeWidget.setWindowTitle(QCoreApplication.translate("ModeWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("ModeWidget", u"Modes", None))
        self.label_11.setText(QCoreApplication.translate("ModeWidget", u"Status:", None))
    # retranslateUi

