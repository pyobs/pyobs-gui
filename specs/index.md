# Design/planning docs

pyobs-gui keeps its own implementation plans in this directory (`YYYY-MM-DD-<slug>.md`), following
the same conventions as `pyobs-core`'s `specs/` tree. Older design docs, implementation plans, and
ADRs that concern `pyobs-gui` live in `pyobs-core`'s `specs/` tree instead (`specs/design/`,
`specs/plans/`, `specs/adrs/`), each tagged with a `Repos:` line naming every repo it concerns. See
`pyobs-core/CLAUDE.md`'s "Cross-repo docs" section.

## Local plans

- `2026-08-31-irobotic-widgets.md` — **implemented, closed (issue #825, PR #155, `5794186`)**.
  `RoboticWidget` / `ScheduleWidget` for `IRobotic`/`IRoboticScheduler`.
- `2026-08-28-structuredconfig-widget.md` — **proposed (issue #154)**. Generic
  `StructuredConfigWidget`: schema-driven, auto-built editable form for `IStructuredConfig`
  modules (from `ConfigSchema` capabilities + `ConfigAppliedState` + `set_config`).
- `2026-08-28-gui-main-vs-sidebar-widgets.md` — **draft**. Fleshed-out issue #150: explicit
  main-widget/sidebar-widget distinction, automatic tab pages for multi-widget modules (shared
  sidebar, merge-per-interface custom config, standalone parity).
- `2026-08-21-gui-widget-startup-responsiveness.md` — **implemented, closed 2026-08-23 (PR #141,
  `123161b`)**. Make module widgets appear and respond immediately at startup: non-blocking
  `_add_client` with a "Loading…" placeholder page (clicks are never dropped), parallel
  `_init_clients`, drop per-connect O(N) work, plus telescope/camera `_init` fast-follows.
- `2026-08-20-gui-remote-call-error-handling.md` — **implemented, closed 2026-08-20 (PR #138,
  `bfc0a87`)**. Catch exceptions on remote method calls and show them in a messagebox (issue #134):
  route every user-triggered remote call through `run_background`, log throttled background
  failures.

## Relevant from pyobs-core

- `pyobs-core/specs/design/irobotic.md` — `IRobotic` (executor) / `IRoboticScheduler`
  (planner) interfaces + `RoboticWidget` / `ScheduleWidget`. **implemented, closed** (issue #825).
  pyobs-core side shipped in `v2.1.0`; pyobs-gui side is this repo's own
  `2026-08-31-irobotic-widgets.md`, above.
- `pyobs-core/specs/design/gui-standalone-binary.md` — big picture: shipping `pyobs-gui` as a
  single compiled binary that works across sites with no rebuild. *proposed* — start here.
- `pyobs-core/specs/plans/2026-07-26-gui-interactive-login.md` — interactive login/settings
  dialog to replace the current YAML-config-file requirement (pyobs-core side).
  **implemented, closed** (landed 2026-07-27)
- `pyobs-core/specs/plans/2026-07-27-gui-login-window.md` — the actual login window UI
  (pyobs-gui side, depends on the above). **implemented, closed**
- `pyobs-core/specs/plans/2026-07-27-gui-widget-plugins-and-packaging.md` — external plugin
  directory for custom widgets, plus the `pyside6-deploy` packaging pipeline itself. **draft** —
  loading mechanism decided + spiked; widget-selection mechanism still open
- `pyobs-core/specs/plans/2026-07-19-pyobs_2_0_work_plan.md` — the `IRunning.is_running()`
  removal item required updating `mainwindow.py`'s two RPC calls to that method to read
  `IRunning`'s pushed state instead. **implemented, closed**
- `pyobs-core/specs/plans/2026-07-29-gui-navbar-shortcuts.md` — **implemented, closed**.
  Control-group-style keyboard shortcuts for the module sidebar.
- `pyobs-core/specs/plans/2026-07-29-gui-acl-aware-widget-gating.md` — **implemented, closed**.
  Greying out / hiding actions an operator isn't permitted to use, per pyobs-core 2.0 ACLs.
- `pyobs-core/specs/plans/2026-07-29-gui-telescopewidget-layout.md` — proposed/exploratory.
  `TelescopeWidget`'s minimum-width investigation and candidate fixes.
- `pyobs-core/specs/adrs/0010-pyobs-gui-stays-on-qtwidgets-not-qml.md` — accepted. Whether
  `pyobs-gui` should move to Qt Quick/QML; decided to stay on QtWidgets.
- `pyobs-core/specs/plans/2026-07-29-gui-iacquisition-widget.md` — **implemented, closed**. The
  `IAcquisition` widget.
- `pyobs-core/specs/plans/2026-07-29-gui-iautofocus-widget.md` — **implemented, closed**. The
  `IAutoFocus` widget (`AutoFocusWidget` shipped in `4d6a48c`, 2026-07-05).
- `pyobs-core/specs/plans/2026-07-29-gui-iautoguiding-widget.md` — **implemented, closed**. The
  `IAutoGuiding` widget; the follow-up refinement (`OffsetResult`/`OffsetFrame`, arcsec-based
  `GuidingState`) has shipped in both pyobs-core and pyobs-gui.
- `pyobs-core/specs/plans/2026-08-21-basevideo-http-token-auth.md` — **proposed**. Shared-token
  auth + browser login for `BaseVideo` (pyobs-core side); pyobs-gui side is a one-header change
  in `VideoWidget`'s raw-socket GET (design: `pyobs-core/specs/design/basevideo-http-auth.md`).
