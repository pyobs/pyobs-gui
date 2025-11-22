# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'coolingwidget.ui'
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
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QDoubleSpinBox,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QToolButton,
    QVBoxLayout,
    QWidget,
)
from . import resources_rc


class Ui_CoolingWidget(object):
    def setupUi(self, CoolingWidget):
        if not CoolingWidget.objectName():
            CoolingWidget.setObjectName("CoolingWidget")
        CoolingWidget.resize(210, 161)
        self.verticalLayout = QVBoxLayout(CoolingWidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.groupBox_2 = QGroupBox(CoolingWidget)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_9 = QLabel(self.groupBox_2)
        self.label_9.setObjectName("label_9")

        self.gridLayout.addWidget(self.label_9, 0, 0, 1, 1)

        self.labelStatus = QLineEdit(self.groupBox_2)
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatus.setAlignment(Qt.AlignCenter)
        self.labelStatus.setReadOnly(True)

        self.gridLayout.addWidget(self.labelStatus, 0, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox_2)
        self.label_10.setObjectName("label_10")

        self.gridLayout.addWidget(self.label_10, 1, 0, 1, 1)

        self.labelPower = QLineEdit(self.groupBox_2)
        self.labelPower.setObjectName("labelPower")
        self.labelPower.setAlignment(Qt.AlignCenter)
        self.labelPower.setReadOnly(True)

        self.gridLayout.addWidget(self.labelPower, 1, 1, 1, 1)

        self.line = QFrame(self.groupBox_2)
        self.line.setObjectName("line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.gridLayout.addWidget(self.line, 2, 0, 1, 2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.spinSetPoint = QDoubleSpinBox(self.groupBox_2)
        self.spinSetPoint.setObjectName("spinSetPoint")
        self.spinSetPoint.setDecimals(1)
        self.spinSetPoint.setMinimum(-50.000000000000000)
        self.spinSetPoint.setMaximum(50.000000000000000)

        self.horizontalLayout.addWidget(self.spinSetPoint)

        self.buttonApply = QToolButton(self.groupBox_2)
        self.buttonApply.setObjectName("buttonApply")
        icon = QIcon()
        icon.addFile(":/resources/arrow-alt-circle-right-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonApply.setIcon(icon)

        self.horizontalLayout.addWidget(self.buttonApply)

        self.horizontalLayout.setStretch(0, 1)

        self.gridLayout.addLayout(self.horizontalLayout, 3, 1, 1, 1)

        self.checkEnabled = QCheckBox(self.groupBox_2)
        self.checkEnabled.setObjectName("checkEnabled")

        self.gridLayout.addWidget(self.checkEnabled, 3, 0, 1, 1)

        self.verticalLayout.addWidget(self.groupBox_2)

        self.retranslateUi(CoolingWidget)

        QMetaObject.connectSlotsByName(CoolingWidget)

    # setupUi

    def retranslateUi(self, CoolingWidget):
        CoolingWidget.setWindowTitle(QCoreApplication.translate("CoolingWidget", "Form", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("CoolingWidget", "Cooling", None))
        self.label_9.setText(QCoreApplication.translate("CoolingWidget", "Set temp:", None))
        self.label_10.setText(QCoreApplication.translate("CoolingWidget", "Power:", None))
        self.spinSetPoint.setSuffix(QCoreApplication.translate("CoolingWidget", " \u00b0C", None))
        self.buttonApply.setText(QCoreApplication.translate("CoolingWidget", "...", None))
        self.checkEnabled.setText(QCoreApplication.translate("CoolingWidget", "Enable", None))

    # retranslateUi
