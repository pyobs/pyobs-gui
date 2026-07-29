"""
TODO: write doc
"""

__title__ = "GUI"

from ._nuitka_astropy_patch import patch_generic_unit_parser

patch_generic_unit_parser()

from .gui import GUI
from .camerawidget import CameraWidget
from .datadisplaywidget import DataDisplayWidget
from .coolingwidget import CoolingWidget
from .shellwidget import ShellWidget
from .videowidget import VideoWidget
from .focuswidget import FocusWidget
from .telescopewidget import TelescopeWidget
from .weatherwidget import WeatherWidget
from .modulegui import ModuleGUI
