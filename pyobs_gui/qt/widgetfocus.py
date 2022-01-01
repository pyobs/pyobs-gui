# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetfocus.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from . import resources_rc


class Ui_WidgetFocus(object):
    def setupUi(self, WidgetFocus):
        if not WidgetFocus.objectName():
            WidgetFocus.setObjectName("WidgetFocus")
        WidgetFocus.resize(248, 195)
        self.verticalLayout = QVBoxLayout(WidgetFocus)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_5 = QGroupBox(WidgetFocus)
        self.groupBox_5.setObjectName("groupBox_5")
        self.formLayout = QFormLayout(self.groupBox_5)
        self.formLayout.setObjectName("formLayout")
        self.label_12 = QLabel(self.groupBox_5)
        self.label_12.setObjectName("label_12")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.label_12)

        self.labelCurFocus = QLineEdit(self.groupBox_5)
        self.labelCurFocus.setObjectName("labelCurFocus")
        sizePolicy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCurFocus.sizePolicy().hasHeightForWidth())
        self.labelCurFocus.setSizePolicy(sizePolicy)
        self.labelCurFocus.setAlignment(Qt.AlignCenter)
        self.labelCurFocus.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.labelCurFocus)

        self.label_11 = QLabel(self.groupBox_5)
        self.label_11.setObjectName("label_11")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.label_11)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelCurFocusBase = QLineEdit(self.groupBox_5)
        self.labelCurFocusBase.setObjectName("labelCurFocusBase")
        sizePolicy.setHeightForWidth(self.labelCurFocusBase.sizePolicy().hasHeightForWidth())
        self.labelCurFocusBase.setSizePolicy(sizePolicy)
        self.labelCurFocusBase.setAlignment(Qt.AlignCenter)
        self.labelCurFocusBase.setReadOnly(True)

        self.horizontalLayout.addWidget(self.labelCurFocusBase)

        self.butSetFocusBase = QToolButton(self.groupBox_5)
        self.butSetFocusBase.setObjectName("butSetFocusBase")
        icon = QIcon()
        icon.addFile(":/resources/edit-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.butSetFocusBase.setIcon(icon)

        self.horizontalLayout.addWidget(self.butSetFocusBase)

        self.formLayout.setLayout(1, QFormLayout.FieldRole, self.horizontalLayout)

        self.label_14 = QLabel(self.groupBox_5)
        self.label_14.setObjectName("label_14")

        self.formLayout.setWidget(2, QFormLayout.LabelRole, self.label_14)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelCurFocusOffset = QLineEdit(self.groupBox_5)
        self.labelCurFocusOffset.setObjectName("labelCurFocusOffset")
        sizePolicy.setHeightForWidth(self.labelCurFocusOffset.sizePolicy().hasHeightForWidth())
        self.labelCurFocusOffset.setSizePolicy(sizePolicy)
        self.labelCurFocusOffset.setAlignment(Qt.AlignCenter)
        self.labelCurFocusOffset.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.labelCurFocusOffset)

        self.butSetFocusOffset = QToolButton(self.groupBox_5)
        self.butSetFocusOffset.setObjectName("butSetFocusOffset")
        self.butSetFocusOffset.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.butSetFocusOffset)

        self.buttonResetFocusOffset = QToolButton(self.groupBox_5)
        self.buttonResetFocusOffset.setObjectName("buttonResetFocusOffset")
        icon1 = QIcon()
        icon1.addFile(":/resources/undo-solid.svg", QSize(), QIcon.Normal, QIcon.Off)
        self.buttonResetFocusOffset.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.buttonResetFocusOffset)

        self.formLayout.setLayout(2, QFormLayout.FieldRole, self.horizontalLayout_2)

        self.label_13 = QLabel(self.groupBox_5)
        self.label_13.setObjectName("label_13")

        self.formLayout.setWidget(3, QFormLayout.LabelRole, self.label_13)

        self.labelCurStatus = QLineEdit(self.groupBox_5)
        self.labelCurStatus.setObjectName("labelCurStatus")
        sizePolicy.setHeightForWidth(self.labelCurStatus.sizePolicy().hasHeightForWidth())
        self.labelCurStatus.setSizePolicy(sizePolicy)
        self.labelCurStatus.setAlignment(Qt.AlignCenter)
        self.labelCurStatus.setReadOnly(True)

        self.formLayout.setWidget(3, QFormLayout.FieldRole, self.labelCurStatus)

        self.verticalLayout.addWidget(self.groupBox_5)

        QWidget.setTabOrder(self.labelCurFocus, self.labelCurFocusBase)
        QWidget.setTabOrder(self.labelCurFocusBase, self.butSetFocusBase)
        QWidget.setTabOrder(self.butSetFocusBase, self.labelCurFocusOffset)
        QWidget.setTabOrder(self.labelCurFocusOffset, self.butSetFocusOffset)
        QWidget.setTabOrder(self.butSetFocusOffset, self.labelCurStatus)

        self.retranslateUi(WidgetFocus)

        QMetaObject.connectSlotsByName(WidgetFocus)

    # setupUi

    def retranslateUi(self, WidgetFocus):
        WidgetFocus.setWindowTitle(QCoreApplication.translate("WidgetFocus", "Form", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("WidgetFocus", "Focus", None))
        self.label_12.setText(QCoreApplication.translate("WidgetFocus", "Focus:", None))
        self.label_11.setText(QCoreApplication.translate("WidgetFocus", "Base:", None))
        self.butSetFocusBase.setText(QCoreApplication.translate("WidgetFocus", "set...", None))
        self.label_14.setText(QCoreApplication.translate("WidgetFocus", "Offset:", None))
        self.butSetFocusOffset.setText(QCoreApplication.translate("WidgetFocus", "set...", None))
        self.buttonResetFocusOffset.setText(QCoreApplication.translate("WidgetFocus", "reset", None))
        self.label_13.setText(QCoreApplication.translate("WidgetFocus", "Status:", None))

    # retranslateUi
