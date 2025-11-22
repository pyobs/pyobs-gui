# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'focuswidget.ui'
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

class Ui_FocusWidget(object):
    def setupUi(self, FocusWidget):
        if not FocusWidget.objectName():
            FocusWidget.setObjectName(u"FocusWidget")
        FocusWidget.resize(248, 196)
        self.verticalLayout = QVBoxLayout(FocusWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_5 = QGroupBox(FocusWidget)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.formLayout = QFormLayout(self.groupBox_5)
        self.formLayout.setObjectName(u"formLayout")
        self.label_12 = QLabel(self.groupBox_5)
        self.label_12.setObjectName(u"label_12")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.labelCurFocus = QLineEdit(self.groupBox_5)
        self.labelCurFocus.setObjectName(u"labelCurFocus")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.labelCurFocus.sizePolicy().hasHeightForWidth())
        self.labelCurFocus.setSizePolicy(sizePolicy)
        self.labelCurFocus.setAlignment(Qt.AlignCenter)
        self.labelCurFocus.setReadOnly(True)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.labelCurFocus)

        self.label_11 = QLabel(self.groupBox_5)
        self.label_11.setObjectName(u"label_11")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.labelCurFocusBase = QLineEdit(self.groupBox_5)
        self.labelCurFocusBase.setObjectName(u"labelCurFocusBase")
        sizePolicy.setHeightForWidth(self.labelCurFocusBase.sizePolicy().hasHeightForWidth())
        self.labelCurFocusBase.setSizePolicy(sizePolicy)
        self.labelCurFocusBase.setAlignment(Qt.AlignCenter)
        self.labelCurFocusBase.setReadOnly(True)

        self.horizontalLayout.addWidget(self.labelCurFocusBase)

        self.butSetFocusBase = QToolButton(self.groupBox_5)
        self.butSetFocusBase.setObjectName(u"butSetFocusBase")
        icon = QIcon()
        icon.addFile(u":/resources/edit-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.butSetFocusBase.setIcon(icon)

        self.horizontalLayout.addWidget(self.butSetFocusBase)


        self.formLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.label_14 = QLabel(self.groupBox_5)
        self.label_14.setObjectName(u"label_14")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_14)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.labelCurFocusOffset = QLineEdit(self.groupBox_5)
        self.labelCurFocusOffset.setObjectName(u"labelCurFocusOffset")
        sizePolicy.setHeightForWidth(self.labelCurFocusOffset.sizePolicy().hasHeightForWidth())
        self.labelCurFocusOffset.setSizePolicy(sizePolicy)
        self.labelCurFocusOffset.setAlignment(Qt.AlignCenter)
        self.labelCurFocusOffset.setReadOnly(True)

        self.horizontalLayout_2.addWidget(self.labelCurFocusOffset)

        self.butSetFocusOffset = QToolButton(self.groupBox_5)
        self.butSetFocusOffset.setObjectName(u"butSetFocusOffset")
        self.butSetFocusOffset.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.butSetFocusOffset)

        self.buttonResetFocusOffset = QToolButton(self.groupBox_5)
        self.buttonResetFocusOffset.setObjectName(u"buttonResetFocusOffset")
        icon1 = QIcon()
        icon1.addFile(u":/resources/undo-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonResetFocusOffset.setIcon(icon1)

        self.horizontalLayout_2.addWidget(self.buttonResetFocusOffset)


        self.formLayout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_2)

        self.label_13 = QLabel(self.groupBox_5)
        self.label_13.setObjectName(u"label_13")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_13)

        self.labelCurStatus = QLineEdit(self.groupBox_5)
        self.labelCurStatus.setObjectName(u"labelCurStatus")
        sizePolicy.setHeightForWidth(self.labelCurStatus.sizePolicy().hasHeightForWidth())
        self.labelCurStatus.setSizePolicy(sizePolicy)
        self.labelCurStatus.setAlignment(Qt.AlignCenter)
        self.labelCurStatus.setReadOnly(True)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.labelCurStatus)


        self.verticalLayout.addWidget(self.groupBox_5)

        QWidget.setTabOrder(self.labelCurFocus, self.labelCurFocusBase)
        QWidget.setTabOrder(self.labelCurFocusBase, self.butSetFocusBase)
        QWidget.setTabOrder(self.butSetFocusBase, self.labelCurFocusOffset)
        QWidget.setTabOrder(self.labelCurFocusOffset, self.butSetFocusOffset)
        QWidget.setTabOrder(self.butSetFocusOffset, self.labelCurStatus)

        self.retranslateUi(FocusWidget)

        QMetaObject.connectSlotsByName(FocusWidget)
    # setupUi

    def retranslateUi(self, FocusWidget):
        FocusWidget.setWindowTitle(QCoreApplication.translate("FocusWidget", u"Form", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("FocusWidget", u"Focus", None))
        self.label_12.setText(QCoreApplication.translate("FocusWidget", u"Focus:", None))
        self.label_11.setText(QCoreApplication.translate("FocusWidget", u"Base:", None))
        self.butSetFocusBase.setText(QCoreApplication.translate("FocusWidget", u"set...", None))
        self.label_14.setText(QCoreApplication.translate("FocusWidget", u"Offset:", None))
        self.butSetFocusOffset.setText(QCoreApplication.translate("FocusWidget", u"set...", None))
        self.buttonResetFocusOffset.setText(QCoreApplication.translate("FocusWidget", u"reset", None))
        self.label_13.setText(QCoreApplication.translate("FocusWidget", u"Status:", None))
    # retranslateUi

