from PyQt5.QtGui import QIcon
from PyQt5.QtDesigner import QPyDesignerCustomWidgetPlugin

from datadisplaywidget import DataDisplayWidget


class DataDisplayPlugin(QPyDesignerCustomWidgetPlugin):
    def __init__(self, parent=None):
        super(DataDisplayPlugin, self).__init__(parent)

        self.initialized = False

    def initialize(self, core):
        if self.initialized:
            return

        self.initialized = True

    def isInitialized(self):
        return self.initialized

    def createWidget(self, parent):
        return DataDisplayWidget(parent)

    def name(self):
        return "DataDisplayWidget"

    def group(self):
        return "pyobs Widgets"

    def icon(self):
        return QIcon()

    def toolTip(self):
        return ""

    def whatsThis(self):
        return ""

    def isContainer(self):
        return False

    def includeFile(self):
        return "datadisplaywidget"
