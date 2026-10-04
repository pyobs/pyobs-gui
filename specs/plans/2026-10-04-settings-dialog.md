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

- [ ] `pyobs_gui/settings.py`: `NotificationSettings`, `VfsSettings`, `GuiSettings` (pydantic).
- [ ] `SettingsStore` (Qt-free): load/save `settings.yaml` in `QStandardPaths.AppConfigLocation`,
      per account id, atomic write, mode `0600` on POSIX, unknown keys preserved.
- [ ] Tests: round trip, unknown keys kept, missing file gives defaults, corrupt file gives a
      clear error and does not overwrite it, per-account isolation.
- [ ] YAML mode: `GUI.__init__(notifications=...)`, validated into `GuiSettings`. Test with a
      `test/*.yaml` config.

## 4. Live VFS roots

- [ ] pyobs-core: `VirtualFileSystem.set_roots(roots)` (keeps default roots unless overridden),
      test, release. Bump the floor in pyobs-gui.
- [ ] GUI: apply `vfs.roots` from `GuiSettings` at startup (standalone: from the store; YAML
      mode: unchanged, uses the core `vfs:` config).
- [ ] `settings_changed` signal; `VideoWidget` re-resolves stream URLs on it and after a failed
      resolve. Running streams are left alone until the next connect.
- [ ] Tests: add a root at runtime, a previously failing path now resolves.

## 5. Dialog

- [ ] `SettingsDialog` (`QDialog`), tabs Notifications and VFS, OK/Apply/Cancel.
- [ ] "Settings" button next to `buttonQuit` in `MainWindow`, created only when
      `on_logout is not None`. Update the `.ui` file and regenerate (`qt/compile.sh`).
- [ ] VFS tab: roots table, class combo from `pyobs.vfs`, key/value parameters with a YAML edit
      toggle, class-path validation on Apply.
- [ ] Notifications tab: five fields, `muted_modules` list with completer from connected modules.
- [ ] Test that walks `GuiSettings.model_fields` and fails on any field without a dialog widget.
- [ ] Test that the button does not exist in YAML mode.

## 6. Hand-off to #168

- [ ] `NotificationSettings` is consumed by the notification implementation. Delivery mechanism,
      tray availability and rate-limit behavior are decided in #168's own design pass.

## 7. Wrap-up

- [ ] Docs: user-facing description of `settings.yaml` and the `notifications:` YAML block.
- [ ] `pyrefly`, `ruff`, `black`, full `pytest`.
- [ ] Update `specs/index.md` and `specs/plans/index.md` status lines.
