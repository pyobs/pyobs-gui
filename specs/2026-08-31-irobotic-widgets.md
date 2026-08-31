# Plan: pyobs-gui — `RoboticWidget` / `ScheduleWidget` (`IRobotic` / `IRoboticScheduler`)

Status: proposed (issue #825)
Audited: 2026-08-31

## Problem

The robotic pipeline (`Mastermind` executes a schedule, `Scheduler` plans it) has no GUI
representation today beyond a passive `IAutonomous`-keyed warning label
(`mainwindow.py:_check_warnings`). See `pyobs-core/specs/design/irobotic.md` for the full
problem statement, interface design, and rationale (why two role-specific interfaces instead of
one). This plan only covers operationalizing that design's already-specified GUI half for
pyobs-gui — the interface shapes, module wiring, and data-flow decisions are not repeated here
except where they directly drive a widget/test decision.

## Current state (audited 2026-08-31)

- **pyobs-core side landed** on `develop` (commit `17968cb8`, PR #826): `IRobotic` /
  `IRoboticScheduler` interfaces (`pyobs/interfaces/IRobotic.py`,
  `pyobs/interfaces/IRoboticScheduler.py`), wired into `Mastermind` (executor) and `Scheduler`
  (planner). `DummyMastermind`/`DummyScheduler` (commit `30b198a6`) exist for GUI-side dev/testing
  without live hardware.
- **Not yet in a pyobs-core release.** `pyobs-gui`'s `pyproject.toml` pins
  `pyobs-core>=2.0.0,<3`; the installed PyPI `2.0.0` does not have `IRobotic`. This plan's
  implementation was developed and tested against a local editable install of pyobs-core's
  `develop` checkout (`uv pip install --python .venv/bin/python -e ../pyobs-core`, venv-only,
  not committed to `pyproject.toml`/`uv.lock`). **This PR cannot be merged into a state that
  passes CI/installs cleanly until pyobs-core ships a release containing `IRobotic`** — either
  hold the PR until that release, or bump the floor (`pyobs-core>=2.1.0` or whatever version
  ships it) as part of merging this.
- **pyobs-gui side not started** before this plan: no `RoboticWidget`/`ScheduleWidget`, no
  matching branch, no existing plan doc (confirmed via `git log --all`, `git branch -a`, and a
  file search across `specs/` and `pyobs_gui/`).
- **Widget pattern**: `pyobs_gui/base.py`'s `BaseWidget` — one-shot `_init()` (memoized,
  retry-safe), `run_background()` + `show_remote_error()` for proxy calls, `permitted()` for ACL
  gating, `_update_loop` disables the widget when the module isn't `READY`. Widgets pair a `.ui`
  file (`pyobs_gui/qt/<name>.ui`, compiled via `pyobs_gui/qt/compile.sh` →
  `pyside6-uic --from-imports`) with a Python class `class XWidget(BaseWidget, Ui_XWidget)`.
  Closest existing patterns: `autofocuswidget.py` (running indicator, action buttons, one status
  line — model for `RoboticWidget`'s button/status shape) and `eventswidget.py` (`QTableWidget`
  set up in `__init__`, columns/headers — model for `ScheduleWidget`'s table).
- **Registration points**: `mainwindow.py`'s `DEFAULT_WIDGETS` (interface → widget class,
  first-match-wins), `DEFAULT_ICONS` (interface → `qtawesome` icon name), `DEFAULT_CONFIG` (the
  same mapping again, config-file form — all three currently kept in sync by hand for every
  existing widget).
- **ACL-gating pattern**: `irobotic.md` cites `pyobs-gui/specs/plans/2026-07-29-gui-acl-aware-widget-gating.md`
  for this — wrong repo in the path (that plan is **implemented, closed** in `pyobs-core`'s
  `specs/plans/`, per this repo's own `specs/index.md:47`, not in `pyobs-gui`, which has no
  `specs/plans/` subdirectory at all — everything here lives flat under `specs/`). The mechanism
  itself (`BaseWidget.permitted()`, gating a button's `setEnabled`) is already in use by
  `autoguidingwidget.py`/`acquisitionwidget.py`; this plan follows their usage directly.
- **Test pattern**: `tests/test_camerawidget.py` — a `FakeComm` implementing only what the widget
  under test touches (`proxy`/`safe_proxy` as async context managers), `qapp` fixture for the
  headless `QApplication` (`tests/conftest.py`, `QT_QPA_PLATFORM=offscreen`), asserting on the
  mocked proxy's calls and on cached-state → GUI-state translation directly (not via Qt signal
  spies).

## Design

### 1. `RoboticWidget` (registered on `IRobotic`) — `pyobs_gui/roboticwidget.py`

Models `autofocuswidget.py`'s shape (status line + action buttons), swapping the plot for two
`QFormLayout` panels.

- `_init()`: `subscribe_state(module, IRobotic, self._on_state)` (delivers `RoboticState`
  immediately per `Comm`'s last-item pubsub semantics — this is the widget's only load path, no
  separate pull), `register_event` for `TaskStartedEvent`/`TaskFinishedEvent`/`TaskFailedEvent`
  (per the design doc, instant transition feedback layered on top of the state push — but
  `RoboticState` alone is sufficient to render the widget correctly even if an event is missed,
  so event handlers only trigger a `signal_update_gui` re-render from the already-cached state,
  never hold their own copy of task data), `subscribe_state(module, IRunning, ...)` for the
  Start/Stop running indicator (same as every other `IStartStop`-based widget — `IRobotic` does
  not duplicate `running` per the design doc), `_fetch_permitted_methods()`.
- Layout: running indicator + Start/Stop buttons (top, colorized green/red per
  `autofocuswidget`/`autoguidingwidget` convention) → "Current task" `QGroupBox` (name, id,
  target, started, ETA/countdown computed client-side from `end`, obsnum) → "Next up"
  `QGroupBox` (name, target, start, `cant_run_reason`). Empty `current`/`next` render as a
  placeholder ("—" / "Idle") rather than hidden rows, so the panel layout doesn't jump around as
  state changes.
- ETA/countdown: `RoboticTask.end` is a `Time`; render both the absolute time and a live
  `until end - now` countdown, recomputed each `_update_loop` tick (the widget already polls at
  1s via `update_func` — no separate timer).
- Buttons: `Start`/`Stop` → `proxy(module, IRobotic).start()/.stop()` via `run_background`,
  gated by `permitted("start")`/`permitted("stop")` — identical wiring to every other
  `IStartStop`-rooted widget.

### 2. `ScheduleWidget` (registered on `IRoboticScheduler`) — `pyobs_gui/schedulewidget.py`

Models `eventswidget.py`'s table setup + `autofocuswidget.py`'s button/status shape.

- `_init()`: `subscribe_state(module, IRoboticScheduler, self._on_state)` for
  `last_reschedule`/running-adjacent display, `subscribe_state(module, IRunning, ...)` for
  Start/Stop, one `proxy(module, IRoboticScheduler).get_schedule(limit=...)` call to populate the
  table initially (state push alone doesn't carry the schedule — only `get_schedule()` does, per
  the interface design), `_fetch_permitted_methods()`.
- Table (`QTableWidget`, columns: start, end, task, target, state, priority) refreshed by
  re-calling `get_schedule()` — on "Re-schedule now" success (schedule likely changed) and on a
  slow poll (`update_func`, e.g. every 30s, cheaper than every 1s since a portal-backed
  `get_schedule()` can be a live HTTP call per the design doc's note on `LcoObservationArchive`
  cost) — not from `SchedulerState`, which only carries `last_reschedule`/`time`.
- "Re-schedule now" button → `proxy(module, IRoboticScheduler).run()` (the existing
  `IRunnable.run()`, not a new method, per the interface design) via `run_background`, gated by
  `permitted("run")`; disabled while a reschedule is in flight (`run_background`'s `disable=`
  kwarg, same pattern as every other action button in this codebase).
- Start/Stop buttons, same wiring as `RoboticWidget`.

### 3. Registration

- `mainwindow.py`: add `IRobotic: RoboticWidget` and `IRoboticScheduler: ScheduleWidget` to
  `DEFAULT_WIDGETS`, `DEFAULT_ICONS` (e.g. `mdi.robot` / `mdi.calendar-clock`), and
  `DEFAULT_CONFIG` (mirroring every existing entry's three-way duplication).
- No interaction with #150 (main-vs-sidebar tab pages) or #154 (`IStructuredConfig` widget) —
  independent interfaces, first-match-wins in `DEFAULT_WIDGETS` is unaffected either way. Written
  as plain `BaseWidget` subclasses so they work as a main page today and slot into #150's
  main/sidebar split later without rework, same forward-compatibility note as #154's plan.

### 4. Tests (`tests/`)

Following `test_camerawidget.py`'s `FakeComm` pattern:

- `test_roboticwidget.py`: `_on_state` → GUI fields render correctly for populated/empty
  `current`/`next`; countdown recomputes across ticks; Start/Stop call the right proxy method and
  are gated by `permitted()`; running-indicator reflects `IRunning` state.
- `test_schedulewidget.py`: `_on_state` updates `last_reschedule` display; initial
  `get_schedule()` populates the table with the right columns/values; "Re-schedule now" calls
  `run()` and is disabled while in flight; `permitted()` gating.
- `tests/test_mainwindow_startup.py`-pattern fake-comm smoke test: a module implementing
  `IRobotic`/`IRoboticScheduler` gets the right widget class assigned via `DEFAULT_WIDGETS`.

## Acceptance criteria

- Any `IRobotic` module gets a `RoboticWidget` tab showing live running state, current task, and
  next-up/`cant_run_reason` — no per-module code.
- Any `IRoboticScheduler` module gets a `ScheduleWidget` tab showing the live schedule table and
  a working "Re-schedule now" action.
- Both widgets follow the existing ACL-gating, error-surfacing, and not-`READY`-disabling
  conventions with no special-casing.
- Existing widgets/pages unaffected.

## Out of scope

- Abort/pause the currently running task (no server-side path — see `irobotic.md`'s "Out of
  scope").
- Manual scheduling / task editing from the GUI (pyobs-portal territory).
- Migrating `mainwindow._check_warnings`'s `IAutonomous`-keyed warning label to the new state.
- Fixing `irobotic.md`'s wrong-repo citation of the ACL-gating plan — noted here, fixed directly
  in `pyobs-core` instead (one-line doc change, unrelated to this branch's diff).
