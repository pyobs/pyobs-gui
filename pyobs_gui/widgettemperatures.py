import logging

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSignal

from pyobs.interfaces import ITemperatures
from pyobs_gui.basewidget import BaseWidget
from .qt.widgettemperatures import Ui_WidgetTemperatures


log = logging.getLogger(__name__)


class WidgetTemperatures(BaseWidget, Ui_WidgetTemperatures):
    signal_update_gui = pyqtSignal()

    def __init__(self, **kwargs):
        BaseWidget.__init__(self, update_func=self._update, update_interval=10, **kwargs)
        self.setupUi(self)

        # status
        self._temps = None

        # widgets
        self._widgets = {}

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def _update(self):
        # get temps
        self._temps = await self.module.get_temperatures()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self):
        if self._temps is not None:
            # enable myself
            self.setEnabled(True)

            # get layout
            layout = self.groupBox.layout()

            # loop temps
            for key in sorted(self._temps.keys()):
                value = self._temps[key]

                # does key widget exist?
                if key not in self._widgets:
                    # create label and widget
                    label = QtWidgets.QLabel(key + ':')
                    widget = QtWidgets.QLineEdit()
                    widget.setReadOnly(True)
                    widget.setAlignment(QtCore.Qt.AlignHCenter)

                    # get new row
                    row = layout.rowCount()

                    # add them to layout
                    layout.addWidget(label, row, 0)
                    layout.addWidget(widget, row, 1)

                    # and to dict
                    self._widgets[key] = (label, widget)

                # set value
                self._widgets[key][1].setText('N/A' if value is None else '%.2f °C' % value)

            # now loop widgets and check, whether we need to delete some
            for key, (label, widget) in self._widgets.items():
                if key not in self._widgets:
                    layout.removeWidget(label)
                    layout.removeWidget(widget)
