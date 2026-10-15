import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock

import pytest

from pyobs_gui.windows_identity import SHORTCUT_NAME, ensure_shortcut, launch_command, shortcut_path


class Recorder:
    def __init__(self, fail: Exception | None = None, leaves_file: bool = False) -> None:
        self.calls: list[tuple[Path, str, str, str]] = []
        self.fail = fail
        self.leaves_file = leaves_file

    def __call__(self, path: Path, target: str, arguments: str, app_id: str) -> None:
        self.calls.append((path, target, arguments, app_id))
        if self.leaves_file:
            path.write_text("partial")
        if self.fail is not None:
            raise self.fail
        path.write_text("link")


def test_creates_the_shortcut_with_target_arguments_and_id(tmp_path: Path) -> None:
    path = tmp_path / "Start Menu" / "Programs" / SHORTCUT_NAME
    create = Recorder()
    assert ensure_shortcut("pyobs-gui", path, ("C:/py/python.exe", "-m pyobs_gui"), create) is True
    assert create.calls == [(path, "C:/py/python.exe", "-m pyobs_gui", "pyobs-gui")]
    assert path.exists()


def test_an_existing_shortcut_is_left_alone(tmp_path: Path) -> None:
    path = tmp_path / SHORTCUT_NAME
    path.write_text("mine")
    create = Recorder()
    update = MagicMock(return_value=True)
    assert ensure_shortcut("pyobs-gui", path, ("x", ""), create, update) is False
    update.assert_called_once_with(path)
    assert create.calls == [] and path.read_text() == "mine"


def test_a_failure_leaves_nothing_behind_and_is_an_oserror(tmp_path: Path) -> None:
    path = tmp_path / SHORTCUT_NAME
    with pytest.raises(OSError, match="Could not create"):
        ensure_shortcut("pyobs-gui", path, ("x", ""), Recorder(fail=RuntimeError("com"), leaves_file=True))
    assert not path.exists()


def test_shortcut_path_is_in_the_users_start_menu(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("APPDATA", str(tmp_path))
    assert shortcut_path() == tmp_path / "Microsoft" / "Windows" / "Start Menu" / "Programs" / SHORTCUT_NAME


def test_shortcut_path_without_appdata_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("APPDATA", raising=False)
    with pytest.raises(OSError, match="APPDATA"):
        shortcut_path()


def test_launch_command_for_the_pip_launcher(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    exe = tmp_path / "pyobs-gui.exe"
    exe.write_text("")
    monkeypatch.setattr(sys, "argv", [str(exe)])
    assert launch_command() == (str(exe.resolve()), "")


@pytest.mark.parametrize("argv0", ["__main__.py", "pyobs-gui", "missing.exe"])
def test_launch_command_otherwise_starts_the_module(monkeypatch: pytest.MonkeyPatch, argv0: Any) -> None:
    monkeypatch.setattr(sys, "argv", [argv0])
    assert launch_command() == (sys.executable, "-m pyobs_gui")


@pytest.fixture
def com_link(monkeypatch: pytest.MonkeyPatch) -> MagicMock:
    """Exercise our COM calls without requiring a Windows notification service."""
    from types import ModuleType

    link = MagicMock()
    pythoncom = MagicMock()
    pythoncom.CoCreateInstance.return_value = link
    monkeypatch.setitem(sys.modules, "pythoncom", pythoncom)
    monkeypatch.setitem(sys.modules, "win32com", ModuleType("win32com"))
    monkeypatch.setitem(sys.modules, "win32com.shell", MagicMock())
    monkeypatch.setitem(sys.modules, "win32com.propsys", MagicMock())
    return link


def test_new_com_shortcut_has_the_packaged_icon(com_link: MagicMock, tmp_path: Path) -> None:
    from pyobs_gui.appicon import icon_path
    from pyobs_gui.windows_identity import create_link_com

    create_link_com(tmp_path / SHORTCUT_NAME, "python.exe", "-m pyobs_gui", "pyobs-gui")
    com_link.SetIconLocation.assert_called_once_with(str(icon_path("ico")), 0)
    com_link.SetPath.assert_called_once_with("python.exe")
    com_link.SetArguments.assert_called_once_with("-m pyobs_gui")


def test_existing_com_shortcut_gets_icon_without_changing_target(com_link: MagicMock, tmp_path: Path) -> None:
    from pyobs_gui.appicon import icon_path
    from pyobs_gui.windows_identity import update_link_icon_com

    path = tmp_path / SHORTCUT_NAME
    com_link.GetIconLocation.return_value = ("python.exe", 0)
    assert update_link_icon_com(path) is True
    com_link.QueryInterface.return_value.Load.assert_called_once_with(str(path))
    com_link.SetIconLocation.assert_called_once_with(str(icon_path("ico")), 0)
    com_link.QueryInterface.return_value.Save.assert_called_once_with(str(path), 0)
    com_link.SetPath.assert_not_called()
    com_link.SetArguments.assert_not_called()


def test_matching_com_shortcut_is_not_rewritten(com_link: MagicMock, tmp_path: Path) -> None:
    from pyobs_gui.appicon import icon_path
    from pyobs_gui.windows_identity import update_link_icon_com

    com_link.GetIconLocation.return_value = (str(icon_path("ico")), 0)
    assert update_link_icon_com(tmp_path / SHORTCUT_NAME) is False
    com_link.SetIconLocation.assert_not_called()
    com_link.QueryInterface.return_value.Save.assert_not_called()
