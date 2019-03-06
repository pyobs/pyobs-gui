# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'widgetshell.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WidgetShell(object):
    def setupUi(self, WidgetShell):
        WidgetShell.setObjectName("WidgetShell")
        WidgetShell.resize(425, 312)
        self.verticalLayout = QtWidgets.QVBoxLayout(WidgetShell)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textCommandLog = QtWidgets.QTextBrowser(WidgetShell)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.textCommandLog.setFont(font)
        self.textCommandLog.setObjectName("textCommandLog")
        self.verticalLayout.addWidget(self.textCommandLog)
        self.textCommandInput = CommandInput(WidgetShell)
        self.textCommandInput.setObjectName("textCommandInput")
        self.verticalLayout.addWidget(self.textCommandInput)

        self.retranslateUi(WidgetShell)
        QtCore.QMetaObject.connectSlotsByName(WidgetShell)

    def retranslateUi(self, WidgetShell):
        _translate = QtCore.QCoreApplication.translate
        WidgetShell.setWindowTitle(_translate("WidgetShell", "Form"))

from .commandinput import CommandInput
