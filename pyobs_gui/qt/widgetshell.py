# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'widgetshell.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

from .commandinput import CommandInput


class Ui_WidgetShell(object):
    def setupUi(self, WidgetShell):
        if not WidgetShell.objectName():
            WidgetShell.setObjectName("WidgetShell")
        WidgetShell.resize(425, 312)
        self.verticalLayout = QVBoxLayout(WidgetShell)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textCommandLog = QTextBrowser(WidgetShell)
        self.textCommandLog.setObjectName("textCommandLog")
        font = QFont()
        font.setFamily("Monospace")
        self.textCommandLog.setFont(font)

        self.verticalLayout.addWidget(self.textCommandLog)

        self.textCommandInput = CommandInput(WidgetShell)
        self.textCommandInput.setObjectName("textCommandInput")

        self.verticalLayout.addWidget(self.textCommandInput)

        self.retranslateUi(WidgetShell)

        QMetaObject.connectSlotsByName(WidgetShell)

    # setupUi

    def retranslateUi(self, WidgetShell):
        WidgetShell.setWindowTitle(QCoreApplication.translate("WidgetShell", "Form", None))

    # retranslateUi
