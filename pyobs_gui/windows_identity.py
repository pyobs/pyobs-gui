"""Windows only: the app identity that toast notifications need.

On the tested Windows 11, a toast is silently dropped, without any error, unless the app has an
AppUserModelID that is attached to a Start Menu shortcut. The registry key `desktop-notifier`
writes is not enough. See specs/2026-10-04-desktop-notifications.md ("App identity (Windows)").

`desktop-notifier` uses its `app_name` as the AppUserModelID, so the id given here has to be that
name.
"""

from __future__ import annotations

import logging
import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

log = logging.getLogger(__name__)

SHORTCUT_NAME = "pyobs-gui.lnk"


def shortcut_path() -> Path:
    appdata = os.environ.get("APPDATA")
    if not appdata:
        raise OSError("APPDATA is not set, cannot find the Start Menu.")
    return Path(appdata) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / SHORTCUT_NAME


def launch_command() -> tuple[str, str]:
    """Program and arguments that start the app the way it was started now: the `pyobs-gui`
    launcher a pip install creates, or the interpreter with `-m pyobs_gui`."""
    argv0 = Path(sys.argv[0])
    if argv0.suffix.lower() == ".exe" and argv0.exists():
        return str(argv0.resolve()), ""
    return sys.executable, "-m pyobs_gui"


def create_link_com(path: Path, target: str, arguments: str, app_id: str) -> None:
    """Write a shortcut with the AppUserModelID property, through pywin32.

    NOT TESTED YET: written from the usual pywin32 recipe on a machine without Windows, to be
    checked on one (see the Windows handover for the notification spike).
    """
    import pythoncom  # type: ignore[import-not-found]
    from win32com.propsys import propsys, pscon  # type: ignore[import-not-found]
    from win32com.shell import shell  # type: ignore[import-not-found]

    link = pythoncom.CoCreateInstance(shell.CLSID_ShellLink, None, pythoncom.CLSCTX_INPROC_SERVER, shell.IID_IShellLink)
    link.SetPath(target)
    if arguments:
        link.SetArguments(arguments)
    store = link.QueryInterface(propsys.IID_IPropertyStore)
    store.SetValue(pscon.PKEY_AppUserModel_ID, propsys.PROPVARIANTType(app_id))
    store.Commit()
    link.QueryInterface(pythoncom.IID_IPersistFile).Save(str(path), 0)


def ensure_shortcut(
    app_id: str,
    path: Path | None = None,
    command: tuple[str, str] | None = None,
    create_link: Callable[[Path, str, str, str], None] = create_link_com,
) -> bool:
    """Make sure the Start Menu shortcut with the AppUserModelID exists.

    An existing shortcut is left alone, whatever it points to.

    Returns:
        Whether a shortcut was created.

    Raises:
        OSError: The shortcut could not be created (nothing is left behind then).
    """
    path = shortcut_path() if path is None else path
    if path.exists():
        return False
    target, arguments = launch_command() if command is None else command
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        create_link(path, target, arguments, app_id)
    except Exception as e:
        path.unlink(missing_ok=True)
        raise OSError(f"Could not create the Start Menu shortcut {path}: {e}") from e
    log.info("Created %s so Windows shows notifications of %s.", path, app_id)
    return True


__all__ = ["ensure_shortcut", "launch_command", "shortcut_path"]
