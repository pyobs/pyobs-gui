# Plan: settings schema, YAML config and standalone settings dialog

Status: proposed. Design: `specs/2026-10-04-settings-dialog.md`.
Repos: pyobs-gui, pyobs-core (step 4 only).
Issues: #185 (unresolved-root error), #186 (VFS roots), #168 (notifications, consumes the
settings).

## 1. Audit (before any code)

- [x] `grep` every use of `self.vfs` / `read_fits` / `open_file` in `pyobs_gui/` and list which
      widgets cache VFS-derived state (known: `VideoWidget` stream URLs). Add findings to the
      design doc's "Risks". Done: only `VideoWidget` and `DataDisplayWidget` use the VFS, only
      `VideoWidget` caches.

## 2. #185: clear error for unresolved roots (ships first, independent)

- [x] Helper that turns the `ValueError: Could not find root ...` from `VirtualFileSystem` into a
      user-facing message with root name and module (`missing_root_message()` in `base.py`).
      The pointer to Settings in standalone mode is added in step 5, once the dialog exists.
- [x] Use it in `DataDisplayWidget` (around `vfs.read_fits`, box once per root) and
      `VideoWidget` (`_resolve_url` records it, `_init` shows it if no stream resolved).
- [x] Tests (`tests/test_missing_vfs_root.py`): message content, once-per-root, other
      `ValueError`s still propagate, video init shows the box and stays disabled.
- [ ] Follow-up in core: a dedicated exception for an unknown root, so the message-prefix match in
      `missing_root_message()` can go.

## 3. Settings schema and store

- [x] `pyobs_gui/settings.py`: `NotificationSettings`, `VfsSettings`, `GuiSettings` (pydantic).
- [x] `SettingsStore` (Qt-free): load/save `settings.yaml` in `QStandardPaths.GenericConfigLocation`/pyobs/pyobs-gui,
      per account id, atomic write, mode `0600` on POSIX, unknown keys preserved.
- [x] Tests: round trip, unknown keys kept, missing file gives defaults, corrupt file gives a
      clear error and does not overwrite it, per-account isolation.
- [x] YAML mode: `GUI.__init__(notifications=...)`, validated into `GuiSettings`. Test with a
      `test/*.yaml` config.

## 4. Live VFS roots

- [ ] pyobs-core: `VirtualFileSystem.set_roots(roots)` (keeps default roots unless overridden).
      Merged (pyobs-core#939), **not released yet**. Then bump the `pyobs-core` floor in
      pyobs-gui and drop the two `pyrefly: ignore [missing-attribute]` (marked TODO in `gui.py`
      and `tests/test_settingsdialog.py`).
- [x] GUI: apply `vfs.roots` from `GuiSettings` at startup (`GUI._apply_vfs_roots()` in `open()`,
      standalone only; YAML mode keeps the core `vfs:` config) and on change
      (`GUI.apply_settings()`: save, `set_roots()`, emit `settings_changed`).
- [x] `settings_changed` signal (`guisignals.py`, app-wide, emitted by whoever applies settings);
      `VideoWidget` re-resolves stream URLs on it and completes a failed init. Running streams are
      left alone until the next connect, and old URLs are kept if nothing resolves any more.
- [x] Tests (`tests/test_video_refresh.py`): a previously failing init is completed by a new root,
      new URL used at next connect without reconnecting, old URLs kept, ignored before init,
      no reaction after discard. They add the root to `vfs._roots` directly, to be switched to
      `set_roots()` once released.

## 5. Dialog

- [x] Settings key per connection: `ConnectionRequest.account_id`, `login.settings_key()` (saved
      account id, or `jid:<bare jid>` for an unsaved connection), returned by
      `show_login_and_connect()` and re-read on log out/in.
- [x] `SettingsDialog` (`QDialog`, `settingsdialog.py`), tabs Notifications and VFS,
      OK/Apply/Cancel. Problems are shown in the dialog, which stays open.
- [x] "Settings" button above `buttonQuit`, created in code only when `on_settings` is given
      (standalone), so no `.ui` change.
- [x] VFS tab: root list, name, class box (known `pyobs.vfs` classes, any path can be typed) and
      parameters as YAML text. Class path, YAML and names are validated on Apply. Deviation from
      the design: no key/value table, YAML text only.
- [x] Notifications tab: five fields, `muted_modules` list with completer from connected modules.
- [x] Test that walks `GuiSettings.model_fields` and fails on any field without a dialog widget.
- [x] Tests that the button and the store only exist in standalone mode.
- [x] Fixed in `default_settings_path()`: `AppConfigLocation` has no app subdirectory here and
      would have put the file into `~/.config`.

## 6. Hand-off to #168

- [ ] `NotificationSettings` is consumed by the notification implementation. Delivery mechanism,
      tray availability and rate-limit behavior are decided in #168's own design pass.

## 7. Wrap-up

- [ ] Docs: user-facing description of `settings.yaml` and the `notifications:` YAML block.
- [ ] `pyrefly`, `ruff`, `black`, full `pytest`.
- [ ] Update `specs/index.md` and `specs/plans/index.md` status lines.
