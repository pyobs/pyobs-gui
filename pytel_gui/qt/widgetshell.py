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
        WidgetShell.resize(612, 491)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(WidgetShell)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.splitter = QtWidgets.QSplitter(WidgetShell)
        self.splitter.setOrientation(QtCore.Qt.Horizontal)
        self.splitter.setObjectName("splitter")
        self.layoutWidget = QtWidgets.QWidget(self.splitter)
        self.layoutWidget.setObjectName("layoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.layoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textCommandLog = QtWidgets.QTextBrowser(self.layoutWidget)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.textCommandLog.setFont(font)
        self.textCommandLog.setObjectName("textCommandLog")
        self.verticalLayout.addWidget(self.textCommandLog)
        self.textCommandInput = CommandInput(self.layoutWidget)
        self.textCommandInput.setObjectName("textCommandInput")
        self.verticalLayout.addWidget(self.textCommandInput)
        self.textCommandHelp = QtWidgets.QTextBrowser(self.splitter)
        self.textCommandHelp.setObjectName("textCommandHelp")
        self.verticalLayout_2.addWidget(self.splitter)

        self.retranslateUi(WidgetShell)
        QtCore.QMetaObject.connectSlotsByName(WidgetShell)

    def retranslateUi(self, WidgetShell):
        _translate = QtCore.QCoreApplication.translate
        WidgetShell.setWindowTitle(_translate("WidgetShell", "Form"))

from .commandinput import CommandInput
