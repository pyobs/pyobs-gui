import asyncio
from typing import Any, Union
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

"""
Helper methods

Original versions of dialog_async_exec and QAsyncMessageBox taken from:
https://github.com/duniter/sakia/blob/1de71a18ec635ca63cf4784e4284eea7f6c1c8a1/src/sakia/gui/widgets/dialogs.py
"""


def dialog_async_exec(dialog: QtWidgets.QWidget) -> asyncio.Future[Any]:
    future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()
    dialog.finished.connect(lambda r: future.set_result(r))
    dialog.open()
    return future


class QAsyncMessageBox:
    @staticmethod
    def critical(
        parent: QtWidgets.QWidget, title: str, label: str, buttons: QMessageBox.StandardButtons = QMessageBox.Ok
    ) -> asyncio.Future[Any]:
        dialog = QMessageBox(QMessageBox.Critical, title, label, buttons, parent)
        return dialog_async_exec(dialog)

    @staticmethod
    def information(
        parent: QtWidgets.QWidget, title: str, label: str, buttons: QMessageBox.StandardButtons = QMessageBox.Ok
    ) -> asyncio.Future[Any]:
        dialog = QMessageBox(QMessageBox.Information, title, label, buttons, parent)
        return dialog_async_exec(dialog)

    @staticmethod
    def warning(
        parent: QtWidgets.QWidget, title: str, label: str, buttons: QMessageBox.StandardButtons = QMessageBox.Ok
    ) -> asyncio.Future[Any]:
        return QAsyncMessageBox._dialog(parent, title, label, buttons)

    @staticmethod
    def question(
        parent: QtWidgets.QWidget,
        title: str,
        label: str,
        buttons: QMessageBox.StandardButtons = QMessageBox.Yes | QMessageBox.No,
    ) -> asyncio.Future[Any]:
        dialog = QMessageBox(QMessageBox.Question, title, label, buttons, parent)
        return dialog_async_exec(dialog)

    @staticmethod
    def _dialog(
        parent: QtWidgets.QWidget,
        title: str,
        label: str,
        buttons: Union[QMessageBox.StandardButton, QMessageBox.StandardButton],
    ) -> asyncio.Future[Any]:
        dialog = QMessageBox(parent)
        dialog.setWindowTitle("Error")
        dialog.setText(title)
        dialog.setInformativeText(label)
        dialog.setStandardButtons(buttons)
        return dialog_async_exec(dialog)
