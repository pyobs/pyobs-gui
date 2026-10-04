"""GUI settings: one schema, used by the YAML-configured GUI and the standalone settings file.

See specs/2026-10-04-settings-dialog.md. In YAML mode the settings come from the GUI module's
config (read-only for the session); in standalone mode `SettingsStore` keeps them per account in
a YAML file in the user config dir, and the settings dialog edits that file.
"""

from __future__ import annotations

import contextlib
import logging
import os
import tempfile
from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

log = logging.getLogger(__name__)

SETTINGS_FILENAME = "settings.yaml"


class SettingsError(Exception):
    """Settings could not be read, validated or written."""


class NotificationSettings(BaseModel):
    """Desktop notifications for module ERROR state and log ERROR/CRITICAL events (#168)."""

    # unknown keys are ignored by the model; SettingsStore keeps them in the file, and
    # unknown_keys() lets the YAML-mode caller reject typos
    model_config = ConfigDict(extra="ignore")

    enabled: bool = True
    min_log_level: Literal["ERROR", "CRITICAL"] = "ERROR"
    only_when_inactive: bool = True
    muted_modules: list[str] = Field(default_factory=list)
    # seconds, repeats from the same module within this time are coalesced
    rate_limit: float = Field(default=10.0, ge=0)


class VfsSettings(BaseModel):
    """VFS roots, same shape as the `roots` argument of `pyobs.vfs.VirtualFileSystem`."""

    model_config = ConfigDict(extra="ignore")

    roots: dict[str, dict[str, Any]] = Field(default_factory=dict)

    @field_validator("roots")
    @classmethod
    def _check_roots(cls, roots: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
        for name, config in roots.items():
            if not name or "/" in name:
                raise ValueError(f"Invalid VFS root name {name!r}: must be non-empty and contain no '/'.")
            if not isinstance(config.get("class"), str) or not config["class"]:
                raise ValueError(f"VFS root {name!r} needs a 'class'.")
        return roots


class GuiSettings(BaseModel):
    model_config = ConfigDict(extra="ignore")

    notifications: NotificationSettings = Field(default_factory=NotificationSettings)
    vfs: VfsSettings = Field(default_factory=VfsSettings)


def unknown_keys(model_class: type[BaseModel], raw: dict[str, Any], prefix: str = "") -> list[str]:
    """Dotted paths of keys in `raw` that `model_class` doesn't know about.

    Only walks into nested models, so the free-form contents of `vfs.roots` are never reported.
    """
    unknown: list[str] = []
    for key, value in raw.items():
        field = model_class.model_fields.get(key)
        if field is None:
            unknown.append(f"{prefix}{key}")
            continue
        sub = _model_class(field.annotation)
        if sub is not None and isinstance(value, dict):
            unknown.extend(unknown_keys(sub, value, f"{prefix}{key}."))
    return unknown


def _model_class(annotation: Any) -> type[BaseModel] | None:
    if isinstance(annotation, type) and issubclass(annotation, BaseModel):
        return annotation
    return None


def _merge(model_class: type[BaseModel], raw: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """`new` over `raw`, recursing into nested models so unknown keys in `raw` survive. Everything
    else (including all of `vfs.roots`) is replaced wholesale, so removing a root really removes it."""
    merged = dict(raw)
    for name, field in model_class.model_fields.items():
        if name not in new:
            continue
        sub = _model_class(field.annotation)
        if sub is not None and isinstance(merged.get(name), dict):
            merged[name] = _merge(sub, merged[name], new[name])
        else:
            merged[name] = new[name]
    return merged


def default_settings_path() -> Path:
    """`settings.yaml` in the platform's per-user app config dir."""
    from PySide6 import QtCore

    location = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.StandardLocation.AppConfigLocation)
    return Path(location) / SETTINGS_FILENAME


class SettingsStore:
    """Per-account settings in one YAML file (standalone mode).

    ```yaml
    accounts:
      <account-id>:
        notifications: {...}
        vfs:
          roots: {...}
    ```

    The file can contain VFS tokens in clear text, so it is created with mode 0600 on POSIX. It is
    never overwritten when it can't be parsed: `set()` raises `SettingsError` instead, leaving the
    file for the user to fix. Keys this version doesn't know are kept when saving.
    """

    def __init__(self, path: Path | str | None = None) -> None:
        self.path = Path(path) if path is not None else default_settings_path()

    def get(self, account_id: str) -> GuiSettings:
        """Settings for an account, defaults if the file or the account doesn't exist."""
        account = self._account(self._read(), account_id)
        extra = unknown_keys(GuiSettings, account)
        if extra:
            log.warning("Ignoring unknown settings for account %s in %s: %s", account_id, self.path, ", ".join(extra))
        try:
            return GuiSettings.model_validate(account)
        except ValidationError as e:
            raise SettingsError(f"Invalid settings for account {account_id} in {self.path}: {e}") from e

    def set(self, account_id: str, settings: GuiSettings) -> None:
        """Save an account's settings, leaving other accounts and unknown keys untouched."""
        data = self._read()
        account = self._account(data, account_id)
        data.setdefault("accounts", {})[account_id] = _merge(GuiSettings, account, settings.model_dump(mode="python"))
        self._write(data)

    def _account(self, data: dict[str, Any], account_id: str) -> dict[str, Any]:
        account = (data.get("accounts") or {}).get(account_id)
        if account is None:
            return {}
        if not isinstance(account, dict):
            raise SettingsError(f"Settings for account {account_id} in {self.path} must be a mapping.")
        return account

    def _read(self) -> dict[str, Any]:
        try:
            text = self.path.read_text(encoding="utf-8")
        except FileNotFoundError:
            return {}
        except OSError as e:
            raise SettingsError(f"Could not read {self.path}: {e}") from e
        try:
            data = yaml.safe_load(text)
        except yaml.YAMLError as e:
            raise SettingsError(f"{self.path} is not valid YAML, fix or delete it: {e}") from e
        if data is None:
            return {}
        if not isinstance(data, dict) or not isinstance(data.get("accounts") or {}, dict):
            raise SettingsError(f"{self.path} has an unexpected structure, expected a mapping with 'accounts'.")
        return data

    def _write(self, data: dict[str, Any]) -> None:
        """Atomic: write a temp file next to the target, then rename it over."""
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            fd, tmp = tempfile.mkstemp(dir=self.path.parent, prefix=f".{SETTINGS_FILENAME}.", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as f:
                    yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
                if os.name == "posix":
                    os.chmod(tmp, 0o600)
                os.replace(tmp, self.path)
            except BaseException:
                with contextlib.suppress(OSError):
                    os.unlink(tmp)
                raise
        except OSError as e:
            raise SettingsError(f"Could not write {self.path}: {e}") from e
