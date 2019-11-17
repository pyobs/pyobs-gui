from PyQt5.QtCore import pyqtSignal
from PyQt5 import QtWidgets

from pyobs.interfaces import IScriptRunner
from pyobs_gui.basewidget import BaseWidget


class WidgetScript(BaseWidget):
    signal_update_gui = pyqtSignal()

    def __init__(self, module, comm, parent=None):
        BaseWidget.__init__(self, parent)
        self.module = module    # type: IScriptRunner
        self.comm = comm        # type: Comm

        # build GUI
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)
        self.script = QtWidgets.QTextEdit()
        layout.addWidget(self.script)
        self.button = QtWidgets.QPushButton()
        self.button.setText('Execute')
        self.button.clicked.connect(self.execute)
        layout.addWidget(self.button)

    def execute(self):
        self.run_async(self.module.run_script, self.script.toPlainText())
