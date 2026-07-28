# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwindow.ui'
##
## Created by: Qt User Interface Compiler version 6.11.1
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
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QHeaderView,
    QLabel, QListView, QListWidget, QListWidgetItem,
    QMainWindow, QPushButton, QSizePolicy, QSpacerItem,
    QSplitter, QStackedWidget, QTableView, QToolButton,
    QVBoxLayout, QWidget)
from . import resources_rc

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1374, 916)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.labelAutonomousWarning = QLabel(self.centralwidget)
        self.labelAutonomousWarning.setObjectName(u"labelAutonomousWarning")
        palette = QPalette()
        brush = QBrush(QColor(0, 0, 0, 255))
        brush.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        brush1 = QBrush(QColor(35, 38, 41, 255))
        brush1.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        brush2 = QBrush(QColor(255, 0, 0, 255))
        brush2.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush2)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush2)
        brush3 = QBrush(QColor(110, 113, 117, 255))
        brush3.setStyle(Qt.BrushStyle.SolidPattern)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush3)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush2)
        palette.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush2)
        self.labelAutonomousWarning.setPalette(palette)
        font = QFont()
        font.setPointSize(12)
        font.setBold(True)
        self.labelAutonomousWarning.setFont(font)
        self.labelAutonomousWarning.setAutoFillBackground(True)
        self.labelAutonomousWarning.setFrameShape(QFrame.Shape.Box)
        self.labelAutonomousWarning.setLineWidth(2)
        self.labelAutonomousWarning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelAutonomousWarning.setMargin(0)

        self.verticalLayout.addWidget(self.labelAutonomousWarning)

        self.labelWeatherWarning = QLabel(self.centralwidget)
        self.labelWeatherWarning.setObjectName(u"labelWeatherWarning")
        palette1 = QPalette()
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.WindowText, brush)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Base, brush1)
        brush4 = QBrush(QColor(255, 85, 0, 255))
        brush4.setStyle(Qt.BrushStyle.SolidPattern)
        palette1.setBrush(QPalette.ColorGroup.Active, QPalette.ColorRole.Window, brush4)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.WindowText, brush)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Base, brush1)
        palette1.setBrush(QPalette.ColorGroup.Inactive, QPalette.ColorRole.Window, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.WindowText, brush3)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, brush4)
        palette1.setBrush(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Window, brush4)
        self.labelWeatherWarning.setPalette(palette1)
        self.labelWeatherWarning.setFont(font)
        self.labelWeatherWarning.setAutoFillBackground(True)
        self.labelWeatherWarning.setFrameShape(QFrame.Shape.Box)
        self.labelWeatherWarning.setFrameShadow(QFrame.Shadow.Plain)
        self.labelWeatherWarning.setLineWidth(2)
        self.labelWeatherWarning.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.labelWeatherWarning.setMargin(0)

        self.verticalLayout.addWidget(self.labelWeatherWarning)

        self.splitterNav = QSplitter(self.centralwidget)
        self.splitterNav.setObjectName(u"splitterNav")
        self.splitterNav.setOrientation(Qt.Orientation.Horizontal)
        self.widgetNavSidebar = QWidget(self.splitterNav)
        self.widgetNavSidebar.setObjectName(u"widgetNavSidebar")
        self.layoutNavSidebar = QVBoxLayout(self.widgetNavSidebar)
        self.layoutNavSidebar.setSpacing(4)
        self.layoutNavSidebar.setObjectName(u"layoutNavSidebar")
        self.layoutNavSidebar.setContentsMargins(0, 0, 0, 4)
        self.listPages = QListWidget(self.widgetNavSidebar)
        self.listPages.setObjectName(u"listPages")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listPages.sizePolicy().hasHeightForWidth())
        self.listPages.setSizePolicy(sizePolicy)
        self.listPages.setMinimumSize(QSize(90, 90))
        self.listPages.setFrameShape(QFrame.Shape.NoFrame)
        self.listPages.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.listPages.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.listPages.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.listPages.setProperty(u"showDropIndicator", False)
        self.listPages.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.listPages.setDefaultDropAction(Qt.DropAction.IgnoreAction)
        self.listPages.setIconSize(QSize(22, 22))
        self.listPages.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.listPages.setMovement(QListView.Movement.Static)
        self.listPages.setFlow(QListView.Flow.TopToBottom)
        self.listPages.setViewMode(QListView.ViewMode.ListMode)
        self.listPages.setTextElideMode(Qt.TextElideMode.ElideRight)
        self.listPages.setSelectionRectVisible(False)

        self.layoutNavSidebar.addWidget(self.listPages)

        self.labelLoggedInAs = QLabel(self.widgetNavSidebar)
        self.labelLoggedInAs.setObjectName(u"labelLoggedInAs")

        self.layoutNavSidebar.addWidget(self.labelLoggedInAs)

        self.buttonQuit = QPushButton(self.widgetNavSidebar)
        self.buttonQuit.setObjectName(u"buttonQuit")

        self.layoutNavSidebar.addWidget(self.buttonQuit)

        self.splitterNav.addWidget(self.widgetNavSidebar)
        self.splitterLog = QSplitter(self.splitterNav)
        self.splitterLog.setObjectName(u"splitterLog")
        self.splitterLog.setOrientation(Qt.Orientation.Vertical)
        self.splitterToolBox = QSplitter(self.splitterLog)
        self.splitterToolBox.setObjectName(u"splitterToolBox")
        self.splitterToolBox.setOrientation(Qt.Orientation.Horizontal)
        self.stackedWidget = QStackedWidget(self.splitterToolBox)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.splitterToolBox.addWidget(self.stackedWidget)
        self.splitterLog.addWidget(self.splitterToolBox)
        self.splitterClients = QSplitter(self.splitterLog)
        self.splitterClients.setObjectName(u"splitterClients")
        self.splitterClients.setOrientation(Qt.Orientation.Horizontal)
        self.tableLog = QTableView(self.splitterClients)
        self.tableLog.setObjectName(u"tableLog")
        self.tableLog.setFrameShape(QFrame.Shape.NoFrame)
        self.tableLog.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tableLog.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.tableLog.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tableLog.setGridStyle(Qt.PenStyle.NoPen)
        self.tableLog.setSortingEnabled(False)
        self.splitterClients.addWidget(self.tableLog)
        self.tableLog.horizontalHeader().setVisible(False)
        self.tableLog.horizontalHeader().setStretchLastSection(True)
        self.tableLog.verticalHeader().setVisible(False)
        self.tableLog.verticalHeader().setMinimumSectionSize(20)
        self.tableLog.verticalHeader().setDefaultSectionSize(20)
        self.widgetLogTools = QWidget(self.splitterClients)
        self.widgetLogTools.setObjectName(u"widgetLogTools")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.widgetLogTools.sizePolicy().hasHeightForWidth())
        self.widgetLogTools.setSizePolicy(sizePolicy1)
        self.layoutLogTools = QVBoxLayout(self.widgetLogTools)
        self.layoutLogTools.setObjectName(u"layoutLogTools")
        self.layoutLogTools.setContentsMargins(2, 2, 2, 2)
        self.buttonClearLog = QToolButton(self.widgetLogTools)
        self.buttonClearLog.setObjectName(u"buttonClearLog")

        self.layoutLogTools.addWidget(self.buttonClearLog)

        self.buttonCopyLog = QToolButton(self.widgetLogTools)
        self.buttonCopyLog.setObjectName(u"buttonCopyLog")

        self.layoutLogTools.addWidget(self.buttonCopyLog)

        self.buttonSelectClients = QToolButton(self.widgetLogTools)
        self.buttonSelectClients.setObjectName(u"buttonSelectClients")
        self.buttonSelectClients.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)

        self.layoutLogTools.addWidget(self.buttonSelectClients)

        self.verticalSpacerLogTools = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.layoutLogTools.addItem(self.verticalSpacerLogTools)

        self.splitterClients.addWidget(self.widgetLogTools)
        self.splitterLog.addWidget(self.splitterClients)
        self.splitterNav.addWidget(self.splitterLog)

        self.verticalLayout.addWidget(self.splitterNav)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(-1)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"pyobs GUI", None))
        self.labelAutonomousWarning.setText(QCoreApplication.translate("MainWindow", u"!!! WARNING: autonomous module(s) active !!!", None))
        self.labelWeatherWarning.setText(QCoreApplication.translate("MainWindow", u"!!! WARNING: weather module disabled !!!", None))
        self.labelLoggedInAs.setText(QCoreApplication.translate("MainWindow", u"Logged in as: ", None))
        self.buttonQuit.setText(QCoreApplication.translate("MainWindow", u"Quit", None))
#if QT_CONFIG(tooltip)
        self.buttonClearLog.setToolTip(QCoreApplication.translate("MainWindow", u"Clear log", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.buttonCopyLog.setToolTip(QCoreApplication.translate("MainWindow", u"Copy log to clipboard", None))
#endif // QT_CONFIG(tooltip)
#if QT_CONFIG(tooltip)
        self.buttonSelectClients.setToolTip(QCoreApplication.translate("MainWindow", u"Select clients shown in log", None))
#endif // QT_CONFIG(tooltip)
    # retranslateUi

