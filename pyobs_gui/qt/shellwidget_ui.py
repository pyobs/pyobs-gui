# -*- coding: utf-8 -*-

# Form implementation generated from ..reading ui file 'shellwidget.ui'
#
# Created by: PyQt5 UI code generator 5.14.2
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ShellWidget(object):
    def setupUi(self, ShellWidget):
        ShellWidget.setObjectName("ShellWidget")
        ShellWidget.resize(425, 312)
        self.verticalLayout = QtWidgets.QVBoxLayout(ShellWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textCommandLog = QtWidgets.QTextBrowser(ShellWidget)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.textCommandLog.setFont(font)
        self.textCommandLog.setObjectName("textCommandLog")
        self.verticalLayout.addWidget(self.textCommandLog)
        self.textCommandInput = CommandInputWidget(ShellWidget)
        self.textCommandInput.setObjectName("textCommandInput")
        self.verticalLayout.addWidget(self.textCommandInput)

        self.retranslateUi(ShellWidget)
        QtCore.QMetaObject.connectSlotsByName(ShellWidget)

    def retranslateUi(self, ShellWidget):
        _translate = QtCore.QCoreApplication.translate
        ShellWidget.setWindowTitle(_translate("ShellWidget", "Form"))
from ..commandinputwidget import CommandInputWidget
