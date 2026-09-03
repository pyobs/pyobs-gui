"""
TODO: write doc
"""

__title__ = "GUI"

from ._nuitka_astropy_patch import patch_generic_unit_parser

# Only relevant in the Nuitka-compiled standalone binary: under a regular interpreter the
# patch must not install, or it breaks astropy's unit/coordinate parsing (issue #151). The
# marker is evaluated here because pyobs_gui/__init__.py is guaranteed compiled in the binary.
patch_generic_unit_parser(compiled="__compiled__" in globals())

from .gui import GUI
from .camerawidget import CameraWidget
from .datadisplaywidget import DataDisplayWidget
from .coolingwidget import CoolingWidget
from .shellwidget import ShellWidget
from .videowidget import VideoWidget
from .videograbwidget import VideoGrabWidget
from .focuswidget import FocusWidget
from .telescopewidget import TelescopeWidget
from .weatherwidget import WeatherWidget
from .modulegui import ModuleGUI
