from PyQt5.QtWidgets import QWidget
from datadisplaywidget_ui import Ui_WidgetDataDisplay


class DataDisplayWidget(QWidget, Ui_WidgetDataDisplay):
    def __init__(self, *args, **kwargs):
        QWidget.__init__(self, *args, **kwargs)
        self.setupUi(self)
