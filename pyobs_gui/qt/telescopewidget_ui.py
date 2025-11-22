# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'telescopewidget.ui'
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
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QStackedWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

from ..compassmovewidget import CompassMoveWidget
from . import resources_rc


class Ui_TelescopeWidget(object):
    def setupUi(self, TelescopeWidget):
        if not TelescopeWidget.objectName():
            TelescopeWidget.setObjectName("TelescopeWidget")
        TelescopeWidget.resize(1019, 652)
        self.horizontalLayout_7 = QHBoxLayout(TelescopeWidget)
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.verticalLayout_2 = QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.groupStatus = QGroupBox(TelescopeWidget)
        self.groupStatus.setObjectName("groupStatus")
        self.verticalLayout = QVBoxLayout(self.groupStatus)
        self.verticalLayout.setObjectName("verticalLayout")
        self.labelStatus = QLineEdit(self.groupStatus)
        self.labelStatus.setObjectName("labelStatus")
        self.labelStatus.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelStatus.setReadOnly(True)

        self.verticalLayout.addWidget(self.labelStatus)

        self.line_3 = QFrame(self.groupStatus)
        self.line_3.setObjectName("line_3")
        self.line_3.setFrameShape(QFrame.Shape.HLine)
        self.line_3.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_3)

        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setSpacing(0)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.buttonInit = QPushButton(self.groupStatus)
        self.buttonInit.setObjectName("buttonInit")

        self.gridLayout_5.addWidget(self.buttonInit, 0, 0, 1, 1)

        self.buttonPark = QPushButton(self.groupStatus)
        self.buttonPark.setObjectName("buttonPark")

        self.gridLayout_5.addWidget(self.buttonPark, 0, 1, 1, 1)

        self.buttonStop = QPushButton(self.groupStatus)
        self.buttonStop.setObjectName("buttonStop")

        self.gridLayout_5.addWidget(self.buttonStop, 1, 0, 1, 2)

        self.verticalLayout.addLayout(self.gridLayout_5)

        self.line_5 = QFrame(self.groupStatus)
        self.line_5.setObjectName("line_5")
        self.line_5.setFrameShape(QFrame.Shape.HLine)
        self.line_5.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_5)

        self.line_4 = QFrame(self.groupStatus)
        self.line_4.setObjectName("line_4")
        self.line_4.setFrameShape(QFrame.Shape.HLine)
        self.line_4.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout.addWidget(self.line_4)

        self.gridLayout = QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QLabel(self.groupStatus)
        self.label.setObjectName("label")

        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

        self.labelCurRA = QLineEdit(self.groupStatus)
        self.labelCurRA.setObjectName("labelCurRA")
        self.labelCurRA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelCurRA.setReadOnly(True)

        self.gridLayout.addWidget(self.labelCurRA, 0, 1, 1, 1)

        self.label_2 = QLabel(self.groupStatus)
        self.label_2.setObjectName("label_2")

        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)

        self.labelCurDec = QLineEdit(self.groupStatus)
        self.labelCurDec.setObjectName("labelCurDec")
        self.labelCurDec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelCurDec.setReadOnly(True)

        self.gridLayout.addWidget(self.labelCurDec, 1, 1, 1, 1)

        self.label_3 = QLabel(self.groupStatus)
        self.label_3.setObjectName("label_3")

        self.gridLayout.addWidget(self.label_3, 2, 0, 1, 1)

        self.labelCurAlt = QLineEdit(self.groupStatus)
        self.labelCurAlt.setObjectName("labelCurAlt")
        self.labelCurAlt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelCurAlt.setReadOnly(True)

        self.gridLayout.addWidget(self.labelCurAlt, 2, 1, 1, 1)

        self.label_4 = QLabel(self.groupStatus)
        self.label_4.setObjectName("label_4")

        self.gridLayout.addWidget(self.label_4, 3, 0, 1, 1)

        self.labelCurAz = QLineEdit(self.groupStatus)
        self.labelCurAz.setObjectName("labelCurAz")
        self.labelCurAz.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelCurAz.setReadOnly(True)

        self.gridLayout.addWidget(self.labelCurAz, 3, 1, 1, 1)

        self.gridLayout.setColumnStretch(0, 1)
        self.gridLayout.setColumnStretch(1, 2)

        self.verticalLayout.addLayout(self.gridLayout)

        self.verticalLayout_2.addWidget(self.groupStatus)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.horizontalLayout_7.addLayout(self.verticalLayout_2)

        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.groupBox_5 = QGroupBox(TelescopeWidget)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_7 = QVBoxLayout(self.groupBox_5)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.comboMoveType = QComboBox(self.groupBox_5)
        self.comboMoveType.setObjectName("comboMoveType")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(255, 85, 0, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Button, brush1)
        brush2 = QBrush(QColor(255, 170, 127, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Light, brush2)
        brush3 = QBrush(QColor(255, 127, 63, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Midlight, brush3)
        brush4 = QBrush(QColor(127, 42, 0, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Dark, brush4)
        brush5 = QBrush(QColor(170, 56, 0, 255))
        brush5.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Text, brush)
        brush6 = QBrush(QColor(255, 255, 255, 255))
        brush6.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.BrightText, brush6)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Shadow, brush)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.AlternateBase, brush2)
        brush7 = QBrush(QColor(255, 255, 220, 255))
        brush7.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipBase, brush7)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.ToolTipText, brush)
        brush8 = QBrush(QColor(0, 0, 0, 128))
        brush8.setStyle(Qt.BrushStyle.SolidPattern)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.PlaceholderText, brush8)
        # endif
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Light, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Midlight, brush3)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Dark, brush4)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Text, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.BrightText, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ButtonText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush6)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Shadow, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.AlternateBase, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipBase, brush7)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.ToolTipText, brush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.PlaceholderText, brush8)
        # endif
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Button, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Light, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Midlight, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Dark, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Mid, brush5)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.BrightText, brush6)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, brush4)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Shadow, brush)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.AlternateBase, brush1)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipBase, brush7)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ToolTipText, brush)
        # if QT_VERSION >= QT_VERSION_CHECK(5, 12, 0)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.PlaceholderText, brush8)
        # endif
        self.comboMoveType.setPalette(palette)

        self.verticalLayout_7.addWidget(self.comboMoveType)

        self.stackedMove = QStackedWidget(self.groupBox_5)
        self.stackedMove.setObjectName("stackedMove")
        self.pageMoveEquatorial = QWidget()
        self.pageMoveEquatorial.setObjectName("pageMoveEquatorial")
        self.verticalLayout_9 = QVBoxLayout(self.pageMoveEquatorial)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.label_11 = QLabel(self.pageMoveEquatorial)
        self.label_11.setObjectName("label_11")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_11)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.textSimbadName = QLineEdit(self.pageMoveEquatorial)
        self.textSimbadName.setObjectName("textSimbadName")

        self.horizontalLayout.addWidget(self.textSimbadName)

        self.buttonSimbadQuery = QToolButton(self.pageMoveEquatorial)
        self.buttonSimbadQuery.setObjectName("buttonSimbadQuery")
        icon = QIcon()
        icon.addFile(":/resources/search-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonSimbadQuery.setIcon(icon)

        self.horizontalLayout.addWidget(self.buttonSimbadQuery)

        self.formLayout.setLayout(1, QFormLayout.ItemRole.FieldRole, self.horizontalLayout)

        self.label_9 = QLabel(self.pageMoveEquatorial)
        self.label_9.setObjectName("label_9")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_9)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setSpacing(0)
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.textJplHorizonsName = QLineEdit(self.pageMoveEquatorial)
        self.textJplHorizonsName.setObjectName("textJplHorizonsName")

        self.horizontalLayout_6.addWidget(self.textJplHorizonsName)

        self.buttonJplHorizonsQuery = QToolButton(self.pageMoveEquatorial)
        self.buttonJplHorizonsQuery.setObjectName("buttonJplHorizonsQuery")
        self.buttonJplHorizonsQuery.setIcon(icon)

        self.horizontalLayout_6.addWidget(self.buttonJplHorizonsQuery)

        self.formLayout.setLayout(2, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_6)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.comboSolarSystemBody = QComboBox(self.pageMoveEquatorial)
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.addItem("")
        self.comboSolarSystemBody.setObjectName("comboSolarSystemBody")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.comboSolarSystemBody.sizePolicy().hasHeightForWidth())
        self.comboSolarSystemBody.setSizePolicy(sizePolicy)

        self.horizontalLayout_4.addWidget(self.comboSolarSystemBody)

        self.formLayout.setLayout(3, QFormLayout.ItemRole.FieldRole, self.horizontalLayout_4)

        self.label_12 = QLabel(self.pageMoveEquatorial)
        self.label_12.setObjectName("label_12")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_12)

        self.verticalLayout_9.addLayout(self.formLayout)

        self.widget = QWidget(self.pageMoveEquatorial)
        self.widget.setObjectName("widget")
        self.gridLayout_4 = QGridLayout(self.widget)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_23 = QLabel(self.widget)
        self.label_23.setObjectName("label_23")

        self.gridLayout_4.addWidget(self.label_23, 0, 0, 1, 1)

        self.textMoveRA = QLineEdit(self.widget)
        self.textMoveRA.setObjectName("textMoveRA")
        sizePolicy.setHeightForWidth(self.textMoveRA.sizePolicy().hasHeightForWidth())
        self.textMoveRA.setSizePolicy(sizePolicy)
        self.textMoveRA.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.textMoveRA, 0, 1, 1, 1)

        self.label_22 = QLabel(self.widget)
        self.label_22.setObjectName("label_22")

        self.gridLayout_4.addWidget(self.label_22, 0, 2, 1, 1)

        self.textMoveDec = QLineEdit(self.widget)
        self.textMoveDec.setObjectName("textMoveDec")
        sizePolicy.setHeightForWidth(self.textMoveDec.sizePolicy().hasHeightForWidth())
        self.textMoveDec.setSizePolicy(sizePolicy)
        self.textMoveDec.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.gridLayout_4.addWidget(self.textMoveDec, 0, 3, 1, 1)

        self.verticalLayout_9.addWidget(self.widget)

        self.verticalSpacer_2 = QSpacerItem(20, 105, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_9.addItem(self.verticalSpacer_2)

        self.stackedMove.addWidget(self.pageMoveEquatorial)
        self.pageMoveHorizontal = QWidget()
        self.pageMoveHorizontal.setObjectName("pageMoveHorizontal")
        self.verticalLayout_3 = QVBoxLayout(self.pageMoveHorizontal)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.widget_2 = QWidget(self.pageMoveHorizontal)
        self.widget_2.setObjectName("widget_2")
        self.gridLayout_3 = QGridLayout(self.widget_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_25 = QLabel(self.widget_2)
        self.label_25.setObjectName("label_25")

        self.gridLayout_3.addWidget(self.label_25, 0, 2, 1, 1)

        self.label_24 = QLabel(self.widget_2)
        self.label_24.setObjectName("label_24")

        self.gridLayout_3.addWidget(self.label_24, 0, 0, 1, 1)

        self.spinMoveAlt = QDoubleSpinBox(self.widget_2)
        self.spinMoveAlt.setObjectName("spinMoveAlt")
        sizePolicy.setHeightForWidth(self.spinMoveAlt.sizePolicy().hasHeightForWidth())
        self.spinMoveAlt.setSizePolicy(sizePolicy)
        self.spinMoveAlt.setMaximum(90.000000000000000)
        self.spinMoveAlt.setValue(60.000000000000000)

        self.gridLayout_3.addWidget(self.spinMoveAlt, 0, 1, 1, 1)

        self.spinMoveAz = QDoubleSpinBox(self.widget_2)
        self.spinMoveAz.setObjectName("spinMoveAz")
        sizePolicy.setHeightForWidth(self.spinMoveAz.sizePolicy().hasHeightForWidth())
        self.spinMoveAz.setSizePolicy(sizePolicy)
        self.spinMoveAz.setMaximum(360.000000000000000)

        self.gridLayout_3.addWidget(self.spinMoveAz, 0, 3, 1, 1)

        self.verticalLayout_3.addWidget(self.widget_2)

        self.verticalSpacer_3 = QSpacerItem(20, 147, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer_3)

        self.stackedMove.addWidget(self.pageMoveHorizontal)
        self.pageMoveHeliographicStonyhurst = QWidget()
        self.pageMoveHeliographicStonyhurst.setObjectName("pageMoveHeliographicStonyhurst")
        self.verticalLayout_4 = QVBoxLayout(self.pageMoveHeliographicStonyhurst)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.widget_4 = QWidget(self.pageMoveHeliographicStonyhurst)
        self.widget_4.setObjectName("widget_4")
        self.gridLayout_10 = QGridLayout(self.widget_4)
        self.gridLayout_10.setObjectName("gridLayout_10")
        self.label_37 = QLabel(self.widget_4)
        self.label_37.setObjectName("label_37")

        self.gridLayout_10.addWidget(self.label_37, 0, 2, 1, 1)

        self.spinMoveHGSLon = QDoubleSpinBox(self.widget_4)
        self.spinMoveHGSLon.setObjectName("spinMoveHGSLon")
        sizePolicy.setHeightForWidth(self.spinMoveHGSLon.sizePolicy().hasHeightForWidth())
        self.spinMoveHGSLon.setSizePolicy(sizePolicy)
        self.spinMoveHGSLon.setMinimum(-180.000000000000000)
        self.spinMoveHGSLon.setMaximum(180.000000000000000)
        self.spinMoveHGSLon.setSingleStep(0.100000000000000)
        self.spinMoveHGSLon.setValue(0.000000000000000)

        self.gridLayout_10.addWidget(self.spinMoveHGSLon, 0, 1, 1, 1)

        self.label_38 = QLabel(self.widget_4)
        self.label_38.setObjectName("label_38")

        self.gridLayout_10.addWidget(self.label_38, 0, 0, 1, 1)

        self.spinMoveHGSLat = QDoubleSpinBox(self.widget_4)
        self.spinMoveHGSLat.setObjectName("spinMoveHGSLat")
        sizePolicy.setHeightForWidth(self.spinMoveHGSLat.sizePolicy().hasHeightForWidth())
        self.spinMoveHGSLat.setSizePolicy(sizePolicy)
        self.spinMoveHGSLat.setMinimum(-90.000000000000000)
        self.spinMoveHGSLat.setMaximum(90.000000000000000)

        self.gridLayout_10.addWidget(self.spinMoveHGSLat, 0, 3, 1, 1)

        self.verticalLayout_4.addWidget(self.widget_4)

        self.verticalSpacer_6 = QSpacerItem(20, 147, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_4.addItem(self.verticalSpacer_6)

        self.stackedMove.addWidget(self.pageMoveHeliographicStonyhurst)
        self.pageMoveHelioprojectiveRadial = QWidget()
        self.pageMoveHelioprojectiveRadial.setObjectName("pageMoveHelioprojectiveRadial")
        self.verticalLayout_10 = QVBoxLayout(self.pageMoveHelioprojectiveRadial)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.label_42 = QLabel(self.pageMoveHelioprojectiveRadial)
        self.label_42.setObjectName("label_42")

        self.horizontalLayout_3.addWidget(self.label_42)

        self.spinMoveHelioProjectiveRadialTx = QSpinBox(self.pageMoveHelioprojectiveRadial)
        self.spinMoveHelioProjectiveRadialTx.setObjectName("spinMoveHelioProjectiveRadialTx")
        sizePolicy.setHeightForWidth(self.spinMoveHelioProjectiveRadialTx.sizePolicy().hasHeightForWidth())
        self.spinMoveHelioProjectiveRadialTx.setSizePolicy(sizePolicy)
        self.spinMoveHelioProjectiveRadialTx.setMinimum(-9999)
        self.spinMoveHelioProjectiveRadialTx.setMaximum(9999)

        self.horizontalLayout_3.addWidget(self.spinMoveHelioProjectiveRadialTx)

        self.label_41 = QLabel(self.pageMoveHelioprojectiveRadial)
        self.label_41.setObjectName("label_41")

        self.horizontalLayout_3.addWidget(self.label_41)

        self.spinMoveHelioProjectiveRadialTy = QSpinBox(self.pageMoveHelioprojectiveRadial)
        self.spinMoveHelioProjectiveRadialTy.setObjectName("spinMoveHelioProjectiveRadialTy")
        sizePolicy.setHeightForWidth(self.spinMoveHelioProjectiveRadialTy.sizePolicy().hasHeightForWidth())
        self.spinMoveHelioProjectiveRadialTy.setSizePolicy(sizePolicy)
        self.spinMoveHelioProjectiveRadialTy.setMinimum(-9999)
        self.spinMoveHelioProjectiveRadialTy.setMaximum(9999)

        self.horizontalLayout_3.addWidget(self.spinMoveHelioProjectiveRadialTy)

        self.verticalLayout_10.addLayout(self.horizontalLayout_3)

        self.verticalSpacer_7 = QSpacerItem(20, 240, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_7)

        self.stackedMove.addWidget(self.pageMoveHelioprojectiveRadial)
        self.pageMoveHelioprojectiveMuPsi = QWidget()
        self.pageMoveHelioprojectiveMuPsi.setObjectName("pageMoveHelioprojectiveMuPsi")
        self.verticalLayout_11 = QVBoxLayout(self.pageMoveHelioprojectiveMuPsi)
        self.verticalLayout_11.setObjectName("verticalLayout_11")
        self.widget_5 = QWidget(self.pageMoveHelioprojectiveMuPsi)
        self.widget_5.setObjectName("widget_5")
        self.gridLayout_13 = QGridLayout(self.widget_5)
        self.gridLayout_13.setObjectName("gridLayout_13")
        self.label_39 = QLabel(self.widget_5)
        self.label_39.setObjectName("label_39")

        self.gridLayout_13.addWidget(self.label_39, 0, 2, 1, 1)

        self.spinMoveHelioprojectiveRadialMu = QDoubleSpinBox(self.widget_5)
        self.spinMoveHelioprojectiveRadialMu.setObjectName("spinMoveHelioprojectiveRadialMu")
        sizePolicy.setHeightForWidth(self.spinMoveHelioprojectiveRadialMu.sizePolicy().hasHeightForWidth())
        self.spinMoveHelioprojectiveRadialMu.setSizePolicy(sizePolicy)
        self.spinMoveHelioprojectiveRadialMu.setMinimum(0.000000000000000)
        self.spinMoveHelioprojectiveRadialMu.setMaximum(1.000000000000000)
        self.spinMoveHelioprojectiveRadialMu.setSingleStep(0.100000000000000)
        self.spinMoveHelioprojectiveRadialMu.setValue(1.000000000000000)

        self.gridLayout_13.addWidget(self.spinMoveHelioprojectiveRadialMu, 0, 1, 1, 1)

        self.label_40 = QLabel(self.widget_5)
        self.label_40.setObjectName("label_40")

        self.gridLayout_13.addWidget(self.label_40, 0, 0, 1, 1)

        self.spinMoveHelioprojectiveRadialPsi = QDoubleSpinBox(self.widget_5)
        self.spinMoveHelioprojectiveRadialPsi.setObjectName("spinMoveHelioprojectiveRadialPsi")
        sizePolicy.setHeightForWidth(self.spinMoveHelioprojectiveRadialPsi.sizePolicy().hasHeightForWidth())
        self.spinMoveHelioprojectiveRadialPsi.setSizePolicy(sizePolicy)
        self.spinMoveHelioprojectiveRadialPsi.setMinimum(0.000000000000000)
        self.spinMoveHelioprojectiveRadialPsi.setMaximum(359.000000000000000)

        self.gridLayout_13.addWidget(self.spinMoveHelioprojectiveRadialPsi, 0, 3, 1, 1)

        self.verticalLayout_11.addWidget(self.widget_5)

        self.verticalSpacer_8 = QSpacerItem(20, 230, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_11.addItem(self.verticalSpacer_8)

        self.stackedMove.addWidget(self.pageMoveHelioprojectiveMuPsi)
        self.pageMoveOrbitElements = QWidget()
        self.pageMoveOrbitElements.setObjectName("pageMoveOrbitElements")
        self.gridLayout_8 = QGridLayout(self.pageMoveOrbitElements)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.horizontalLayout_8 = QHBoxLayout()
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.label_21 = QLabel(self.pageMoveOrbitElements)
        self.label_21.setObjectName("label_21")

        self.horizontalLayout_8.addWidget(self.label_21)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.textHorizonsName = QLineEdit(self.pageMoveOrbitElements)
        self.textHorizonsName.setObjectName("textHorizonsName")

        self.horizontalLayout_2.addWidget(self.textHorizonsName)

        self.buttonHorizonsQuery = QToolButton(self.pageMoveOrbitElements)
        self.buttonHorizonsQuery.setObjectName("buttonHorizonsQuery")
        self.buttonHorizonsQuery.setIcon(icon)

        self.horizontalLayout_2.addWidget(self.buttonHorizonsQuery)

        self.horizontalLayout_8.addLayout(self.horizontalLayout_2)

        self.gridLayout_8.addLayout(self.horizontalLayout_8, 0, 0, 1, 1)

        self.widget_3 = QWidget(self.pageMoveOrbitElements)
        self.widget_3.setObjectName("widget_3")
        self.gridLayout_2 = QGridLayout(self.widget_3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_29 = QLabel(self.widget_3)
        self.label_29.setObjectName("label_29")

        self.gridLayout_2.addWidget(self.label_29, 0, 2, 1, 1)

        self.label_32 = QLabel(self.widget_3)
        self.label_32.setObjectName("label_32")

        self.gridLayout_2.addWidget(self.label_32, 2, 0, 1, 1)

        self.label_34 = QLabel(self.widget_3)
        self.label_34.setObjectName("label_34")

        self.gridLayout_2.addWidget(self.label_34, 2, 2, 1, 1)

        self.label_28 = QLabel(self.widget_3)
        self.label_28.setObjectName("label_28")

        self.gridLayout_2.addWidget(self.label_28, 1, 0, 1, 1)

        self.label_30 = QLabel(self.widget_3)
        self.label_30.setObjectName("label_30")

        self.gridLayout_2.addWidget(self.label_30, 1, 2, 1, 1)

        self.label_33 = QLabel(self.widget_3)
        self.label_33.setObjectName("label_33")

        self.gridLayout_2.addWidget(self.label_33, 3, 0, 1, 1)

        self.label_31 = QLabel(self.widget_3)
        self.label_31.setObjectName("label_31")

        self.gridLayout_2.addWidget(self.label_31, 0, 0, 1, 1)

        self.spinOrbitElementsSemiMajorAxis = QDoubleSpinBox(self.widget_3)
        self.spinOrbitElementsSemiMajorAxis.setObjectName("spinOrbitElementsSemiMajorAxis")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.spinOrbitElementsSemiMajorAxis.sizePolicy().hasHeightForWidth())
        self.spinOrbitElementsSemiMajorAxis.setSizePolicy(sizePolicy1)
        self.spinOrbitElementsSemiMajorAxis.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter
        )
        self.spinOrbitElementsSemiMajorAxis.setDecimals(6)
        self.spinOrbitElementsSemiMajorAxis.setValue(1.000000000000000)

        self.gridLayout_2.addWidget(self.spinOrbitElementsSemiMajorAxis, 0, 1, 1, 1)

        self.spinOrbitElementsIncl = QDoubleSpinBox(self.widget_3)
        self.spinOrbitElementsIncl.setObjectName("spinOrbitElementsIncl")
        sizePolicy1.setHeightForWidth(self.spinOrbitElementsIncl.sizePolicy().hasHeightForWidth())
        self.spinOrbitElementsIncl.setSizePolicy(sizePolicy1)
        self.spinOrbitElementsIncl.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter
        )
        self.spinOrbitElementsIncl.setDecimals(6)
        self.spinOrbitElementsIncl.setMaximum(360.000000000000000)

        self.gridLayout_2.addWidget(self.spinOrbitElementsIncl, 1, 1, 1, 1)

        self.spinOrbitElementsEcc = QDoubleSpinBox(self.widget_3)
        self.spinOrbitElementsEcc.setObjectName("spinOrbitElementsEcc")
        sizePolicy1.setHeightForWidth(self.spinOrbitElementsEcc.sizePolicy().hasHeightForWidth())
        self.spinOrbitElementsEcc.setSizePolicy(sizePolicy1)
        self.spinOrbitElementsEcc.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter
        )
        self.spinOrbitElementsEcc.setDecimals(6)
        self.spinOrbitElementsEcc.setMaximum(1.000000000000000)
        self.spinOrbitElementsEcc.setSingleStep(0.100000000000000)

        self.gridLayout_2.addWidget(self.spinOrbitElementsEcc, 2, 1, 1, 1)

        self.spinOrbitElementsMA = QDoubleSpinBox(self.widget_3)
        self.spinOrbitElementsMA.setObjectName("spinOrbitElementsMA")
        sizePolicy1.setHeightForWidth(self.spinOrbitElementsMA.sizePolicy().hasHeightForWidth())
        self.spinOrbitElementsMA.setSizePolicy(sizePolicy1)
        self.spinOrbitElementsMA.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter
        )
        self.spinOrbitElementsMA.setDecimals(6)
        self.spinOrbitElementsMA.setMaximum(360.000000000000000)

        self.gridLayout_2.addWidget(self.spinOrbitElementsMA, 3, 1, 1, 1)

        self.spinOrbitElementsOmega = QDoubleSpinBox(self.widget_3)
        self.spinOrbitElementsOmega.setObjectName("spinOrbitElementsOmega")
        sizePolicy1.setHeightForWidth(self.spinOrbitElementsOmega.sizePolicy().hasHeightForWidth())
        self.spinOrbitElementsOmega.setSizePolicy(sizePolicy1)
        self.spinOrbitElementsOmega.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter
        )
        self.spinOrbitElementsOmega.setDecimals(6)
        self.spinOrbitElementsOmega.setMaximum(360.000000000000000)

        self.gridLayout_2.addWidget(self.spinOrbitElementsOmega, 0, 3, 1, 1)

        self.spinOrbitElementsPerifocus = QDoubleSpinBox(self.widget_3)
        self.spinOrbitElementsPerifocus.setObjectName("spinOrbitElementsPerifocus")
        sizePolicy1.setHeightForWidth(self.spinOrbitElementsPerifocus.sizePolicy().hasHeightForWidth())
        self.spinOrbitElementsPerifocus.setSizePolicy(sizePolicy1)
        self.spinOrbitElementsPerifocus.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter
        )
        self.spinOrbitElementsPerifocus.setDecimals(6)
        self.spinOrbitElementsPerifocus.setMaximum(360.000000000000000)

        self.gridLayout_2.addWidget(self.spinOrbitElementsPerifocus, 1, 3, 1, 1)

        self.spinOrbitElementsEpoch = QDoubleSpinBox(self.widget_3)
        self.spinOrbitElementsEpoch.setObjectName("spinOrbitElementsEpoch")
        self.spinOrbitElementsEpoch.setAlignment(
            Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter
        )
        self.spinOrbitElementsEpoch.setDecimals(6)
        self.spinOrbitElementsEpoch.setMaximum(9999999.000000000000000)

        self.gridLayout_2.addWidget(self.spinOrbitElementsEpoch, 2, 3, 1, 1)

        self.gridLayout_8.addWidget(self.widget_3, 1, 0, 1, 1)

        self.stackedMove.addWidget(self.pageMoveOrbitElements)

        self.verticalLayout_7.addWidget(self.stackedMove)

        self.groupDestCoords = QGroupBox(self.groupBox_5)
        self.groupDestCoords.setObjectName("groupDestCoords")
        self.gridLayout_6 = QGridLayout(self.groupDestCoords)
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_26 = QLabel(self.groupDestCoords)
        self.label_26.setObjectName("label_26")

        self.gridLayout_6.addWidget(self.label_26, 0, 0, 1, 1)

        self.textDestRA = QLineEdit(self.groupDestCoords)
        self.textDestRA.setObjectName("textDestRA")
        self.textDestRA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textDestRA.setReadOnly(True)

        self.gridLayout_6.addWidget(self.textDestRA, 0, 1, 1, 1)

        self.label_36 = QLabel(self.groupDestCoords)
        self.label_36.setObjectName("label_36")

        self.gridLayout_6.addWidget(self.label_36, 0, 2, 1, 1)

        self.textDestAlt = QLineEdit(self.groupDestCoords)
        self.textDestAlt.setObjectName("textDestAlt")
        self.textDestAlt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textDestAlt.setReadOnly(True)

        self.gridLayout_6.addWidget(self.textDestAlt, 0, 3, 1, 1)

        self.label_27 = QLabel(self.groupDestCoords)
        self.label_27.setObjectName("label_27")

        self.gridLayout_6.addWidget(self.label_27, 1, 0, 1, 1)

        self.textDestDec = QLineEdit(self.groupDestCoords)
        self.textDestDec.setObjectName("textDestDec")
        self.textDestDec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textDestDec.setReadOnly(True)

        self.gridLayout_6.addWidget(self.textDestDec, 1, 1, 1, 1)

        self.label_35 = QLabel(self.groupDestCoords)
        self.label_35.setObjectName("label_35")

        self.gridLayout_6.addWidget(self.label_35, 1, 2, 1, 1)

        self.textDestAz = QLineEdit(self.groupDestCoords)
        self.textDestAz.setObjectName("textDestAz")
        self.textDestAz.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textDestAz.setReadOnly(True)

        self.gridLayout_6.addWidget(self.textDestAz, 1, 3, 1, 1)

        self.verticalLayout_7.addWidget(self.groupDestCoords)

        self.buttonMove = QPushButton(self.groupBox_5)
        self.buttonMove.setObjectName("buttonMove")
        icon1 = QIcon()
        icon1.addFile(":/resources/arrow-alt-circle-right-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonMove.setIcon(icon1)

        self.verticalLayout_7.addWidget(self.buttonMove)

        self.verticalLayout_8.addWidget(self.groupBox_5)

        self.verticalSpacer_5 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_5)

        self.horizontalLayout_7.addLayout(self.verticalLayout_8)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.groupBox = QGroupBox(TelescopeWidget)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout_5 = QVBoxLayout(self.groupBox)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.groupEquatorialOffsets = QGroupBox(self.groupBox)
        self.groupEquatorialOffsets.setObjectName("groupEquatorialOffsets")
        self.gridLayout_12 = QGridLayout(self.groupEquatorialOffsets)
        self.gridLayout_12.setObjectName("gridLayout_12")
        self.label_8 = QLabel(self.groupEquatorialOffsets)
        self.label_8.setObjectName("label_8")

        self.gridLayout_12.addWidget(self.label_8, 3, 0, 1, 1)

        self.textOffsetRA = QLineEdit(self.groupEquatorialOffsets)
        self.textOffsetRA.setObjectName("textOffsetRA")
        sizePolicy.setHeightForWidth(self.textOffsetRA.sizePolicy().hasHeightForWidth())
        self.textOffsetRA.setSizePolicy(sizePolicy)
        self.textOffsetRA.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textOffsetRA.setReadOnly(True)

        self.gridLayout_12.addWidget(self.textOffsetRA, 1, 1, 2, 1)

        self.label_7 = QLabel(self.groupEquatorialOffsets)
        self.label_7.setObjectName("label_7")

        self.gridLayout_12.addWidget(self.label_7, 1, 0, 1, 1)

        self.buttonSetRaOffset = QToolButton(self.groupEquatorialOffsets)
        self.buttonSetRaOffset.setObjectName("buttonSetRaOffset")
        icon2 = QIcon()
        icon2.addFile(":/resources/edit-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonSetRaOffset.setIcon(icon2)

        self.gridLayout_12.addWidget(self.buttonSetRaOffset, 1, 2, 1, 1)

        self.textOffsetDec = QLineEdit(self.groupEquatorialOffsets)
        self.textOffsetDec.setObjectName("textOffsetDec")
        sizePolicy.setHeightForWidth(self.textOffsetDec.sizePolicy().hasHeightForWidth())
        self.textOffsetDec.setSizePolicy(sizePolicy)
        self.textOffsetDec.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textOffsetDec.setReadOnly(True)

        self.gridLayout_12.addWidget(self.textOffsetDec, 3, 1, 1, 1)

        self.buttonSetDecOffset = QToolButton(self.groupEquatorialOffsets)
        self.buttonSetDecOffset.setObjectName("buttonSetDecOffset")
        self.buttonSetDecOffset.setIcon(icon2)

        self.gridLayout_12.addWidget(self.buttonSetDecOffset, 3, 2, 1, 1)

        self.buttonResetEquatorialOffsets = QToolButton(self.groupEquatorialOffsets)
        self.buttonResetEquatorialOffsets.setObjectName("buttonResetEquatorialOffsets")
        icon3 = QIcon()
        icon3.addFile(":/resources/undo-solid.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.buttonResetEquatorialOffsets.setIcon(icon3)

        self.gridLayout_12.addWidget(self.buttonResetEquatorialOffsets, 1, 3, 3, 1)

        self.verticalLayout_5.addWidget(self.groupEquatorialOffsets)

        self.groupHorizontalOffsets = QGroupBox(self.groupBox)
        self.groupHorizontalOffsets.setObjectName("groupHorizontalOffsets")
        self.gridLayout_11 = QGridLayout(self.groupHorizontalOffsets)
        self.gridLayout_11.setObjectName("gridLayout_11")
        self.buttonSetAltOffset = QToolButton(self.groupHorizontalOffsets)
        self.buttonSetAltOffset.setObjectName("buttonSetAltOffset")
        self.buttonSetAltOffset.setIcon(icon2)

        self.gridLayout_11.addWidget(self.buttonSetAltOffset, 0, 3, 1, 1)

        self.textOffsetAlt = QLineEdit(self.groupHorizontalOffsets)
        self.textOffsetAlt.setObjectName("textOffsetAlt")
        sizePolicy.setHeightForWidth(self.textOffsetAlt.sizePolicy().hasHeightForWidth())
        self.textOffsetAlt.setSizePolicy(sizePolicy)
        self.textOffsetAlt.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textOffsetAlt.setReadOnly(True)

        self.gridLayout_11.addWidget(self.textOffsetAlt, 0, 1, 1, 1)

        self.label_5 = QLabel(self.groupHorizontalOffsets)
        self.label_5.setObjectName("label_5")

        self.gridLayout_11.addWidget(self.label_5, 0, 0, 1, 1)

        self.textOffsetAz = QLineEdit(self.groupHorizontalOffsets)
        self.textOffsetAz.setObjectName("textOffsetAz")
        sizePolicy.setHeightForWidth(self.textOffsetAz.sizePolicy().hasHeightForWidth())
        self.textOffsetAz.setSizePolicy(sizePolicy)
        self.textOffsetAz.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.textOffsetAz.setReadOnly(True)

        self.gridLayout_11.addWidget(self.textOffsetAz, 1, 1, 1, 1)

        self.label_6 = QLabel(self.groupHorizontalOffsets)
        self.label_6.setObjectName("label_6")

        self.gridLayout_11.addWidget(self.label_6, 1, 0, 1, 1)

        self.buttonSetAzOffset = QToolButton(self.groupHorizontalOffsets)
        self.buttonSetAzOffset.setObjectName("buttonSetAzOffset")
        self.buttonSetAzOffset.setIcon(icon2)

        self.gridLayout_11.addWidget(self.buttonSetAzOffset, 1, 3, 1, 1)

        self.buttonResetHorizontalOffsets = QToolButton(self.groupHorizontalOffsets)
        self.buttonResetHorizontalOffsets.setObjectName("buttonResetHorizontalOffsets")
        self.buttonResetHorizontalOffsets.setIcon(icon3)

        self.gridLayout_11.addWidget(self.buttonResetHorizontalOffsets, 0, 4, 2, 1)

        self.verticalLayout_5.addWidget(self.groupHorizontalOffsets)

        self.verticalLayout_6.addWidget(self.groupBox)

        self.compassmovewidget = CompassMoveWidget(TelescopeWidget)
        self.compassmovewidget.setObjectName("compassmovewidget")

        self.verticalLayout_6.addWidget(self.compassmovewidget)

        self.verticalSpacer_4 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_4)

        self.horizontalLayout_7.addLayout(self.verticalLayout_6)

        self.horizontalSpacer = QSpacerItem(133, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_7.addItem(self.horizontalSpacer)

        self.widgetSidebar = QWidget(TelescopeWidget)
        self.widgetSidebar.setObjectName("widgetSidebar")

        self.horizontalLayout_7.addWidget(self.widgetSidebar)

        QWidget.setTabOrder(self.labelStatus, self.buttonInit)
        QWidget.setTabOrder(self.buttonInit, self.buttonPark)
        QWidget.setTabOrder(self.buttonPark, self.labelCurRA)
        QWidget.setTabOrder(self.labelCurRA, self.labelCurDec)
        QWidget.setTabOrder(self.labelCurDec, self.labelCurAlt)
        QWidget.setTabOrder(self.labelCurAlt, self.labelCurAz)

        self.retranslateUi(TelescopeWidget)

        self.stackedMove.setCurrentIndex(1)

        QMetaObject.connectSlotsByName(TelescopeWidget)

    # setupUi

    def retranslateUi(self, TelescopeWidget):
        TelescopeWidget.setWindowTitle(QCoreApplication.translate("TelescopeWidget", "Form", None))
        self.groupStatus.setTitle(QCoreApplication.translate("TelescopeWidget", "Status", None))
        self.buttonInit.setText(QCoreApplication.translate("TelescopeWidget", "Init", None))
        self.buttonPark.setText(QCoreApplication.translate("TelescopeWidget", "Park", None))
        self.buttonStop.setText(QCoreApplication.translate("TelescopeWidget", "Stop", None))
        self.label.setText(QCoreApplication.translate("TelescopeWidget", "RA:", None))
        self.label_2.setText(QCoreApplication.translate("TelescopeWidget", "Dec:", None))
        self.label_3.setText(QCoreApplication.translate("TelescopeWidget", "Alt:", None))
        self.label_4.setText(QCoreApplication.translate("TelescopeWidget", "Az:", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("TelescopeWidget", "Move", None))
        self.label_11.setText(QCoreApplication.translate("TelescopeWidget", "Simbad:", None))
        self.buttonSimbadQuery.setText(QCoreApplication.translate("TelescopeWidget", "...", None))
        self.label_9.setText(QCoreApplication.translate("TelescopeWidget", "JPL Horizons:", None))
        self.buttonJplHorizonsQuery.setText(QCoreApplication.translate("TelescopeWidget", "...", None))
        self.comboSolarSystemBody.setItemText(0, "")
        self.comboSolarSystemBody.setItemText(1, QCoreApplication.translate("TelescopeWidget", "Sun", None))
        self.comboSolarSystemBody.setItemText(2, QCoreApplication.translate("TelescopeWidget", "Mercury", None))
        self.comboSolarSystemBody.setItemText(3, QCoreApplication.translate("TelescopeWidget", "Venus", None))
        self.comboSolarSystemBody.setItemText(4, QCoreApplication.translate("TelescopeWidget", "Moon", None))
        self.comboSolarSystemBody.setItemText(5, QCoreApplication.translate("TelescopeWidget", "Mars", None))
        self.comboSolarSystemBody.setItemText(6, QCoreApplication.translate("TelescopeWidget", "Jupiter", None))
        self.comboSolarSystemBody.setItemText(7, QCoreApplication.translate("TelescopeWidget", "Saturn", None))
        self.comboSolarSystemBody.setItemText(8, QCoreApplication.translate("TelescopeWidget", "Uranus", None))
        self.comboSolarSystemBody.setItemText(9, QCoreApplication.translate("TelescopeWidget", "Neptune", None))

        self.label_12.setText(QCoreApplication.translate("TelescopeWidget", "Solar system:", None))
        self.label_23.setText(QCoreApplication.translate("TelescopeWidget", "RA:", None))
        self.label_22.setText(QCoreApplication.translate("TelescopeWidget", "Dec:", None))
        self.label_25.setText(QCoreApplication.translate("TelescopeWidget", "Az:", None))
        self.label_24.setText(QCoreApplication.translate("TelescopeWidget", "Alt:", None))
        self.spinMoveAlt.setSuffix(QCoreApplication.translate("TelescopeWidget", " \u00b0", None))
        self.spinMoveAz.setSuffix(QCoreApplication.translate("TelescopeWidget", " \u00b0", None))
        self.label_37.setText(QCoreApplication.translate("TelescopeWidget", "Lat:", None))
        self.spinMoveHGSLon.setSuffix("")
        self.label_38.setText(QCoreApplication.translate("TelescopeWidget", "Lon:", None))
        self.spinMoveHGSLat.setSuffix(QCoreApplication.translate("TelescopeWidget", " \u00b0", None))
        self.label_42.setText(QCoreApplication.translate("TelescopeWidget", "Tx", None))
        self.spinMoveHelioProjectiveRadialTx.setSuffix(QCoreApplication.translate("TelescopeWidget", '"', None))
        self.spinMoveHelioProjectiveRadialTx.setPrefix("")
        self.label_41.setText(QCoreApplication.translate("TelescopeWidget", "Ty", None))
        self.spinMoveHelioProjectiveRadialTy.setSuffix(QCoreApplication.translate("TelescopeWidget", '"', None))
        self.label_39.setText(QCoreApplication.translate("TelescopeWidget", "Psi:", None))
        self.spinMoveHelioprojectiveRadialMu.setSuffix("")
        self.label_40.setText(QCoreApplication.translate("TelescopeWidget", "Mu:", None))
        self.spinMoveHelioprojectiveRadialPsi.setSuffix(QCoreApplication.translate("TelescopeWidget", " \u00b0", None))
        self.label_21.setText(QCoreApplication.translate("TelescopeWidget", "JPL Horizons:", None))
        self.buttonHorizonsQuery.setText(QCoreApplication.translate("TelescopeWidget", "...", None))
        self.label_29.setText(QCoreApplication.translate("TelescopeWidget", "\u03a9:", None))
        self.label_32.setText(QCoreApplication.translate("TelescopeWidget", "e:", None))
        self.label_34.setText(QCoreApplication.translate("TelescopeWidget", "T:", None))
        self.label_28.setText(QCoreApplication.translate("TelescopeWidget", "i:", None))
        self.label_30.setText(QCoreApplication.translate("TelescopeWidget", "\u03c9:", None))
        self.label_33.setText(QCoreApplication.translate("TelescopeWidget", "MA:", None))
        self.label_31.setText(QCoreApplication.translate("TelescopeWidget", "a:", None))
        self.spinOrbitElementsSemiMajorAxis.setSuffix(QCoreApplication.translate("TelescopeWidget", " AU", None))
        self.spinOrbitElementsIncl.setSuffix(QCoreApplication.translate("TelescopeWidget", " \u00b0", None))
        self.spinOrbitElementsMA.setSuffix(QCoreApplication.translate("TelescopeWidget", " \u00b0", None))
        self.spinOrbitElementsOmega.setSuffix(QCoreApplication.translate("TelescopeWidget", " \u00b0", None))
        self.spinOrbitElementsPerifocus.setSuffix(QCoreApplication.translate("TelescopeWidget", " \u00b0", None))
        self.groupDestCoords.setTitle(QCoreApplication.translate("TelescopeWidget", "Destination", None))
        self.label_26.setText(QCoreApplication.translate("TelescopeWidget", "RA:", None))
        self.label_36.setText(QCoreApplication.translate("TelescopeWidget", " Alt:", None))
        self.label_27.setText(QCoreApplication.translate("TelescopeWidget", "Dec:", None))
        self.label_35.setText(QCoreApplication.translate("TelescopeWidget", "Az:", None))
        self.buttonMove.setText(QCoreApplication.translate("TelescopeWidget", "Move", None))
        self.groupBox.setTitle(QCoreApplication.translate("TelescopeWidget", "Offsets", None))
        self.groupEquatorialOffsets.setTitle(QCoreApplication.translate("TelescopeWidget", "Equitorial", None))
        self.label_8.setText(QCoreApplication.translate("TelescopeWidget", "Dec:", None))
        self.label_7.setText(QCoreApplication.translate("TelescopeWidget", "RA:", None))
        self.buttonSetRaOffset.setText(QCoreApplication.translate("TelescopeWidget", "set", None))
        self.buttonSetDecOffset.setText(QCoreApplication.translate("TelescopeWidget", "set", None))
        self.buttonResetEquatorialOffsets.setText(QCoreApplication.translate("TelescopeWidget", "reset", None))
        self.groupHorizontalOffsets.setTitle(QCoreApplication.translate("TelescopeWidget", "Horizontal", None))
        self.buttonSetAltOffset.setText(QCoreApplication.translate("TelescopeWidget", "set", None))
        self.label_5.setText(QCoreApplication.translate("TelescopeWidget", "Alt:", None))
        self.label_6.setText(QCoreApplication.translate("TelescopeWidget", "Az:", None))
        self.buttonSetAzOffset.setText(QCoreApplication.translate("TelescopeWidget", "set", None))
        self.buttonResetHorizontalOffsets.setText(QCoreApplication.translate("TelescopeWidget", "reset", None))

    # retranslateUi
