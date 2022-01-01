# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetfitsheaders.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_WidgetFitsHeaders(object):
    def setupUi(self, WidgetFitsHeaders):
        if not WidgetFitsHeaders.objectName():
            WidgetFitsHeaders.setObjectName("WidgetFitsHeaders")
        WidgetFitsHeaders.resize(259, 427)
        self.horizontalLayout = QHBoxLayout(WidgetFitsHeaders)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QGroupBox(WidgetFitsHeaders)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.checkAddHeaders = QCheckBox(self.groupBox)
        self.checkAddHeaders.setObjectName("checkAddHeaders")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.checkAddHeaders)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName("label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label)

        self.textObject = QLineEdit(self.groupBox)
        self.textObject.setObjectName("textObject")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.textObject)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_3)

        self.textUser = QLineEdit(self.groupBox)
        self.textUser.setObjectName("textUser")

        self.formLayout.setWidget(2, QFormLayout.FieldRole, self.textUser)

        self.tableAdditionalHeaders = QTableWidget(self.groupBox)
        if self.tableAdditionalHeaders.columnCount() < 2:
            self.tableAdditionalHeaders.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableAdditionalHeaders.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableAdditionalHeaders.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tableAdditionalHeaders.setObjectName("tableAdditionalHeaders")
        self.tableAdditionalHeaders.setColumnCount(2)
        self.tableAdditionalHeaders.horizontalHeader().setDefaultSectionSize(50)
        self.tableAdditionalHeaders.horizontalHeader().setStretchLastSection(True)
        self.tableAdditionalHeaders.verticalHeader().setVisible(False)

        self.formLayout.setWidget(3, QFormLayout.SpanningRole, self.tableAdditionalHeaders)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.buttonAddHeader = QToolButton(self.groupBox)
        self.buttonAddHeader.setObjectName("buttonAddHeader")

        self.horizontalLayout_2.addWidget(self.buttonAddHeader)

        self.buttonDelHeader = QToolButton(self.groupBox)
        self.buttonDelHeader.setObjectName("buttonDelHeader")

        self.horizontalLayout_2.addWidget(self.buttonDelHeader)

        self.formLayout.setLayout(4, QFormLayout.SpanningRole, self.horizontalLayout_2)

        self.horizontalLayout.addWidget(self.groupBox)

        self.retranslateUi(WidgetFitsHeaders)

        QMetaObject.connectSlotsByName(WidgetFitsHeaders)

    # setupUi

    def retranslateUi(self, WidgetFitsHeaders):
        WidgetFitsHeaders.setWindowTitle(QCoreApplication.translate("WidgetFitsHeaders", "Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("WidgetFitsHeaders", "FITS headers", None))
        self.checkAddHeaders.setText(QCoreApplication.translate("WidgetFitsHeaders", "Add headers", None))
        self.label.setText(QCoreApplication.translate("WidgetFitsHeaders", "OBJECT:", None))
        self.label_3.setText(QCoreApplication.translate("WidgetFitsHeaders", "USER:", None))
        ___qtablewidgetitem = self.tableAdditionalHeaders.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("WidgetFitsHeaders", "Key", None))
        ___qtablewidgetitem1 = self.tableAdditionalHeaders.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("WidgetFitsHeaders", "Value", None))
        self.buttonAddHeader.setText(QCoreApplication.translate("WidgetFitsHeaders", "+", None))
        self.buttonDelHeader.setText(QCoreApplication.translate("WidgetFitsHeaders", "-", None))

    # retranslateUi
