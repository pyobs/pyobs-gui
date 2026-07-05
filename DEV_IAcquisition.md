# IAcquisition widget

**Status:** design proposal — not implemented yet.

## Current state (pyobs-core, `develop`)

`IAcquisition` (`pyobs/interfaces/IAcquisition.py:26`) already inherits `IRunning` and
`IAbortable`:

```python
class IAcquisition(IRunning, IAbortable, metaclass=ABCMeta):
    async def acquire_target(self, **kwargs: Any) -> AcquisitionResult: ...
```

`AcquisitionResult` (`IAcquisition.py:14`) carries `time`, `ra`, `dec`, `alt`, `az`, and optional
`off_ra`/`off_dec` or `off_alt`/`off_az` — but it's only ever returned from the RPC call, never
pushed as state.

The one real implementation, `Acquisition` (`pyobs/modules/pointing/acquisition.py:43`), confirms
the same wiring gap seen in `IAutoFocus`: `is_running()` (`acquisition.py:102`) correctly returns
`self._is_running`, but that flag (set at `acquisition.py:122`/`126`) is **never published via
`set_state(IRunning, ...)`** — `IRunning` is already in the interface's MRO, but nothing calls it.
So unlike `IAutoFocus`, the interface itself is already correctly designed; only the implementation
is missing the publish call.

More interesting: acquisition is genuinely iterative. `_acquire()` (`acquisition.py:130` onward)
loops up to `self._attempts` times, each iteration takes an image, computes an on-sky distance to
target (`osd.distance`, arcsec), and either finishes (distance within `self._tolerance`), applies an
offset and continues, or gives up (distance beyond `self._max_offset`). None of that per-attempt
telemetry is currently surfaced — a widget only sees the final `AcquisitionResult`, and only if it
was the one that made the RPC call.

## Proposed pyobs-core change

Publish `RunningState` around `acquire_target()`, same fix as `IAutoFocus`:

```python
async def acquire_target(self, **kwargs: Any) -> AcquisitionResult:
    try:
        self._is_running = True
        await self.comm.set_state(IRunning, RunningState(running=True))
        self._abort_event = asyncio.Event()
        return await self._acquire(self._default_exposure_time)
    finally:
        self._is_running = False
        await self.comm.set_state(IRunning, RunningState(running=False))
```

Then add a dedicated growing state, mirroring `AutoFocusState`'s pattern, so the per-attempt
distance is visible live rather than only in the final result:

```python
# IAcquisition.py
@dataclass
class AcquisitionAttempt:
    attempt: int
    distance: Annotated[float, Unit.ARCSEC]
    offset_applied: bool

@dataclass
class AcquisitionState:
    attempts: list[AcquisitionAttempt] = field(default_factory=list)
    result: AcquisitionResult | None = None
    time: Time = field(default_factory=Time.now)

class IAcquisition(IRunning, IAbortable, metaclass=ABCMeta):
    state = AcquisitionState
    ...
```

And in `Acquisition._acquire()`, publish after each attempt (right after `osd.distance` is known,
around `acquisition.py:200`):

```python
self._attempts_log.append(AcquisitionAttempt(attempt=a, distance=osd.distance.arcsec, offset_applied=False))
await self.comm.set_state(IAcquisition, AcquisitionState(attempts=self._attempts_log))
```

and set `result=` on the final publish once `_create_log_and_return()` produces it.

## Widget design (pyobs-gui)

Same visual language as the `IAutoFocus` widget — this is the same shape of problem (one-shot,
abortable, iterative, converges-or-fails):

- `framePlot` — distance-to-target (arcsec) vs attempt number, one point per iteration, so you can
  see it converging (or not) live
- `buttonAcquire` (green) / `buttonAbort` (red)
- `labelStatus` — Idle / Acquiring... / `Acquired.`
- Result group box: RA/Dec, Alt/Az, and whichever offset pair (`off_ra`/`off_dec` or
  `off_alt`/`off_az`) is populated, from the final `AcquisitionState.result`

```python
class AcquisitionWidget(BaseWidget, Ui_AcquisitionWidget):
    signal_update_gui = QtCore.Signal()

    def __init__(self, **kwargs: Any):
        BaseWidget.__init__(self, **kwargs)
        self.setupUi(self)

        self._attempts: list[AcquisitionAttempt] = []
        self._running = False
        self._result: AcquisitionResult | None = None

        self.figure, self.ax = plt.subplots()
        layout = QtWidgets.QVBoxLayout(self.framePlot)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.signal_update_gui.connect(self.update_gui)
        self.buttonAcquire.clicked.connect(self._acquire)
        self.buttonAbort.clicked.connect(self._abort)
        self.colorize_button(self.buttonAcquire, QtCore.Qt.GlobalColor.green)
        self.colorize_button(self.buttonAbort, QtCore.Qt.GlobalColor.red)

    async def _init(self) -> None:
        await self.comm.subscribe_state(self.module, IRunning, self._on_running_state)
        await self.comm.subscribe_state(self.module, IAcquisition, self._on_acquisition_state)

    def _on_running_state(self, state: RunningState) -> None:
        if state.running and not self._running:
            self._attempts = []
            self._result = None
        self._running = state.running
        self.signal_update_gui.emit()

    def _on_acquisition_state(self, state: AcquisitionState) -> None:
        self._attempts = state.attempts
        self._result = state.result
        self.signal_update_gui.emit()

    def update_gui(self) -> None:
        self.buttonAcquire.setEnabled(not self._running)
        self.buttonAbort.setEnabled(self._running)

        if self._running:
            self.labelStatus.setText("Acquiring...")
        elif self._result:
            self.labelStatus.setText("Acquired.")
            self.labelRa.setText(f"{self._result.ra:.5f}")
            self.labelDec.setText(f"{self._result.dec:.5f}")
            self.labelAlt.setText(f"{self._result.alt:.3f}")
            self.labelAz.setText(f"{self._result.az:.3f}")
        else:
            self.labelStatus.setText("Idle")

        self.ax.clear()
        if self._attempts:
            self.ax.plot(
                [a.attempt for a in self._attempts],
                [a.distance for a in self._attempts],
                marker="o", color="tab:blue",
            )
        self.ax.set_xlabel("Attempt")
        self.ax.set_ylabel("Distance to target [arcsec]")
        self.ax.grid(linestyle=":", alpha=0.5)
        self.ax.set_axisbelow(True)
        self.canvas.draw()

    @qasync.asyncSlot()  # type: ignore
    async def _acquire(self) -> None:
        async with self.comm.proxy(self.module, IAcquisition) as proxy:
            await proxy.acquire_target()

    @qasync.asyncSlot()  # type: ignore
    async def _abort(self) -> None:
        async with self.comm.proxy(self.module, IAcquisition) as proxy:
            await proxy.abort()
```

## Open questions

- `off_ra`/`off_dec` vs `off_alt`/`off_az` are mutually exclusive depending on mount type — the
  widget needs to show whichever pair is non-`None` rather than a fixed set of four labels.
- Should `attempts` be capped (e.g. keep only the last N) to avoid an unbounded list on a module
  that's misconfigured and cycling forever? `AutoFocusState.points` doesn't cap either, but that
  loop is bounded by `2*count+1` by construction — acquisition's `self._attempts` config already
  bounds it too, so probably fine as-is.
