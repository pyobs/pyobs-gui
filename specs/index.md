# Design/planning docs

pyobs-gui keeps its own implementation plans in this directory (`YYYY-MM-DD-<slug>.md`), following
the same conventions as `pyobs-core`'s `specs/` tree. Older design docs, implementation plans, and
ADRs that concern `pyobs-gui` live in `pyobs-core`'s `specs/` tree instead (`specs/design/`,
`specs/plans/`, `specs/adrs/`), each tagged with a `Repos:` line naming every repo it concerns. See
`pyobs-core/CLAUDE.md`'s "Cross-repo docs" section.

## Local plans

- `2026-08-20-gui-remote-call-error-handling.md` — proposed. Catch exceptions on remote method
  calls and show them in a messagebox (issue #134): route every user-triggered remote call through
  `run_background`, log throttled background failures.

## Relevant from pyobs-core

- `pyobs-core/specs/design/gui-standalone-binary.md` — big picture: shipping `pyobs-gui` as a
  single compiled binary that works across sites with no rebuild. Start here.
- `pyobs-core/specs/plans/gui-interactive-login.md` — interactive login/settings dialog to replace
  the current YAML-config-file requirement (pyobs-core side).
- `pyobs-core/specs/plans/gui-login-window.md` — the actual login window UI (pyobs-gui side,
  depends on the above).
- `pyobs-core/specs/plans/gui-widget-plugins-and-packaging.md` — external plugin directory for
  custom widgets, plus the `pyside6-deploy` packaging pipeline itself.
- `pyobs-core/specs/plans/pyobs_2_0_work_plan.md` — the `IRunning.is_running()` removal item
  required updating `mainwindow.py`'s two RPC calls to that method to read `IRunning`'s pushed
  state instead.
- `pyobs-core/specs/plans/gui-navbar-shortcuts.md` — implemented, closed. Control-group-style
  keyboard shortcuts for the module sidebar.
- `pyobs-core/specs/plans/gui-acl-aware-widget-gating.md` — implemented, closed. Greying out /
  hiding actions an operator isn't permitted to use, per pyobs-core 2.0 ACLs.
- `pyobs-core/specs/plans/gui-telescopewidget-layout.md` — proposed/exploratory.
  `TelescopeWidget`'s minimum-width investigation and candidate fixes.
- `pyobs-core/specs/adrs/0010-pyobs-gui-stays-on-qtwidgets-not-qml.md` — accepted. Whether
  `pyobs-gui` should move to Qt Quick/QML; decided to stay on QtWidgets.
- `pyobs-core/specs/plans/gui-iacquisition-widget.md` — implemented, closed. The `IAcquisition`
  widget.
- `pyobs-core/specs/plans/gui-iautofocus-widget.md` — proposed, not implemented yet. The
  `IAutoFocus` widget.
- `pyobs-core/specs/plans/gui-iautoguiding-widget.md` — in progress. The `IAutoGuiding` widget;
  first pass shipped, follow-up refinement (physical-unit offsets) in progress.
