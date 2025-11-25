# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'fitsheaderswidget.ui'
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
from PySide6.QtWidgets import (QApplication, QCheckBox, QFormLayout, QGroupBox,
    QHBoxLayout, QHeaderView, QLabel, QLineEdit,
    QSizePolicy, QSpacerItem, QTableWidget, QTableWidgetItem,
    QToolButton, QWidget)

class Ui_FitsHeadersWidget(object):
    def setupUi(self, FitsHeadersWidget):
        if not FitsHeadersWidget.objectName():
            FitsHeadersWidget.setObjectName(u"FitsHeadersWidget")
        FitsHeadersWidget.resize(262, 425)
        self.horizontalLayout = QHBoxLayout(FitsHeadersWidget)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.groupBox = QGroupBox(FitsHeadersWidget)
        self.groupBox.setObjectName(u"groupBox")
        self.formLayout = QFormLayout(self.groupBox)
        self.formLayout.setObjectName(u"formLayout")
        self.checkAddHeaders = QCheckBox(self.groupBox)
        self.checkAddHeaders.setObjectName(u"checkAddHeaders")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.checkAddHeaders)

        self.label = QLabel(self.groupBox)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label)

        self.textObject = QLineEdit(self.groupBox)
        self.textObject.setObjectName(u"textObject")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.textObject)

        self.label_3 = QLabel(self.groupBox)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.textUser = QLineEdit(self.groupBox)
        self.textUser.setObjectName(u"textUser")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.textUser)

        self.tableAdditionalHeaders = QTableWidget(self.groupBox)
        if (self.tableAdditionalHeaders.columnCount() < 2):
            self.tableAdditionalHeaders.setColumnCount(2)
        __qtablewidgetitem = QTableWidgetItem()
        self.tableAdditionalHeaders.setHorizontalHeaderItem(0, __qtablewidgetitem)
        __qtablewidgetitem1 = QTableWidgetItem()
        self.tableAdditionalHeaders.setHorizontalHeaderItem(1, __qtablewidgetitem1)
        self.tableAdditionalHeaders.setObjectName(u"tableAdditionalHeaders")
        self.tableAdditionalHeaders.setColumnCount(2)
        self.tableAdditionalHeaders.horizontalHeader().setDefaultSectionSize(50)
        self.tableAdditionalHeaders.horizontalHeader().setStretchLastSection(True)
        self.tableAdditionalHeaders.verticalHeader().setVisible(False)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.SpanningRole, self.tableAdditionalHeaders)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.buttonAddHeader = QToolButton(self.groupBox)
        self.buttonAddHeader.setObjectName(u"buttonAddHeader")

        self.horizontalLayout_2.addWidget(self.buttonAddHeader)

        self.buttonDelHeader = QToolButton(self.groupBox)
        self.buttonDelHeader.setObjectName(u"buttonDelHeader")

        self.horizontalLayout_2.addWidget(self.buttonDelHeader)


        self.formLayout.setLayout(4, QFormLayout.ItemRole.SpanningRole, self.horizontalLayout_2)


        self.horizontalLayout.addWidget(self.groupBox)


        self.retranslateUi(FitsHeadersWidget)

        QMetaObject.connectSlotsByName(FitsHeadersWidget)
    # setupUi

    def retranslateUi(self, FitsHeadersWidget):
        FitsHeadersWidget.setWindowTitle(QCoreApplication.translate("FitsHeadersWidget", u"Form", None))
        self.groupBox.setTitle(QCoreApplication.translate("FitsHeadersWidget", u"FITS headers", None))
        self.checkAddHeaders.setText(QCoreApplication.translate("FitsHeadersWidget", u"Add headers", None))
        self.label.setText(QCoreApplication.translate("FitsHeadersWidget", u"OBJECT:", None))
        self.label_3.setText(QCoreApplication.translate("FitsHeadersWidget", u"USER:", None))
        ___qtablewidgetitem = self.tableAdditionalHeaders.horizontalHeaderItem(0)
        ___qtablewidgetitem.setText(QCoreApplication.translate("FitsHeadersWidget", u"Key", None));
        ___qtablewidgetitem1 = self.tableAdditionalHeaders.horizontalHeaderItem(1)
        ___qtablewidgetitem1.setText(QCoreApplication.translate("FitsHeadersWidget", u"Value", None));
        self.buttonAddHeader.setText(QCoreApplication.translate("FitsHeadersWidget", u"+", None))
        self.buttonDelHeader.setText(QCoreApplication.translate("FitsHeadersWidget", u"-", None))
    # retranslateUi

