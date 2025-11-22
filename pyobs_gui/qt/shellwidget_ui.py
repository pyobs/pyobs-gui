# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'shellwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import QApplication, QSizePolicy, QTextBrowser, QVBoxLayout, QWidget

from ..commandinputwidget import CommandInputWidget


class Ui_ShellWidget(object):
    def setupUi(self, ShellWidget):
        if not ShellWidget.objectName():
            ShellWidget.setObjectName("ShellWidget")
        ShellWidget.resize(425, 312)
        self.verticalLayout = QVBoxLayout(ShellWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.textCommandLog = QTextBrowser(ShellWidget)
        self.textCommandLog.setObjectName("textCommandLog")
        font = QFont()
        font.setFamilies(["Monospace"])
        self.textCommandLog.setFont(font)

        self.verticalLayout.addWidget(self.textCommandLog)

        self.textCommandInput = CommandInputWidget(ShellWidget)
        self.textCommandInput.setObjectName("textCommandInput")

        self.verticalLayout.addWidget(self.textCommandInput)

        self.retranslateUi(ShellWidget)

        QMetaObject.connectSlotsByName(ShellWidget)

    # setupUi

    def retranslateUi(self, ShellWidget):
        ShellWidget.setWindowTitle(QCoreApplication.translate("ShellWidget", "Form", None))

    # retranslateUi
