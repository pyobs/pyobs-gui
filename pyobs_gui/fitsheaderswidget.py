import logging
import os
from typing import Any, Optional, List, Dict, Tuple

from PyQt5 import QtCore, QtWidgets

from .base import BaseWidget
from .qt.fitsheaderswidget_ui import Ui_FitsHeadersWidget


log = logging.getLogger(__name__)


class FitsHeadersWidget(QtWidgets.QWidget, BaseWidget, Ui_FitsHeadersWidget):
    def __init__(self, **kwargs: Any):
        QtWidgets.QWidget.__init__(self)
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        # this only works in Linux
        try:
            # set current username
            import pwd

            self.textUser.setText(pwd.getpwuid(os.getuid()).pw_name)
        except ModuleNotFoundError:
            pass

    def get_fits_headers(self, namespaces: Optional[List[str]] = None, **kwargs: Any) -> Dict[str, Tuple[Any, str]]:
        """Returns FITS header for the current status of this module.

        Args:
            namespaces: If given, only return FITS headers for the given namespaces.

        Returns:
            Dictionary containing FITS headers.
        """

        # check sender
        if "sender" in kwargs and kwargs["sender"] != self.module.name:
            return {}

        # don't want to send headers?
        if not self.checkAddHeaders.isChecked():
            return {}

        # define basic headers
        headers = {
            "OBJECT": (self.textObject.text(), "Observed object"),
            "USER": (self.textUser.text(), "Name of user"),
        }

        # addition headers?
        for row in range(self.tableAdditionalHeaders.rowCount()):
            # get key and value
            key = self.tableAdditionalHeaders.item(row, 0).text()
            value = self.tableAdditionalHeaders.item(row, 1).text()

            # add it
            if len(key) > 0 and len(value) > 0:
                headers[key] = value

        # return them
        return headers

    @QtCore.pyqtSlot(name="on_buttonAddHeader_clicked")
    def add_header(self) -> None:
        """Increase row count by 1."""
        self.tableAdditionalHeaders.setRowCount(self.tableAdditionalHeaders.rowCount() + 1)

    @QtCore.pyqtSlot(name="on_buttonDelHeader_clicked")
    def del_header(self) -> None:
        """Delete current row"""

        # get row
        row = self.tableAdditionalHeaders.currentRow()
        if row == -1:
            return

        # delete it
        self.tableAdditionalHeaders.removeRow(row)
