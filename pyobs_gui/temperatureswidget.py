import logging
from typing import Any, Dict, Tuple
from PyQt5 import QtWidgets, QtCore

from pyobs.interfaces import ITemperatures
from .base import BaseWidget
from .qt.temperatureswidget_ui import Ui_TemperaturesWidget


log = logging.getLogger(__name__)


class TemperaturesWidget(QtWidgets.QWidget, BaseWidget, Ui_TemperaturesWidget):
    signal_update_gui = QtCore.pyqtSignal()

    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, update_func=self._update, update_interval=10, **kwargs)
        self.setupUi(self)

        # status
        self._temps = None

        # widgets
        self._widgets: Dict[str, Tuple[QtWidgets.QLabel, QtWidgets.QLineEdit]] = {}

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    async def _update(self) -> None:
        # get temps
        if isinstance(self.module, ITemperatures):
            self._temps = await self.module.get_temperatures()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
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
                    label = QtWidgets.QLabel(key + ":")
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
                self._widgets[key][1].setText("N/A" if value is None else "%.2f °C" % value)

            # now loop widgets and check, whether we need to delete some
            for key, (label, widget) in self._widgets.items():
                if key not in self._widgets:
                    layout.removeWidget(label)
                    layout.removeWidget(widget)
