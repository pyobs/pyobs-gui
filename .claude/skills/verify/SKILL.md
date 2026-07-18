---
name: verify
description: Drive the real pyobs-gui app headlessly against a real pyobs module (LocalComm) to verify a widget change actually works end-to-end.
---

# Verifying pyobs-gui changes

pyobs-gui is a PySide6 app that talks to pyobs modules over `Comm`. There's no
pytest suite (see `DEVELOPMENT.md`) — verification means running the real
`GUI` module against a real target module and observing widget state /
screenshots. This works headlessly, no Xvfb needed.

## The recipe

`test/*.yaml` are `MultiModule` fixtures that run a target module (e.g.
`DummyCamera`) and `pyobs_gui.GUI` in one process, connected via
`pyobs.comm.local.LocalComm` (in-process, no network). Normally launched with
`uv run pyobs test/camera.yaml`, but for scripted verification, drive it from
Python directly so you can reach into live widget state:

```python
import os
os.environ["QT_QPA_PLATFORM"] = "offscreen"  # before importing PySide6/qasync

import asyncio, yaml
from pyobs.object import get_object
from pyobs.modules import Module
from pyobs_gui.gui import GUI

async def main():
    with open("test/camera.yaml") as f:
        cfg = yaml.safe_load(f)
    multi = get_object(cfg, Module)
    await multi.open()          # returns once sub-modules are *scheduled*, not ready
    gui = multi["gui"]
    # poll gui._window, then window._widgets["<module-name>"] until present
    ...

loop = GUI.new_event_loop()     # QApplication(offscreen) + qasync.QEventLoop
asyncio.set_event_loop(loop)
loop.run_until_complete(main())
```

A working end-to-end example lives in git history / can be reconstructed from
this skill — see the gotchas below, they're all non-obvious.

## Gotchas

1. **`MultiModule.open()` doesn't wait for children.** Each sub-module opens
   as its own asyncio task. Poll `gui._window is not None`, then
   `"<name>" in window._widgets`, with `asyncio.sleep(0.1)` between checks.

2. **Widgets only run `_init()` on a real Qt `showEvent`**
   (`pyobs_gui/base.py:245-252`, `BaseWidget.showEvent`/`_showEvent`). A
   widget sitting in a `QStackedWidget` that's never made current, or a
   `QMainWindow` that's never `.show()`n, never fires it — `has_proxy`/
   `subscribe_state` calls in `_init()` never run, buttons stay disabled
   forever. Always `window.stackedWidget.setCurrentWidget(widget)` +
   `window.show()` *before* waiting for the widget to become enabled.

3. **Don't call `QApplication.processEvents()` manually inside a coroutine
   running on the qasync loop.** It reenters qasync's own dispatch and
   silently drops other scheduled coroutines (you'll see spurious
   `RuntimeWarning: coroutine '...' was never awaited` for totally unrelated
   widgets). Just `await asyncio.sleep(...)` — qasync pumps Qt events as
   part of the normal loop.

4. **Fire-and-forget RPCs prove nothing about the server side just by not
   raising.** Methods like `IDataSequence.grab_sequence()` return
   immediately; the real work happens in a background task on the target
   module. A clean `await proxy.grab_sequence(...)` only means the call
   dispatched — verify the actual effect via the pushed state
   (`subscribe_state` callback / widget fields) or a registered event
   handler (e.g. `NewImageEvent`), not the call's return.

5. **`DummyCamera`'s default `"pyobs"` VFS root is hardcoded to
   `/opt/pyobs/storage/`** (`pyobs/vfs/vfs.py`), used for its FITS
   frame-number cache regardless of your `vfs:` config — not writable by a
   regular user. Override it in the loaded config before `get_object()`:
   ```python
   cfg["vfs"]["roots"]["pyobs"] = {"class": "pyobs.vfs.LocalFile", "root": "/tmp/some-writable-dir/"}
   ```
   (YAML anchors mean `cfg["vfs"]` is shared by reference with each module's
   `vfs: *vfs`, so mutating the top-level dict before construction is
   enough.)

6. **`DummyCamera` needs the optional `photutils` package** to simulate
   images at all (`pip install photutils` into the venv — not a pyobs-gui
   dependency, just needed for this fixture). Even then, as of photutils
   3.0.0 there's a real incompatibility bug in pyobs-core's
   `DummyCamera._simulate_image()`: `make_model_image()` is called with a
   params table using column name `x_0`, which newer photutils rejects
   (`ValueError: value "x_0" not in params_table column names`) — but only
   when `exposure_time > 0` (it tries to paint simulated star sources sized
   by exposure). Setting exposure_time to `0.0` sidesteps it entirely, and
   `DummyCamera`'s default `readout_time=2` (seconds, per grab) is still
   enough on its own to observe multi-grab sequence progress and test
   aborting mid-sequence.

## Capturing evidence

`window.grab().save(path)` on the (offscreen) `QMainWindow` produces a real
PNG of the actual rendered UI — read it back with the Read tool to inspect.
