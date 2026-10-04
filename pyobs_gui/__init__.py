"""
TODO: write doc
"""

__title__ = "GUI"

# pydantic loads its submodules lazily. If that first happens after PySide6 was imported, PySide6's
# import hook (shibokensupport.feature) trips over it: "cannot import name 'import_string' ...
# circular import". The `pyobs` command imports pydantic through pyobs-core before it imports this
# package, but only partly, so what this package uses from pydantic is loaded here, before anything
# imports PySide6 (see tests/test_import_order.py).
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator  # noqa: E402, F401

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
