import os
import sys

import pytest

# Run headless by default (no DISPLAY needed) -- only if the environment hasn't already picked a
# platform, so a real display (e.g. local dev) is still used when available.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6 import QtWidgets  # noqa: E402  (must follow the QT_QPA_PLATFORM default above)


@pytest.fixture(scope="session", autouse=True)
def qapp() -> QtWidgets.QApplication:
    """A QApplication is required to construct any QWidget -- session-scoped since only one may
    exist per process."""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication(sys.argv)
    return app  # type: ignore[return-value]
