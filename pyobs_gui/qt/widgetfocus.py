# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetfocus.ui'
#
# Created by: PyQt5 UI code generator 5.12.3
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_WidgetFocus(object):
    def setupUi(self, WidgetFocus):
        WidgetFocus.setObjectName("WidgetFocus")
        WidgetFocus.resize(248, 195)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetFocus)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_5 = QtWidgets.QGroupBox(WidgetFocus)
        self.groupBox_5.setObjectName("groupBox_5")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox_5)
        self.formLayout.setObjectName("formLayout")
        self.label_12 = QtWidgets.QLabel(self.groupBox_5)
        self.label_12.setObjectName("label_12")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_12)
        self.labelCurFocus = QtWidgets.QLineEdit(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCurFocus.sizePolicy().hasHeightForWidth())
        self.labelCurFocus.setSizePolicy(sizePolicy)
        self.labelCurFocus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurFocus.setReadOnly(True)
        self.labelCurFocus.setObjectName("labelCurFocus")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.labelCurFocus)
        self.label_11 = QtWidgets.QLabel(self.groupBox_5)
        self.label_11.setObjectName("label_11")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_11)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.labelCurFocusBase = QtWidgets.QLineEdit(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCurFocusBase.sizePolicy().hasHeightForWidth())
        self.labelCurFocusBase.setSizePolicy(sizePolicy)
        self.labelCurFocusBase.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurFocusBase.setReadOnly(True)
        self.labelCurFocusBase.setObjectName("labelCurFocusBase")
        self.horizontalLayout.addWidget(self.labelCurFocusBase)
        self.butSetFocusBase = QtWidgets.QToolButton(self.groupBox_5)
        icon = QtGui.QIcon()
        icon.addPixmap(
            QtGui.QPixmap(":/resources/edit-solid.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.butSetFocusBase.setIcon(icon)
        self.butSetFocusBase.setObjectName("butSetFocusBase")
        self.horizontalLayout.addWidget(self.butSetFocusBase)
        self.formLayout.setLayout(1, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout)
        self.label_14 = QtWidgets.QLabel(self.groupBox_5)
        self.label_14.setObjectName("label_14")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_14)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.labelCurFocusOffset = QtWidgets.QLineEdit(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCurFocusOffset.sizePolicy().hasHeightForWidth())
        self.labelCurFocusOffset.setSizePolicy(sizePolicy)
        self.labelCurFocusOffset.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurFocusOffset.setReadOnly(True)
        self.labelCurFocusOffset.setObjectName("labelCurFocusOffset")
        self.horizontalLayout_2.addWidget(self.labelCurFocusOffset)
        self.butSetFocusOffset = QtWidgets.QToolButton(self.groupBox_5)
        self.butSetFocusOffset.setIcon(icon)
        self.butSetFocusOffset.setObjectName("butSetFocusOffset")
        self.horizontalLayout_2.addWidget(self.butSetFocusOffset)
        self.buttonResetFocusOffset = QtWidgets.QToolButton(self.groupBox_5)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(
            QtGui.QPixmap(":/resources/undo-solid.svg"),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        self.buttonResetFocusOffset.setIcon(icon1)
        self.buttonResetFocusOffset.setObjectName("buttonResetFocusOffset")
        self.horizontalLayout_2.addWidget(self.buttonResetFocusOffset)
        self.formLayout.setLayout(2, QtWidgets.QFormLayout.FieldRole, self.horizontalLayout_2)
        self.label_13 = QtWidgets.QLabel(self.groupBox_5)
        self.label_13.setObjectName("label_13")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_13)
        self.labelCurStatus = QtWidgets.QLineEdit(self.groupBox_5)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCurStatus.sizePolicy().hasHeightForWidth())
        self.labelCurStatus.setSizePolicy(sizePolicy)
        self.labelCurStatus.setAlignment(QtCore.Qt.AlignCenter)
        self.labelCurStatus.setReadOnly(True)
        self.labelCurStatus.setObjectName("labelCurStatus")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.labelCurStatus)
        self.verticalLayout.addWidget(self.groupBox_5)

        self.retranslateUi(WidgetFocus)
        QtCore.QMetaObject.connectSlotsByName(WidgetFocus)
        WidgetFocus.setTabOrder(self.labelCurFocus, self.labelCurFocusBase)
        WidgetFocus.setTabOrder(self.labelCurFocusBase, self.butSetFocusBase)
        WidgetFocus.setTabOrder(self.butSetFocusBase, self.labelCurFocusOffset)
        WidgetFocus.setTabOrder(self.labelCurFocusOffset, self.butSetFocusOffset)
        WidgetFocus.setTabOrder(self.butSetFocusOffset, self.labelCurStatus)

    def retranslateUi(self, WidgetFocus):
        _translate = QtCore.QCoreApplication.translate
        WidgetFocus.setWindowTitle(_translate("WidgetFocus", "Form"))
        self.groupBox_5.setTitle(_translate("WidgetFocus", "Focus"))
        self.label_12.setText(_translate("WidgetFocus", "Focus:"))
        self.label_11.setText(_translate("WidgetFocus", "Base:"))
        self.butSetFocusBase.setText(_translate("WidgetFocus", "set..."))
        self.label_14.setText(_translate("WidgetFocus", "Offset:"))
        self.butSetFocusOffset.setText(_translate("WidgetFocus", "set..."))
        self.buttonResetFocusOffset.setText(_translate("WidgetFocus", "reset"))
        self.label_13.setText(_translate("WidgetFocus", "Status:"))


from . import resources_rc
