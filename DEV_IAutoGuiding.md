# IAutoGuiding widget

*Note: pyobs-core's actual interface name is `IAutoGuiding`, not `IGuiding` — used the real name
throughout.*

**Status:** design proposal — not implemented yet.

## Current state (pyobs-core, `develop`)

`IAutoGuiding` (`pyobs/interfaces/IAutoGuiding.py:7`) is bare — it adds no methods or state of its
own, just combines two existing interfaces:

```python
class IAutoGuiding(IStartStop, IExposureTime, metaclass=ABCMeta):
    """The module can perform auto-guiding."""
```

So today it inherits `RunningState` (from `IStartStop` → `IRunning`) and `ExposureTimeState`, and
gets `start()`/`stop()`/`set_exposure_time()` for free.

The one implementation, `BaseGuiding` (`pyobs/modules/pointing/_baseguiding.py:23`), has the same
wiring gap as the other two interfaces: `is_running()` (`_baseguiding.py:85`) correctly returns
`self._enabled`, set in `start()`/`stop()` via `_reset_guiding()` (`_baseguiding.py:144`), but
`RunningState` is never published.

More interesting: there's already real per-image telemetry computed internally that never reaches a
live subscriber:

- `self._loop_closed` (`_baseguiding.py:62`, toggled by `_set_loop_state()` at `155`) — whether the
  last image was successfully guided on (closed loop) or not (open loop). Currently only surfaced
  via a FITS header string, `AGSTATE` (`_baseguiding.py:110,128`).
- `GuidingStatisticsPixelOffset`/`GuidingStatisticsSkyOffset`
  (`pyobs/modules/pointing/guidingstatistics/`) compute an RMS pixel or sky offset — but only as a
  *per-science-exposure session* (`init_stats`/`add_to_header`, keyed by requesting client), written
  into the FITS header of each subsequent image, not as a running live value. `_statistics.add_data(image)`
  (`_baseguiding.py:241`) feeds it on every processed image.

## Proposed pyobs-core change

Publish `RunningState` in `start()`/`stop()`:

```python
async def start(self, **kwargs: Any) -> None:
    log.info("Start auto-guiding...")
    await self._reset_guiding(enabled=True)
    await self.comm.set_state(IRunning, RunningState(running=True))

async def stop(self, **kwargs: Any) -> None:
    log.info("Stopping auto-guiding...")
    await self._reset_guiding(enabled=False)
    await self.comm.set_state(IRunning, RunningState(running=False))
```

Add a dedicated `GuidingState` for the live open/closed-loop status and last offset — separate from
the FITS-header RMS statistics, which stay as they are:

```python
@dataclass
class GuidingState:
    loop_closed: bool = False
    last_offset_x: float | None = None  # pixel offset, axis 1
    last_offset_y: float | None = None  # pixel offset, axis 2
    time: Time = field(default_factory=Time.now)

class IAutoGuiding(IStartStop, IExposureTime, metaclass=ABCMeta):
    state = GuidingState
```

Publish it from `_set_loop_state()` (`_baseguiding.py:155`), which is already the single choke point
every closed/open transition goes through:

```python
async def _set_loop_state(self, state: bool) -> None:
    self._uptime.add_data(state)
    self._loop_closed = state
    await self.comm.set_state(IAutoGuiding, GuidingState(loop_closed=state))
```

`_set_loop_state` is currently synchronous (`_baseguiding.py:155`) — making it `async` means
updating its 5 call sites, but all of them are already inside `async def`s, so it's a mechanical
change rather than a real restructuring.

## Widget design (pyobs-gui)

Guiding is continuous rather than one-shot, so no plot of "progress toward a goal" the way
autofocus/acquisition have — instead, a simple live status display plus the existing pattern for
editable numeric fields:

- `buttonStart` / `buttonStop`, enabled based on `RunningState.running`
- Status label for `loop_closed` — "Closed loop" / "Open loop" / "Stopped"
- `spinExposureTime` — a `ModifiedDoubleSpinBox`, same `ModifiedMixin` pattern used elsewhere in
  pyobs-gui, committing via `set_exposure_time()`
- Last pixel offset (X/Y), plain labels, updating live

```python
class AutoGuidingWidget(BaseWidget, Ui_AutoGuidingWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        self._running = False
        self._loop_closed = False
        self._offset: tuple[float, float] | None = None

        self.signal_update_gui.connect(self.update_gui)
        self.buttonStart.clicked.connect(self._start)
        self.buttonStop.clicked.connect(self._stop)
        self.colorize_button(self.buttonStart, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonStop, QtCore.Qt.GlobalColor.red)

        self.spinExposureTime.init_modified("Exposure time")
        self.spinExposureTime.valueChangedByUser.connect(self._set_exposure_time)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IRunning, self._on_running_state)
        await self.comm.subscribe_state(self.module, IExposureTime, self._on_exptime_state)
        await self.comm.subscribe_state(self.module, IAutoGuiding, self._on_guiding_state)

    def _on_running_state(self, state: RunningState) -> None:
        self._running = state.running
        self.signal_update_gui.emit()

    def _on_exptime_state(self, state: ExposureTimeState) -> None:
        self.spinExposureTime.setValue(state.exposure_time)

    def _on_guiding_state(self, state: GuidingState) -> None:
        self._loop_closed = state.loop_closed
        if state.last_offset_x is not None and state.last_offset_y is not None:
            self._offset = (state.last_offset_x, state.last_offset_y)
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.buttonStart.setEnabled(not self._running)
        self.buttonStop.setEnabled(self._running)
        self.labelLoopState.setText(
            "Closed loop" if self._running and self._loop_closed
            else "Open loop" if self._running
            else "Stopped"
        )
        if self._offset:
            self.labelOffset.setText(f"({self._offset[0]:+.2f}, {self._offset[1]:+.2f}) px")

    @qasync.asyncSlot()  # type: ignore
    async def _start(self) -> None:
        async with self.comm.proxy(self.module, IAutoGuiding) as proxy:
            await proxy.start()

    @qasync.asyncSlot()  # type: ignore
    async def _stop(self) -> None:
        async with self.comm.proxy(self.module, IAutoGuiding) as proxy:
            await proxy.stop()

    @qasync.asyncSlot()  # type: ignore
    async def _set_exposure_time(self, value: float) -> None:
        async with self.comm.proxy(self.module, IExposureTime) as proxy:
            await proxy.set_exposure_time(value)
```

## Open questions

- `_set_loop_state` currently isn't `async` — decide between making it `async` (5 call sites to
  update, all already in async context) or fire-and-forget with `asyncio.create_task` as a cheaper
  first pass.
- Whether `last_offset_x/y` (pixel offsets) is the right unit for a general-purpose widget, given
  `GuidingStatisticsSkyOffset` also exists (arcsec on sky) — pixel offset is guider/camera-specific
  and not directly comparable across setups, arcsec is. Might be worth publishing both, or just
  sky-offset if a consistent astrometric solution is always available at that point in the pipeline.
- No live RMS in `GuidingState` as proposed — only last-offset. A rolling RMS would need its own
  small ring buffer on the module (separate from the per-client `GuidingStatistics` sessions, which
  reset on each FITS header pull and shouldn't be reused for this). Left out for now to keep the
  first cut minimal; easy to add a `rolling_rms_x/y` field later if useful in practice.
