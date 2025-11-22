# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'compassmovewidget.ui'
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
from PySide6.QtWidgets import QApplication, QGridLayout, QPushButton, QSizePolicy, QSpinBox, QWidget
from . import resources_rc


class Ui_CompassMoveWidget(object):
    def setupUi(self, CompassMoveWidget):
        if not CompassMoveWidget.objectName():
            CompassMoveWidget.setObjectName("CompassMoveWidget")
        CompassMoveWidget.resize(276, 126)
        self.gridLayout = QGridLayout(CompassMoveWidget)
        self.gridLayout.setObjectName("gridLayout")
        self.buttonOffsetNorth = QPushButton(CompassMoveWidget)
        self.buttonOffsetNorth.setObjectName("buttonOffsetNorth")
        icon = QIcon()
        icon.addFile(":/resources/arrow-alt-circle-up-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonOffsetNorth.setIcon(icon)

        self.gridLayout.addWidget(self.buttonOffsetNorth, 0, 1, 1, 1)

        self.buttonOffsetEast = QPushButton(CompassMoveWidget)
        self.buttonOffsetEast.setObjectName("buttonOffsetEast")
        icon1 = QIcon()
        icon1.addFile(":/resources/arrow-alt-circle-left-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonOffsetEast.setIcon(icon1)

        self.gridLayout.addWidget(self.buttonOffsetEast, 1, 0, 1, 1)

        self.spinOffset = QSpinBox(CompassMoveWidget)
        self.spinOffset.setObjectName("spinOffset")
        self.spinOffset.setMaximum(999)
        self.spinOffset.setSingleStep(10)
        self.spinOffset.setValue(30)

        self.gridLayout.addWidget(self.spinOffset, 1, 1, 1, 1)

        self.buttonOffsetWest = QPushButton(CompassMoveWidget)
        self.buttonOffsetWest.setObjectName("buttonOffsetWest")
        icon2 = QIcon()
        icon2.addFile(":/resources/arrow-alt-circle-right-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonOffsetWest.setIcon(icon2)

        self.gridLayout.addWidget(self.buttonOffsetWest, 1, 2, 1, 1)

        self.buttonOffsetSouth = QPushButton(CompassMoveWidget)
        self.buttonOffsetSouth.setObjectName("buttonOffsetSouth")
        icon3 = QIcon()
        icon3.addFile(":/resources/arrow-alt-circle-down-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonOffsetSouth.setIcon(icon3)

        self.gridLayout.addWidget(self.buttonOffsetSouth, 2, 1, 1, 1)

        self.retranslateUi(CompassMoveWidget)

        QMetaObject.connectSlotsByName(CompassMoveWidget)

    # setupUi

    def retranslateUi(self, CompassMoveWidget):
        CompassMoveWidget.setWindowTitle(QCoreApplication.translate("CompassMoveWidget", "Form", None))
        self.buttonOffsetNorth.setText(QCoreApplication.translate("CompassMoveWidget", "N", None))
        self.buttonOffsetEast.setText(QCoreApplication.translate("CompassMoveWidget", "E", None))
        self.spinOffset.setSuffix(QCoreApplication.translate("CompassMoveWidget", '"', None))
        self.spinOffset.setPrefix("")
        self.buttonOffsetWest.setText(QCoreApplication.translate("CompassMoveWidget", "W", None))
        self.buttonOffsetSouth.setText(QCoreApplication.translate("CompassMoveWidget", "S", None))

    # retranslateUi
