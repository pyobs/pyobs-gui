# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'filterwidget.ui'
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
from PySide6.QtWidgets import (QApplication, QFormLayout, QGroupBox, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QToolButton,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_FilterWidget(object):
    def setupUi(self, FilterWidget):
        if not FilterWidget.objectName():
            FilterWidget.setObjectName(u"FilterWidget")
        FilterWidget.resize(229, 128)
        self.verticalLayout = QVBoxLayout(FilterWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.groupBox_2 = QGroupBox(FilterWidget)
        self.groupBox_2.setObjectName(u"groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName(u"formLayout")
        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName(u"label_9")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.textFilter = QLineEdit(self.groupBox_2)
        self.textFilter.setObjectName(u"textFilter")
        self.textFilter.setAlignment(Qt.AlignCenter)
        self.textFilter.setReadOnly(True)

        self.horizontalLayout.addWidget(self.textFilter)

        self.buttonSetFilter = QToolButton(self.groupBox_2)
        self.buttonSetFilter.setObjectName(u"buttonSetFilter")
        icon = QIcon()
        icon.addFile(u":/resources/edit-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonSetFilter.setIcon(icon)

        self.horizontalLayout.addWidget(self.buttonSetFilter)


        self.formLayout.setLayout(0, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.textStatus = QLineEdit(self.groupBox_2)
        self.textStatus.setObjectName(u"textStatus")
        self.textStatus.setAlignment(Qt.AlignCenter)
        self.textStatus.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.textStatus)


        self.verticalLayout.addWidget(self.groupBox_2)


        self.retranslateUi(FilterWidget)

        QMetaObject.connectSlotsByName(FilterWidget)
    # setupUi

    def retranslateUi(self, FilterWidget):
        FilterWidget.setWindowTitle(QCoreApplication.translate("FilterWidget", u"Form", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("FilterWidget", u"Filter", None))
        self.label_9.setText(QCoreApplication.translate("FilterWidget", u"Filter:", None))
        self.buttonSetFilter.setText(QCoreApplication.translate("FilterWidget", u"set...", None))
        self.label_11.setText(QCoreApplication.translate("FilterWidget", u"Status:", None))
    # retranslateUi

