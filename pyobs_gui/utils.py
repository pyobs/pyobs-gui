import asyncio
from typing import Any
from PySide6 import QtWidgets  # type: ignore
from PySide6.QtWidgets import QMessageBox  # type: ignore

"""
Helper methods

Original versions of dialog_async_exec and QAsyncMessageBox taken from:
https://github.com/duniter/sakia/blob/1de71a18ec635ca63cf4784e4284eea7f6c1c8a1/src/sakia/gui/widgets/dialogs.py
"""


_live_dialogs: set[QtWidgets.QMessageBox] = set()


def dialog_async_exec(dialog: QtWidgets.QMessageBox) -> asyncio.Future[Any]:
    future: asyncio.Future[Any] = asyncio.get_running_loop().create_future()

    def _on_finished(r: int) -> None:
        _live_dialogs.discard(dialog)
        future.set_result(r)

    # a dialog with no parent has nothing anchoring its C++ lifetime, so Python can garbage
    # collect it before the user ever sees/clicks it, silently hanging whoever awaits this
    # future -- keep a strong reference alive until it actually finishes. Harmless no-op for
    # dialogs that do have a parent (Qt's own parent/child ownership already keeps those alive).
    _live_dialogs.add(dialog)
    dialog.finished.connect(_on_finished)
    dialog.open()
    return future


class QAsyncMessageBox:
    @staticmethod
    def critical(
        parent: QtWidgets.QWidget | None,
        title: str,
        label: str,
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> asyncio.Future[Any]:
        dialog = QMessageBox(QMessageBox.Icon.Critical, title, label, buttons, parent)
        return dialog_async_exec(dialog)

    @staticmethod
    def information(
        parent: QtWidgets.QWidget,
        title: str,
        label: str,
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> asyncio.Future[Any]:
        dialog = QMessageBox(QMessageBox.Icon.Information, title, label, buttons, parent)
        return dialog_async_exec(dialog)

    @staticmethod
    def warning(
        parent: QtWidgets.QWidget,
        title: str,
        label: str,
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Ok,
    ) -> asyncio.Future[Any]:
        return QAsyncMessageBox._dialog(parent, title, label, buttons)

    @staticmethod
    def question(
        parent: QtWidgets.QWidget,
        title: str,
        label: str,
        buttons: QMessageBox.StandardButton = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
    ) -> asyncio.Future[Any]:
        dialog = QMessageBox(QMessageBox.Icon.Question, title, label, buttons, parent)
        return dialog_async_exec(dialog)

    @staticmethod
    def _dialog(
        parent: QtWidgets.QWidget, title: str, label: str, buttons: QMessageBox.StandardButton
    ) -> asyncio.Future[Any]:
        dialog = QMessageBox(parent)
        dialog.setWindowTitle("Error")
        dialog.setText(title)
        dialog.setInformativeText(label)
        dialog.setStandardButtons(buttons)
        return dialog_async_exec(dialog)
