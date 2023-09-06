import datetime
import logging
import os
from typing import Any, Dict, Tuple, Optional

import pandas as pd
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import pyqtSlot
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.dates import date2num, DateFormatter

from pyobs.interfaces import ITemperatures
from pyobs.utils.time import Time
from .base import BaseWidget
from .qt.temperaturesplotwidget_ui import Ui_TemperaturesPlotWidget


log = logging.getLogger(__name__)


class TemperaturesPlotWidget(QtWidgets.QWidget, Ui_TemperaturesPlotWidget):
    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        self.setupUi(self)

        # add plot
        self.figure, self.ax = plt.subplots()
        layout = QtWidgets.QVBoxLayout(self.frame)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        self.frame.setLayout(layout)

        # format time
        fmt = DateFormatter("%H:%m:%s")
        self.ax.xaxis.set_major_formatter(fmt)

        # data
        self.data: Optional[pd.DataFrame] = None

        # show options
        self.comboShow.addItems(["All", "Last minute", "Last 5 minutes"])
        self.show_option = "All"

        # log
        self.log_file = ""
        self.log_dir = os.path.expanduser("~")

    def add_data(self, time: Time, data: Dict[str, float]) -> None:
        # copy data, add time
        data_copy = dict(data)
        data_copy.update({"time": time.to_datetime()})
        df = pd.DataFrame({k: [v] for k, v in data_copy.items()})

        # init data
        if self.data is None:
            self.data = pd.DataFrame(columns=df.columns)

        # append
        self.data = pd.concat([self.data, df], ignore_index=True, axis=0)

        # save?
        if self.checkLogFile.isChecked() and self.log_file != "":
            self.data.to_csv(self.log_file, index=False)

        # what to plot?
        if self.show_option == "All":
            d = self.data
        elif self.show_option == "Last minute":
            d = self.data[self.data["time"] >= datetime.datetime.utcnow() - datetime.timedelta(minutes=1)]
        elif self.show_option == "Last 5 minutes":
            d = self.data[self.data["time"] >= datetime.datetime.utcnow() - datetime.timedelta(minutes=5)]
        else:
            return

        # plot
        self.ax.clear()
        for col in d.columns:
            # ignore time column
            if col == "time":
                continue

            # plot
            self.ax.plot(d["time"], d[col], label=col)

        # draw
        self.ax.set_xlabel("Time [UT]")
        self.ax.set_ylabel("Temperature [°C]")
        self.ax.grid(linestyle=":", alpha=0.5)
        self.ax.set_axisbelow(True)
        if len(d.columns) > 2:
            # only show legend, if data exists
            self.ax.legend()
        self.canvas.draw()

    @pyqtSlot(str)
    def on_comboShow_currentTextChanged(self, opt: str) -> None:
        self.show_option = opt

    @pyqtSlot()
    def on_buttonPickFile_clicked(self) -> None:
        filename, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Select log file", self.log_dir, "CSV files (*.csv)")
        if filename is not None:
            self.lineLogFile.setText(filename)
            self.log_file = filename
            self.log_dir = os.path.dirname(filename)
