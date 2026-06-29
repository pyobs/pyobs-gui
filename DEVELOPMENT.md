# pyobs-gui — Phase 4 Development Notes

## Context

pyobs-gui is being updated as part of **pyobs 2.0 Phase 4**. The core change: all
widgets must stop polling via RPC (`get_*`, `list_*`, `is_ready`) and instead
subscribe to state via `comm.subscribe_state()` and read capabilities via
`comm.get_capabilities()`. Events (`MotionStatusChangedEvent`,
`FilterChangedEvent` etc.) are also replaced by state subscriptions.

See the pyobs-core design document:
https://gist.github.com/thusser/f6daf9ae4c41126776efa2e297b71e87

---

## Key API — pyobs-core 2.0

### State subscription
```python
await self.comm.subscribe_state(self.module, ICooling, self._on_state)

async def _on_state(self, state: ICooling.State) -> None:
    self._setpoint = state.setpoint
    self._power = state.power
```

### Capabilities
```python
caps = await self.comm.get_capabilities(self.module, IWindow)
# caps is an IWindow.Capabilities instance or None
if caps is not None:
    full_frame = caps.full_frame  # IWindow.State(x, y, width, height)

caps = await self.comm.get_capabilities(self.module, IFilters)
# caps.filters: list[str]

caps = await self.comm.get_capabilities(self.module, IBinning)
# caps.binnings: list[IBinning.State]

caps = await self.comm.get_capabilities(self.module, IImageFormat)
# caps.image_formats: list[str]

caps = await self.comm.get_capabilities(self.module, IVideo)
# caps.url: str
```

### Presence (replaces get_state / get_error_string)
```python
# Subscribe — callback fires immediately with current state, then on every change
await self.comm.subscribe_presence(self.module, self._on_presence)

def _on_presence(self, state: ModuleState, error_string: str) -> None:
    # ModuleState: READY, ERROR, LOCAL, CLOSED
    if state == ModuleState.ERROR:
        self.label_status.setText(f"ERROR: {error_string}")
    else:
        self.label_status.setText(state.value)

# Or read synchronously (no subscription):
result = self.comm.get_client_state(self.module)
# result: tuple[ModuleState, str] | None
```

### RPC still valid (commands, not queries)
```python
async with self.comm.proxy(self.module, ICooling) as proxy:
    await proxy.set_cooling(enabled=True, setpoint=-20.0)
```

---

## Widget audit — what needs updating

### ✓ Done
- **`coolingwidget.py`** — already uses `subscribe_state(ICooling)`. Done.
- **`modifiedmixin.py`** — `ModifiedMixin`, `ModifiedLineEdit`, `ModifiedSpinBox`,
  `ModifiedDoubleSpinBox` implemented for dirty-state red highlight.

### ✗ Needs updating

**`statuswidget.py`**
- `get_state()` → `comm.subscribe_presence(module, cb)` → callback arg 0
- `get_error_string()` → callback arg 1
- `get_version()` → `comm.get_capabilities(module, IModule)` → `.version`
- Replace polling timer with `subscribe_presence` per module

**`filterwidget.py`**
- `get_filter()` → `subscribe_state(module, IFilters, cb)` → `state.filter`
- `list_filters()` → `get_capabilities(module, IFilters)` → `.filters`
- `get_motion_status()` → `subscribe_state(module, IMotion, cb)` → `state.status`
- Remove `MotionStatusChangedEvent` and `FilterChangedEvent` handlers

**`focuswidget.py`**
- `get_focus()` → `subscribe_state(module, IFocuser, cb)` → `state.focus`
- `get_focus_offset()` → `subscribe_state(module, IFocusOffset, cb)` → `state.focus_offset`
- `get_motion_status()` → `subscribe_state(module, IMotion, cb)` → `state.status`
- Remove `MotionStatusChangedEvent` handler

**`roofwidget.py`**
- `get_motion_status()` → `subscribe_state(module, IMotion, cb)` → `state.status`
- `get_altaz()` → `subscribe_state(module, IPointingAltAz, cb)` → `state.alt/az`

**`telescopewidget.py`**
- `get_motion_status()` → `subscribe_state(module, IMotion, cb)` → `state.status`
- `get_radec()` → `subscribe_state(module, IPointingRaDec, cb)` → `state.ra/dec`
- `get_altaz()` → `subscribe_state(module, IPointingAltAz, cb)` → `state.alt/az`
- `get_offsets_radec()` → `subscribe_state(module, IOffsetsRaDec, cb)` → `state.dra/ddec`
- Remove `MotionStatusChangedEvent` handler

**`camerawidget.py`**
- `get_exposure_status()` → `subscribe_state(module, IExposure, cb)` → `state.status`
- `list_binnings()` → `get_capabilities(module, IBinning)` → `.binnings`
- `list_image_formats()` → `get_capabilities(module, IImageFormat)` → `.image_formats`
- Remove `ExposureStatusChangedEvent` handler

**`spectrographwidget.py`**
- `get_exposure_status()` → `subscribe_state(module, IExposure, cb)` → `state.status`
- Remove `ExposureStatusChangedEvent` handler

**`videowidget.py`**
- `get_video()` → `get_capabilities(module, IVideo)` → `.url`
- `get_exposure_time()` → `subscribe_state(module, IExposureTime, cb)` → `state.exposure_time`
- `get_gain()` → `subscribe_state(module, IGain, cb)` → `state.gain`

**`temperatureswidget.py`**
- `get_temperatures()` → `subscribe_state(module, ITemperatures, cb)` → `state.readings`

**`modewidget.py`**
- `get_motion_status()` → `subscribe_state(module, IMotion, cb)` → `state.status`
- `list_mode_groups()` / `list_modes()` / `get_mode()` — these are still RPC
  (no State/Capabilities replacement yet in pyobs-core for IMode)
- Remove `MotionStatusChangedEvent` handler; keep `ModeChangedEvent` for now

---

## Pattern to follow

`coolingwidget.py` is the reference implementation. The general pattern:

```python
class MyWidget(Base):
    async def _init(self) -> None:
        # 1. Subscribe to state — delivers current value immediately
        await self.comm.subscribe_state(self.module, IMyInterface, self._on_state)

        # 2. Read capabilities (static, read once)
        caps = await self.comm.get_capabilities(self.module, IMyInterface)
        if caps is not None:
            self._populate_combo(caps.my_list)

    def _on_state(self, state: IMyInterface.State) -> None:
        # Called immediately with current value, then on every change
        self._my_value = state.my_field
        self._update_ui()

    def _update_ui(self) -> None:
        # Pure Qt, no async — update widgets from cached state
        ...
```

Key points:
- **No polling** — no `_update()` timers calling `get_*` RPCs
- **No event handlers** for state-replaced events (`MotionStatusChangedEvent`,
  `FilterChangedEvent`, `ExposureStatusChangedEvent`)
- **`_init`** is called once when the module connects; re-called on reconnect
- Callbacks from `subscribe_state` are called from the asyncio event loop —
  use `QMetaObject.invokeMethod` or signals if updating Qt widgets from them

---

## Testing

Test configs live in `test/` in the pyobs-gui repo. Each is a `MultiModule`
that runs the relevant dummy module and the GUI in a single process via
`LocalComm` — no XMPP server needed.

```bash
cd pyobs-gui
mkdir -p /tmp/pyobs-test      # shared VFS cache dir for camera images
pyobs test/camera.yaml       # camerawidget, coolingwidget, filterwidget, temperatureswidget
pyobs test/telescope.yaml    # telescopewidget, focuswidget
pyobs test/roof.yaml         # roofwidget
pyobs test/spectrograph.yaml # spectrographwidget
pyobs test/mode.yaml         # modewidget
pyobs test/full.yaml         # all of the above together
```

### Missing: DummyVideo
`videowidget` has no dummy module yet — `BaseVideo` is abstract and requires
a real video source. Options:
1. Write a `DummyVideo` in pyobs-core that serves a static MJPEG stream or
   returns a fixed URL string
2. Test `videowidget` manually against a real video source

For now, `videowidget` is excluded from the test configs.

---

## Machines / repos

- pyobs-gui repo: `git@github.com:pyobs/pyobs-gui.git`, branch `develop`
- Working machines: `husserLaptop`, `astro144`
- pyobs-core must be installed from its `develop` branch for the new API