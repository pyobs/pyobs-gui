"""Importing pyobs_gui after pyobs-core, which is what the `pyobs` command does for a YAML config
with `class: pyobs_gui.GUI`, must work. Each case needs a fresh interpreter, because it is about
what was imported first."""

import subprocess
import sys

import pytest


@pytest.mark.parametrize(
    "statement",
    [
        "import pyobs_gui",
        "from pyobs.application import Application; import pyobs_gui",
        "from pyobs.modules import Module; import pyobs_gui.settings",
        "import pyobs_gui.__main__",
    ],
)
def test_import_works_whatever_was_imported_first(statement: str) -> None:
    result = subprocess.run([sys.executable, "-c", statement], capture_output=True, text=True, timeout=120)
    assert result.returncode == 0, result.stderr[-1500:]
