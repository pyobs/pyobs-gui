import threading

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import pyqtSignal, pyqtSlot
from astroplan import Observer
import logging

from pyobs.comm import Comm
from pyobs.interfaces import IWeather
from pyobs.utils.time import Time
from .qt.widgetweather import Ui_widgetWeather
from .basewidget import BaseWidget


log = logging.getLogger(__name__)


AVERAGE_SENSOR_FIELDS = [
    {'field': 'time', 'label': 'Time', 'unit': ''},
    {'field': 'temp', 'label': 'Temp.', 'unit': '°C'},
    {'field': 'humid', 'label': 'Rel. humid.', 'unit': '%'},
    {'field': 'dewpoint', 'label': 'Dew point', 'unit': '°C'},
    {'field': 'press', 'label': 'Press.', 'unit': '°E of N'},
    {'field': 'winddir', 'label': 'Wind dir', 'unit': '°E of N'},
    {'field': 'windspeed', 'label': 'Wind speed', 'unit': 'km/h'},
    {'field': 'particles', 'label': 'Particles', 'unit': 'ppqm'},
    {'field': 'rain', 'label': 'Rain', 'unit': ''},
    {'field': 'skytemp', 'label': 'Rel. sky temp.', 'unit': '°C'},
    {'field': 'sunalt', 'label': 'Sun', 'unit': '°'},
]


class WidgetCurrentSensor(QtWidgets.QFrame):
    def __init__(self, label: str, unit: str, *args, **kwargs):
        QtWidgets.QFrame.__init__(self, *args, **kwargs)

        # create layout
        layout = QtWidgets.QVBoxLayout()
        self.setLayout(layout)

        # font
        font1 = QtGui.QFont("Times", 8, QtGui.QFont.Normal)
        font2 = QtGui.QFont("Times", 12, QtGui.QFont.Bold)

        # add label
        self._label = QtWidgets.QLabel(label)
        self._label.setFont(font1)
        self._label.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self._label)

        # add value
        self._value = QtWidgets.QLabel()
        self._value.setFont(font2)
        self._value.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self._value)

        # add unit
        if unit is not None:
            self._unit = QtWidgets.QLabel(unit)
            self._unit.setFont(font1)
            self._unit.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(self._unit)
        else:
            self._unit = None

    def set_value(self, value: str):
        self._value.setText(value)

    def set_good(self, good: bool):
        # which colour?
        if good is None:
            stylesheet = ''
        else:
            stylesheet = 'QLabel {color: ' + ('lime' if good else 'red') + ';}'

        # set colour
        self._label.setStyleSheet(stylesheet)
        self._value.setStyleSheet(stylesheet)
        if self._unit is not None:
            self._unit.setStyleSheet(stylesheet)


class WidgetWeather(BaseWidget, Ui_widgetWeather):
    signal_update_gui = pyqtSignal()

    def __init__(self, module: IWeather, comm: Comm, parent=None):
        BaseWidget.__init__(self, parent=parent, update_func=self._update, update_interval=10)
        self.setupUi(self)
        self.module = module
        self.comm = comm

        # weather info
        self._current_weather = {}
        self._current_sensors = []
        self._current_widgets = {}

        # before first update, disable mys
        self.setEnabled(False)

        # connect signals
        self.signal_update_gui.connect(self.update_gui)

    def _update(self):
        """Update values from weather module."""

        # get current weather
        self._current_weather = self.module.get_current_weather().wait()

        # signal GUI update
        self.signal_update_gui.emit()

    def update_gui(self):
        # enable myself and set filter
        self.setEnabled(True)

        # get current weather
        cur = self._current_weather['sensors']

        # update current
        if 'sensors' in self._current_weather:
            # get current list of sensors
            current_sensors = list(sorted(cur.keys()))

            # did it change?
            if current_sensors != self._current_sensors:
                layout = self.frameCurrent.layout()

                # remove all widgets from frameCurrent
                for w in self._current_widgets.values():
                    w.setParent(None)

                # add time
                self._current_widgets['time'] = WidgetCurrentSensor('Time', None)
                layout.addWidget(self._current_widgets['time'])

                # loop sensor types
                for sensor in AVERAGE_SENSOR_FIELDS:
                    if sensor['field'] in current_sensors:
                        widget = WidgetCurrentSensor(sensor['label'], sensor['unit'])
                        self._current_widgets[sensor['field']] = widget
                        layout.addWidget(widget)

            # set time
            if 'time' in self._current_weather and self._current_weather['time'] is not None:
                t = Time(self._current_weather['time'])
                self._current_widgets['time'].set_value(t.strftime('%Y-%m-%d\n%H:%M:%S'))
            else:
                self._current_widgets['time'].set_value('')

            # set values
            for sensor in AVERAGE_SENSOR_FIELDS:
                f = sensor['field']
                if f in current_sensors:
                    format = '%d' if f == 'rain' else '%.2f'
                    self._current_widgets[f].set_value(format % cur[f]['value'])
                    self._current_widgets[f].set_good(cur[f]['good'])

            # store it
            self._current_sensors = current_sensors


__all__ = ['WidgetWeather']
