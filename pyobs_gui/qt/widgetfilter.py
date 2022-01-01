# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetfilter.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from . import resources_rc


class Ui_WidgetFilter(object):
    def setupUi(self, WidgetFilter):
        if not WidgetFilter.objectName():
            WidgetFilter.setObjectName("WidgetFilter")
        WidgetFilter.resize(229, 126)
        self.verticalLayout = QVBoxLayout(WidgetFilter)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_2 = QGroupBox(WidgetFilter)
        self.groupBox_2.setObjectName("groupBox_2")
        self.formLayout = QFormLayout(self.groupBox_2)
        self.formLayout.setObjectName("formLayout")
        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_9)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textFilter = QLineEdit(self.groupBox_2)
        self.textFilter.setObjectName("textFilter")
        self.textFilter.setAlignment(Qt.AlignCenter)
        self.textFilter.setReadOnly(True)

        self.horizontalLayout.addWidget(self.textFilter)

        self.buttonSetFilter = QToolButton(self.groupBox_2)
        self.buttonSetFilter.setObjectName("buttonSetFilter")
        icon = QIcon()
        icon.addFile(":/resources/edit-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.buttonSetFilter.setIcon(icon)

        self.horizontalLayout.addWidget(self.buttonSetFilter)

        self.formLayout.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout)

        self.label_11 = QLabel(self.groupBox_2)
        self.label_11.setObjectName("label_11")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_11)

        self.textStatus = QLineEdit(self.groupBox_2)
        self.textStatus.setObjectName("textStatus")
        self.textStatus.setAlignment(Qt.AlignCenter)
        self.textStatus.setReadOnly(True)

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.textStatus)

        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(WidgetFilter)

        QMetaObject.connectSlotsByName(WidgetFilter)

    # setupUi

    def retranslateUi(self, WidgetFilter):
        WidgetFilter.setWindowTitle(QCoreApplication.translate("WidgetFilter", "Form", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("WidgetFilter", "Filter", None))
        self.label_9.setText(QCoreApplication.translate("WidgetFilter", "Filter:", None))
        self.buttonSetFilter.setText(QCoreApplication.translate("WidgetFilter", "set...", None))
        self.label_11.setText(QCoreApplication.translate("WidgetFilter", "Status:", None))

    # retranslateUi
