"""Shared app artwork as real files for Qt, notifications and Windows shortcuts."""

from pathlib import Path
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from PySide6.QtGui import QIcon


def icon_path(format: Literal["png", "ico"] = "png") -> Path:
    """Installed package data, also placed beside this module by Nuitka."""
    return Path(__file__).resolve().with_name("icons") / f"pyobs-gui.{format}"


def window_icon() -> "QIcon":
    """Qt reads all resolutions in the ICO, including the small window-title icon."""
    from PySide6.QtGui import QIcon

    return QIcon(str(icon_path("ico")))
