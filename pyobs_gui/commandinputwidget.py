from typing import List, Any

from PyQt5 import QtCore, QtWidgets, QtGui


class CommandInputWidget(QtWidgets.QLineEdit):  # type: ignore
    commandExecuted = QtCore.pyqtSignal(str)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        QtWidgets.QLineEdit.__init__(self, *args, **kwargs)
        self._history: List[str] = []
        self._history_index = 0

    def keyPressEvent(self, event: QtGui.QKeyEvent) -> None:
        if event.key() == QtCore.Qt.Key_Return:
            # get command
            cmd = str(self.text())
            # emit command
            self.commandExecuted.emit(cmd)
            # clear text field
            self.clear()
            # remember if new command and reset index
            if not (self._history and self._history[-1] == cmd):
                self._history.append(cmd)
            self._history_index = 0

        elif event.key() == QtCore.Qt.Key_Up:
            # history empty?
            if len(self._history) > 0:
                # get new history index
                self._history_index = max(self._history_index - 1, -len(self._history))
                # show text
                self.setText(self._history[self._history_index])

        elif event.key() == QtCore.Qt.Key_Down:
            # get new history index
            self._history_index = min(self._history_index + 1, 0)
            # show text or clear it, if we're back to current entry
            if self._history_index == 0:
                self.clear()
            else:
                self.setText(self._history[self._history_index])

        else:
            # default action
            QtWidgets.QLineEdit.keyPressEvent(self, event)
