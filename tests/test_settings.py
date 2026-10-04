import os
import stat
from pathlib import Path
from typing import Any

import pytest
import yaml
from pydantic import ValidationError

from pyobs_gui.gui import GUI
from pyobs_gui.settings import (
    GuiSettings,
    NotificationSettings,
    SettingsError,
    SettingsStore,
    VfsSettings,
    unknown_keys,
)

ROOTS = {"webcam": {"class": "pyobs.vfs.HttpFile", "download": "http://localhost:37077/", "token": "secret"}}


def _store(tmp_path: Path) -> SettingsStore:
    return SettingsStore(tmp_path / "config" / "settings.yaml")


# ── schema ────────────────────────────────────────────────────────────────


def test_defaults() -> None:
    s = GuiSettings()
    assert s.notifications.enabled is True
    assert s.notifications.min_log_level == "ERROR"
    assert s.notifications.muted_modules == []
    assert s.vfs.roots == {}


def test_notification_validation() -> None:
    with pytest.raises(ValidationError):
        NotificationSettings(min_log_level="WARNING")  # type: ignore[arg-type]
    with pytest.raises(ValidationError):
        NotificationSettings(rate_limit=-1)  # pyrefly: ignore [bad-argument-type]


@pytest.mark.parametrize("roots", [{"": {"class": "x"}}, {"a/b": {"class": "x"}}, {"a": {}}, {"a": {"class": ""}}])
def test_vfs_root_validation(roots: dict) -> None:  # type: ignore[type-arg]
    with pytest.raises(ValidationError):
        VfsSettings(roots=roots)


def test_unknown_keys_walks_models_but_not_free_form_roots() -> None:
    raw = {
        "notifications": {"enabled": True, "typo": 1},
        "vfs": {"roots": {"anything": {"whatever": 1}}},
        "other": 2,
    }
    assert sorted(unknown_keys(GuiSettings, raw)) == ["notifications.typo", "other"]


# ── store ─────────────────────────────────────────────────────────────────


def test_missing_file_gives_defaults(tmp_path: Path) -> None:
    assert _store(tmp_path).get("acc") == GuiSettings()


def test_round_trip(tmp_path: Path) -> None:
    store = _store(tmp_path)
    settings = GuiSettings(
        notifications=NotificationSettings(enabled=False, muted_modules=["weather"], rate_limit=2.5),
        vfs=VfsSettings(roots=ROOTS),
    )
    store.set("acc", settings)
    assert _store(tmp_path).get("acc") == settings


def test_accounts_are_isolated(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.set("a", GuiSettings(vfs=VfsSettings(roots=ROOTS)))
    store.set("b", GuiSettings(notifications=NotificationSettings(enabled=False)))
    assert store.get("a").vfs.roots == ROOTS
    assert store.get("a").notifications.enabled is True
    assert store.get("b").vfs.roots == {}
    assert store.get("b").notifications.enabled is False
    assert store.get("c") == GuiSettings()


def test_removing_a_root_removes_it(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.set("acc", GuiSettings(vfs=VfsSettings(roots=ROOTS)))
    store.set("acc", GuiSettings(vfs=VfsSettings(roots={})))
    assert store.get("acc").vfs.roots == {}


def test_unknown_keys_survive_saving(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.path.parent.mkdir(parents=True)
    store.path.write_text(
        yaml.safe_dump(
            {
                "future": {"x": 1},
                "accounts": {
                    "acc": {"new_section": {"y": 2}, "notifications": {"enabled": False, "new_key": 3}},
                    "other": {"vfs": {"roots": ROOTS}},
                },
            }
        )
    )
    settings = store.get("acc")
    assert settings.notifications.enabled is False

    settings.notifications.rate_limit = 1.0
    store.set("acc", settings)

    data = yaml.safe_load(store.path.read_text())
    assert data["future"] == {"x": 1}
    assert data["accounts"]["acc"]["new_section"] == {"y": 2}
    assert data["accounts"]["acc"]["notifications"]["new_key"] == 3
    assert data["accounts"]["acc"]["notifications"]["rate_limit"] == 1.0
    assert data["accounts"]["other"] == {"vfs": {"roots": ROOTS}}


@pytest.mark.skipif(os.name != "posix", reason="POSIX permissions")
def test_file_is_only_readable_by_owner(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.set("acc", GuiSettings(vfs=VfsSettings(roots=ROOTS)))
    assert stat.S_IMODE(store.path.stat().st_mode) == 0o600
    store.set("acc", GuiSettings())
    assert stat.S_IMODE(store.path.stat().st_mode) == 0o600


def test_no_temp_files_left_behind(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.set("acc", GuiSettings())
    assert [p.name for p in store.path.parent.iterdir()] == ["settings.yaml"]


@pytest.mark.parametrize(
    "content",
    ["accounts: [unclosed", "- just\n- a list\n", "accounts: 3\n", "accounts:\n  acc: 5\n"],
)
def test_corrupt_file_raises_and_is_never_overwritten(tmp_path: Path, content: str) -> None:
    store = _store(tmp_path)
    store.path.parent.mkdir(parents=True)
    store.path.write_text(content)
    with pytest.raises(SettingsError):
        store.get("acc")
    with pytest.raises(SettingsError):
        store.set("acc", GuiSettings())
    assert store.path.read_text() == content


def test_invalid_values_raise_settings_error(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.path.parent.mkdir(parents=True)
    store.path.write_text(yaml.safe_dump({"accounts": {"acc": {"notifications": {"min_log_level": "NOPE"}}}}))
    with pytest.raises(SettingsError, match="acc"):
        store.get("acc")


def test_empty_file_is_fine(tmp_path: Path) -> None:
    store = _store(tmp_path)
    store.path.parent.mkdir(parents=True)
    store.path.write_text("")
    assert store.get("acc") == GuiSettings()


# ── YAML mode ─────────────────────────────────────────────────────────────


def _gui(notifications: dict[str, Any] | None = None) -> GUI:
    from pyobs.comm.local import LocalComm

    return GUI(comm=LocalComm(name="gui"), notifications=notifications)


def test_gui_reads_notifications_from_config() -> None:
    gui = _gui(notifications={"enabled": False, "muted_modules": ["weather"]})
    assert gui.settings.notifications.enabled is False
    assert gui.settings.notifications.muted_modules == ["weather"]
    assert gui.settings.notifications.min_log_level == "ERROR"


def test_gui_notifications_are_off_without_a_notifications_block() -> None:
    # YAML mode, so an upgrade does not start desktop notifications in existing control rooms
    assert _gui().settings == GuiSettings(notifications=NotificationSettings(enabled=False))


def test_gui_notifications_are_on_with_a_notifications_block() -> None:
    assert _gui(notifications={}).settings == GuiSettings()
    assert _gui(notifications={"rate_limit": 3}).settings.notifications.enabled is True


def test_gui_rejects_typos_in_notifications() -> None:
    with pytest.raises(ValueError, match="notifications.muted_module"):
        _gui(notifications={"muted_module": ["weather"]})


def test_gui_rejects_invalid_notification_values() -> None:
    with pytest.raises(ValidationError):
        _gui(notifications={"min_log_level": "INFO"})
