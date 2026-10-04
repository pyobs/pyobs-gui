import sys
from pathlib import Path
from typing import Any

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
    assert ensure_shortcut("pyobs-gui", path, ("x", ""), create) is False
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
