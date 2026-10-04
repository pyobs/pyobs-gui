# Settings: one schema, YAML in YAML mode, settings dialog in standalone mode

Status: proposed (issues #168 notifications, #186 VFS roots, #185 unresolved-root error).
Repos: pyobs-gui, pyobs-core (one small addition, see "VFS roots, live").
Plan: `specs/plans/2026-10-04-settings-dialog.md`.

## Problem

- #168 needs user-configurable notification settings.
- #186: in standalone mode the user cannot configure VFS roots at all, so camera images and live
  view don't work (default VFS has only `pyobs` and `robotic`, both local).
- Today the only persisted standalone data is the account list (`QSettings`, `accounts.py`) and
  per-camera live-view values (`QSettings`, `videowidget.py`). There is no settings UI.

## Requirements

- Every setting is available in both places: a YAML config and a settings dialog.
- The dialog exists in standalone (login window) mode only. YAML mode is configured through YAML
  only, there is no dialog and no menu entry.
- Settings are per account in standalone mode (accounts are identified by `Account.id`).
- Changing settings takes effect live, without logging out. Needed for VFS roots; see below.
- Secrets (VFS tokens and passwords) may be stored in clear text in the YAML file. The XMPP login
  password keeps using `keyring`, unchanged.

## Design

### One schema

`pyobs_gui/settings.py` defines pydantic models, the single source of truth:

```python
class NotificationSettings(BaseModel):
    enabled: bool = True
    min_log_level: Literal["ERROR", "CRITICAL"] = "ERROR"
    only_when_inactive: bool = True
    muted_modules: list[str] = []
    rate_limit: float = 10.0          # seconds, coalesce repeats per module

class VfsSettings(BaseModel):
    roots: dict[str, dict[str, Any]] = {}   # same shape as pyobs-core's `vfs: roots:`

class GuiSettings(BaseModel):
    notifications: NotificationSettings = NotificationSettings()
    vfs: VfsSettings = VfsSettings()
```

`vfs.roots` deliberately has the same shape as the `roots` argument of
`pyobs.vfs.VirtualFileSystem`, so a block can be copied between a module config and the GUI config.

### YAML mode

`GUI.__init__` gets `notifications: dict | None` (and uses the existing core `vfs:` handling).
Validated into `GuiSettings`. No dialog, no persistence. The settings are read-only for the
session.

```yaml
class: pyobs_gui.GUI
notifications:
  enabled: true
  min_log_level: ERROR
  muted_modules: [weather]
```

### Standalone mode

- Settings live in a YAML file in the user config dir, `QStandardPaths.AppConfigLocation` +
  `settings.yaml` (no new dependency). Layout:

  ```yaml
  accounts:
    <account-id>:
      notifications: {...}
      vfs:
        roots:
          webcam: {class: pyobs.vfs.HttpFile, download: https://..., upload: https://..., token: ...}
  ```

- Why a YAML file and not `QSettings`: the requirement is that every setting also exists as YAML,
  and VFS roots are nested free-form dicts that map badly onto `QSettings` keys. The file doubles
  as the export/import format. The account list stays in `QSettings` for now (no reason to move
  it, out of scope).
- File is written atomically (temp file + rename) and created with mode `0600` on POSIX, since it
  can contain tokens.
- Unknown keys are kept on round trip, not dropped, so a file edited by hand or by a newer
  version survives a save.
- A `SettingsStore` object (Qt-free) loads/saves the file and exposes `get(account_id)` and
  `set(account_id, GuiSettings)`. A `settings_changed` Qt signal on the GUI side fires after a
  save.

### Dialog

- Reached from a "Settings" button next to `buttonQuit` ("Log out"). Created only when
  `on_logout is not None` (standalone), same condition as the Log out text.
- One `QDialog`, two tabs: Notifications, VFS. OK/Apply/Cancel; Apply saves and applies live.
- Notifications tab: the five fields above. `muted_modules` is an editable list with a completer
  filled from the modules currently connected (the dialog is only available after connecting).
- VFS tab: table of roots (name, class, parameters). Class is a combo of the known VFS classes
  (`HttpFile`, `LocalFile`, `SMBFile`, ... whatever `pyobs.vfs` ships), parameters are a
  key/value table with a raw YAML edit toggle, since the parameter set depends on the class. No
  auto-detection of roots.
- Test: one test walks `GuiSettings.model_fields` recursively and fails if a field has no
  dialog widget, so "every setting is in the dialog" can't silently regress.

### VFS roots, live

All widgets share the one `VirtualFileSystem` instance the GUI module owns, and
`DataDisplayWidget` resolves paths per event, so mutating that instance's roots reaches it
immediately. `VirtualFileSystem._roots` is private, so this needs a small public method in
pyobs-core, `VirtualFileSystem.set_roots(roots)`, that replaces the user roots while keeping the
two default roots unless overridden. Falls back to setting `_roots` from the GUI (with a comment)
if the core release is not yet the floor.

`VideoWidget` resolves its stream URLs once in `open()`. It needs to re-resolve on
`settings_changed` (and when a resolve failed before). That is the only widget known to cache
VFS results; the rest of the GUI is to be audited in the plan.

Unresolved roots (#185) must produce a clear message naming the root and module, pointing to
Settings in standalone mode. Ships first, independent of the dialog.

### Notifications

This doc only covers where the settings come from and how they are edited. How notifications are
shown (`QSystemTrayIcon`, availability on GNOME/Wayland, `notify-send` fallback, rate limiting
behavior) is decided in #168's own design pass and consumes `NotificationSettings`.

## Alternatives considered

- **QSettings for everything** (as accounts do): simple and consistent with today, but fails the
  "also a YAML config" requirement without a second translation layer.
- **Dialog in YAML mode too** (read-only or with a `lock`): dropped, the requirement says
  standalone only.
- **Keyring for VFS secrets:** unnecessary, clear text in a `0600` YAML file is acceptable.
- **Roots published by the fleet:** rejected, needs a core change and would send credentials over
  XMPP.

## Risks and open items

- `set_roots()` needs a pyobs-core release before the GUI can rely on it. Check that the GUI's
  `pyobs-core` floor is bumped in the same release.
- A bad root (wrong class name, missing parameter) only fails when a file is opened. The VFS tab
  should validate the class path on Apply and show the error there, not only later at use.
- Clear-text tokens: `0600` is POSIX only. On Windows the file is in the user profile but not
  restricted further. Acceptable per the requirement, but say so in the dialog text.
- VFS audit (plan step 1, 2026-10-04): only two places in `pyobs_gui/` actually use the VFS.
  `VideoWidget._resolve_url` (`vfs.open_file`, caches stream URLs from `open()`) and
  `DataDisplayWidget._on_new_data` (`vfs.read_fits`, per event, no caching; also hit by
  `NewSpectrumEvent`, so spectrographs are affected too). All other widgets only pass `vfs` through
  `BaseWidget.open()` and keep the reference. `MainWindow` and `GUI.open` pass the one shared
  instance, so in-place root updates reach everything. External widget plugins that use
  `self.vfs` are not covered by this audit.
- `DataDisplayWidget._on_new_data` has no error handling around `read_fits`; a missing root
  raises out of the event handler. `grab_data()` calls it directly, so the error also surfaces
  there. #185 needs to cover both call paths.
- Changing the roots while a live-view stream is running: reconnect or keep the old stream until
  the next start. Proposed: keep it, re-resolve on next connect.
