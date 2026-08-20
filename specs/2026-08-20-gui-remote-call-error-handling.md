# Plan: pyobs-gui — surface remote-call failures in messageboxes (issue #134)

Status: proposed
Issue: pyobs-gui#134

## Problem

Every user-triggered remote call (`async with self.comm.proxy(...) as proxy: await proxy.foo(...)`)
can fail with a `pyobs.utils.exceptions.PyobsError` — domain errors from the module (`MoveError`,
`GrabImageError`, `DeviceBusyError`, `NotSupportedError`, `InvalidArgumentError`, ...) or transport
errors (`RemoteError`, `RemoteTimeoutError`, `ForbiddenError`). Most widget call sites swallow or
ignore the exception today, so the operator gets no feedback and only finds out from the log (or not
at all). Issue #134 asks for every user-triggered remote call to surface the failure in a messagebox,
via the code path that already exists: `BaseWidget.run_background()`.

## Current state (audited 2026-08-20)

### Already handled — routed through `run_background()`

`run_background()` → `_background_task()` (`base.py:296-318`) wraps the call in
`except exc.PyobsError → show_error()`, `except Exception → log.exception + QAsyncMessageBox.warning`,
plus optional button disable/enable. Already used by:

- `filterwidget.py:69` — `set_filter` (proxy is created in the asyncSlot, then
  `run_background(proxy.set_filter, ...)` is scheduled; works because `_ProxyContext.__aexit__` is a
  no-op and the `Proxy` is cached by `Comm`, but stylistically the whole call should live inside the
  background task — tidy-up below)
- `modewidget.py:118` — `set_mode` (correct pattern: a nested `_do_set_mode()` owns the proxy)
- `telescopewidget.py` — all `_do_move_*` / `_do_track_*` launched from `move()`
- `compassmovewidget.py:32` — `__move_offset`

### Not handled — bare `@qasync.asyncSlot()` that awaits `proxy.method()` directly

An exception here only reaches the event loop's exception handler (one log line), never the user:

- `roofwidget.py:56-69` — `open_roof` (`init`), `close_roof` (`park`), `stop_roof` (`stop_motion`)
- `coolingwidget.py:50-55` — `buttonApply_clicked` (`set_cooling`)
- `autofocuswidget.py:98-106` — `_run_auto_focus`, `_abort`
- `autoguidingwidget.py:133-147` — `_start`, `_stop`, `_set_exposure_time`
- `acquisitionwidget.py:150-158` — `_acquire`, `_abort`
- `spectrographwidget.py:62-80` — `grab_spectrum` (loop of `datadisplay.grab_data`), `abort`
- `telescopewidget.py:520-533` — `_init_telescope`, `_park_telescope`, `_stop_telescope`
- `focuswidget.py:90-93` — `_reset_focus_offset`
- `camerawidget.py:228,271,351` — `set_full_frame` (read-only capabilities fetch), `expose` (has two
  ad-hoc `except Exception` → `QMessageBox.information` blocks, lines 277-282 and 291-295), `abort`
- `videowidget.py:227-287` — `grab_image`, `exposure_time_changed`, `gain_changed`
- `statuswidget.py:132-135` — `StatusItem.button_clicked` (`reset_error`); `StatusItem` is not a
  `BaseWidget`, so it has no `run_background`

### Fire-and-forget tasks — exceptions discarded at GC

- `focuswidget.py:74,84` — `asyncio.ensure_future(self._set_focus_base_async(...))` /
  `_set_focus_offset_async`
- `telescopewidget.py:542-555` — `_set_offset` launches `_do_set_offsets_altaz` /
  `_do_set_offsets_radec` via `asyncio.create_task`

### Background polling — silently swallowed

`base.py:292-294` — `_update_loop` catches `(exc.PyobsError, IndexError)` and just sleeps; every
widget's `_update_func` failure is invisible (no log, no dialog).

## Design

### 1. Single code path: route every user-triggered remote call through `run_background()`

Convert each affected `@qasync.asyncSlot()` handler into a plain (sync) method that (a) reads any
widget state it needs (spinbox/checkbox values — cheap, must stay on the Qt thread and run before
the task starts), then (b) calls `self.run_background(<async impl>, ...)`. The async impl owns the
`async with self.comm.proxy(...)` block and the single `await proxy.method(...)` — nothing else.
This is exactly the `modewidget.set_mode` pattern already in the codebase.

```python
# before
@qasync.asyncSlot()
async def open_roof(self) -> None:
    async with self.comm.proxy(self.module, IMotion) as proxy:
        await proxy.init()

# after
def open_roof(self) -> None:
    self.run_background(self._open_roof)

async def _open_roof(self) -> None:
    async with self.comm.proxy(self.module, IMotion) as proxy:
        await proxy.init()
```

No `@qasync.asyncSlot()` remains for any user-triggered remote call. Sync methods need no decorator;
Qt connects to any callable and drops extra signal args (e.g. `valueChanged(int)` → no-arg method),
which is exactly what the current no-arg asyncSlots already rely on.

### 2. Replace `show_error()` with the shared `show_remote_error()` helper

`show_error()` (`base.py`) did `title, message = err.split(":")` — breaks on any message containing
":", e.g. `str(e) == "Cannot move: motor stalled at 12:30"` yields a nonsense title. It is replaced
by the shared `show_remote_error()` helper below: title = exception class name, body = the message
only (`PyobsError.__str__` already prefixes the class name, so `str(exception)` would duplicate it
— use `exception.message`):

```python
async def show_remote_error(parent: QtWidgets.QWidget, exception: Exception) -> None:
    if isinstance(exception, exc.PyobsError):
        await QAsyncMessageBox.warning(parent, type(exception).__name__, exception.message or str(exception))
    else:
        log.exception("An error occurred.")
        await QAsyncMessageBox.warning(parent, "Error", str(exception))
```

Keep the `warning` icon for all `PyobsError` (see Decisions). `show_error()` and its never-emitted
`_show_error` signal are removed (dead code after this change).

### 3. Non-`BaseWidget` callers use the same helper

`StatusItem.button_clicked` needs the same handling but `StatusItem` isn't a `BaseWidget`. Extract
the display half of `_background_task`'s error handling into one reusable helper so there is
genuinely a single code path:

```python
# base.py
async def show_remote_error(parent: QtWidgets.QWidget, exception: Exception) -> None:
    if isinstance(exception, exc.PyobsError):
        await QAsyncMessageBox.warning(parent, type(exception).__name__, str(exception))
    else:
        log.exception("An error occurred.")
        await QAsyncMessageBox.warning(parent, "Error", str(exception))
```

`_background_task` and `StatusItem.button_clicked` both delegate to it.

### 4. `_update_loop()`: log, throttled, never a dialog

Background polling failures must not pop a dialog per failed poll (spam). Replace the silent
`except (exc.PyobsError, IndexError): sleep` with throttled logging — first failure, then every 60th
(~once a minute at the 1 s poll interval), counter reset on success:

```python
async def _update_loop(self) -> None:
    consecutive_failures = 0
    while True:
        try:
            ...existing body...
            consecutive_failures = 0
        except (exc.PyobsError, IndexError) as e:
            consecutive_failures += 1
            if consecutive_failures == 1 or consecutive_failures % 60 == 0:
                log.warning("Update of %s failed: %s", self.module, e)
            await asyncio.sleep(1)
```

### 5. Fold camerawidget's ad-hoc `except Exception` blocks into the shared path

Remove the two `try/except Exception: QMessageBox.information(...); return` blocks in `expose()`
(lines 277-282, 291-295) and let `_background_task` surface failures. Behavior change: the dialog
becomes a warning carrying the actual exception text instead of the generic "Could not set
binning." / "Could not set window." — strictly more useful. The remaining expose steps are still
skipped on failure, because the exception propagates and aborts the task (same as today's `return`).

## Decisions (open questions from the issue)

- **`show_remote_error` icon/title**: title = exception class name, icon = `warning` for all `PyobsError`.
  Rationale: every `PyobsError` — domain or transport — is an operator-actionable failure that can
  simply be retried; `critical` in this codebase is reserved for pre-call checks that block the
  action entirely ("Not permitted to …", "Invalid coordinates" — `QMessageBox.critical` in
  `telescopewidget.move()`).
- **`_update_loop`**: log + throttle, never a dialog (Design §4). User-triggered failures get the
  dialog; background polling gets the log.
- **camerawidget ad-hoc blocks**: folded into the shared path (Design §5).

## Per-file change list

All files under `pyobs_gui/`:

1. `base.py` — replace `show_error()` with the `show_remote_error()` helper (drop the dead
   `_show_error` signal); `_update_loop()` throttled
   logging.
2. `roofwidget.py` — `open_roof` / `close_roof` / `stop_roof` → sync + `run_background`; drop the
   `qasync` import if unused.
3. `coolingwidget.py` — `buttonApply_clicked` → sync + `run_background`; read checkbox/spin values in
   the sync slot.
4. `autofocuswidget.py` — `_run_auto_focus` / `_abort` → sync + `run_background`.
5. `autoguidingwidget.py` — `_start` / `_stop` / `_set_exposure_time` → sync + `run_background`; read
   the spin value in the sync slot.
6. `acquisitionwidget.py` — `_acquire` / `_abort` → sync + `run_background`.
7. `spectrographwidget.py` — `grab_spectrum` / `abort` → sync + `run_background`. `abort` keeps
   setting `exposures_left = 0` synchronously (stops the loop immediately even if the remote abort
   fails); the grab loop (incl. `datadisplay.grab_data`) runs inside the background task.
8. `telescopewidget.py` — `_init_telescope` / `_park_telescope` / `_stop_telescope` → sync +
   `run_background`; `_set_offset` → `run_background(self._do_set_offsets_*, ...)` instead of
   `asyncio.create_task`.
9. `focuswidget.py` — `_set_focus_base` / `_set_focus_offset` → `run_background(...)` instead of
   `asyncio.ensure_future`; `_reset_focus_offset` → sync + `run_background`.
10. `camerawidget.py` — `expose` / `abort` / `set_full_frame` → sync + `run_background`; delete the
    two ad-hoc `except Exception` blocks.
11. `videowidget.py` — `grab_image` → sync + `run_background(self._expose_task_func)` instead of
    `asyncio.create_task`; `exposure_time_changed` / `gain_changed` → sync + `run_background`.
12. `statuswidget.py` — `StatusItem.button_clicked` → try/except delegating to `show_remote_error()`.

`filterwidget.py` / `modewidget.py` / `compassmovewidget.py` need no behavior change; optionally tidy
`filterwidget.set_filter` to create the proxy inside the background task (same pattern as
`modewidget`).

## Verification

No pytest suite exists; verify by driving the real `GUI` module headlessly (offscreen Qt) against
the existing `LocalComm` fixtures (`test/*.yaml`: `roof.yaml`, `telescope.yaml`, `camera.yaml`,
`spectrograph.yaml`, `autofocus.yaml`, `guiding.yaml`, `acquisition.yaml`, `video.yaml`), per the
`verify` skill recipe.

For each converted widget:

1. Open the fixture; show the window so `_init()` runs; wait for the widget to enable.
2. Force the remote call to fail — e.g. monkeypatch the module's method (or the proxy) to raise
   `exc.MoveError("...")` / `exc.RemoteError(...)`.
3. Trigger the slot (call the sync method or `button.click()`).
4. Assert: a `QAsyncMessageBox` appeared with the exception text (observe via `utils._live_dialogs`
   or a patched `QAsyncMessageBox.warning` recording calls); no "Task exception was
   never retrieved" warning; no exception reached the event loop handler; the button re-enables
   afterwards (`_background_task`'s `finally`).

For `_update_loop`: give a widget an `_update_func` that raises `exc.PyobsError`; assert one log
line on first failure, no dialog, and throttled repeats.

## Rollout / out of scope

- pyobs-gui only; no config, API, or pyobs-core changes. Rollback = revert the widget edits.
- Out of scope: `mainwindow.py` background tasks (`_check_warning_task`, `_client_connected`) — not
  user-triggered; event-handler callbacks (`_on_new_data` etc.) — dispatched by comm, logged there;
  `videowidget` MJPEG socket / `_init` failures — already logged; `statuswidget._add_module_details`
  — already caught.
- Follow-up candidates (noted, not planned): give `mainwindow._check_warning_task` the same
  throttled-logging treatment; make `filterwidget.set_filter` proxy creation consistent with
  `modewidget`.
