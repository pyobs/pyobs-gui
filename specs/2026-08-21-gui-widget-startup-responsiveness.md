# Plan: pyobs-gui — make module widgets appear and respond immediately at startup

Status: proposed
Audited: 2026-08-21

## Problem

When pyobs-gui starts (or a new module connects), the module's nav-list entry appears in the
sidebar **before** the widget behind it is ready, and there is no loading feedback anywhere:

1. **Clicks are silently dropped.** `MainWindow._add_client()` (`mainwindow.py:415`) adds the
   nav item first, then `await widget.open(...)`, and only afterwards adds the widget to the
   `stackedWidget` and registers it in `self._widgets`. `_change_page()` (`mainwindow.py:445`)
   early-returns when `client not in self._widgets`, so clicking a module name right after it
   appears does nothing at all — the row highlights, the page never changes, and the user has to
   click again later with no hint.
2. **The widget is blank and disabled until state arrives.** No widget passes `update_func`, so
   every widget is purely state-subscription driven. Content is fetched only on first show
   (`BaseWidget.showEvent` → `_init()`, `base.py:261-268`), which is deferred until the page is
   clicked. Until the first state callback, widgets are `setEnabled(False)` and show `N/A`/empty
   fields (e.g. `TelescopeWidget.__init__` disables itself, `telescopewidget.py:77`, and only
   `update_gui()`, triggered by state callbacks, re-enables it).
3. **The telescope is the worst case.** Its `open()` chain is the heaviest in the codebase —
   compass widget + `get_interfaces` + ACL `get_permitted_methods` + up to three sidebar widgets
   (Filter/Focus/Temperatures, each opened) + a `get_capabilities(IModule)` observer fallback in
   login/standalone mode — all sequential (`telescopewidget.py:142-199`). On first click its
   `_init()` then fires five sequential `subscribe_state` calls (`:201-210`). Camera is similar:
   `_init()` has several `wait_for_state()` calls with the default **10 s timeout**
   (`interface.py:53-54`, e.g. `camerawidget.py:120,140,148,162,170,178,188`).
4. **Startup itself is serialized.** `_init_clients()` (`mainwindow.py:353`) awaits
   `_client_connected()` for each module sequentially, and each call additionally rebuilds the
   Shell command model over **all** clients (`_update_client_list` → `CommandModel.init`,
   `shellwidget.py:40` — O(N) per module, O(N²) total, with synchronous interface introspection on
   the UI thread) and re-scans all clients for autonomous/weather modules (`_check_warnings`).

## Current state (audited 2026-08-21)

- `mainwindow.py:415-443` — `_add_client()`: nav item added before `widget.open()`; widget added
  to `stackedWidget` and `self._widgets` only afterwards.
- `mainwindow.py:445-465` — `_change_page()`: silent `return` for clients not yet in `_widgets`.
- `mainwindow.py:353-356` — `_init_clients()`: strictly sequential per-client awaits.
- `mainwindow.py:626-690` — `_client_connected()`: per-module chain includes
  `await self._update_client_list()` (Shell command-model rebuild over all clients) and
  `await self._check_warnings()` (all-clients scan ×2).
- `base.py:261-287` — `showEvent` → `_init()` once; content is subscription-driven, no `update_func`
  is used by any widget; `_update_loop` (`base.py:289`) never actually runs.
- `telescopewidget.py:142-210`, `camerawidget.py:59-198` — heavy sequential `open()`/`_init()`
  chains (see Problem §3).
- No loading indicator exists anywhere in `pyobs_gui/`.

## Design

### 1. `_add_client()` becomes non-blocking: placeholder page + background open

The nav item, the page, and the widget registry all exist the moment the module connects; only the
remote work is deferred:

```python
# mainwindow.py — new state
self._pages: Dict[str, QtWidgets.QWidget] = {}          # client -> current page (placeholder or real)
self._pending_opens: Dict[str, asyncio.Task[None]] = {}  # client -> in-flight open task
```

```python
async def _add_client(self, client: str, icon: QtGui.QIcon, widget: BaseWidget) -> None:
    # nav item first, exactly as today
    item = PagesListWidgetItem()
    item.setIcon(icon)
    item.setText(client)
    self.listPages.addItem(item)
    self.listPages.sortItems()

    # register immediately so _change_page and the shortcuts always find the client
    self._widgets[client] = widget

    # placeholder page: clickable now, explains the delay, no per-widget changes
    placeholder = self._make_loading_page(client, icon)
    self.stackedWidget.addWidget(placeholder)
    self._pages[client] = placeholder

    # open in the background; swap in the real widget when done
    self._pending_opens[client] = asyncio.create_task(self._open_client(client, widget))

async def _open_client(self, client: str, widget: BaseWidget) -> None:
    try:
        await widget.open(
            modules=[client] if client is not None else [],
            comm=self.comm, observer=self.observer, vfs=self.vfs,
        )
    finally:
        self._pending_opens.pop(client, None)

    # swap placeholder -> real widget at the same stackedWidget index
    placeholder = self._pages.get(client)
    if placeholder is None:
        return  # client disconnected while opening

    # capture BEFORE removeWidget(placeholder): once the placeholder is removed from the
    # stack it can never again be currentWidget(), so the check has to happen first or the
    # "user is sitting on this page" branch below can never fire
    was_current = self.stackedWidget.currentWidget() is placeholder

    idx = self.stackedWidget.indexOf(placeholder)
    self.stackedWidget.removeWidget(placeholder)
    placeholder.deleteLater()
    self.stackedWidget.insertWidget(idx, widget)
    self._pages[client] = widget

    # if the user is sitting on this page, show the real widget now — showEvent ->
    # _init() runs and the content fills in
    if was_current:
        self.stackedWidget.setCurrentWidget(widget)
```

`_make_loading_page(client, icon)` returns a plain `QWidget` with a centered vertical layout: the
module's icon and a grey "Loading <client>…" label. No new dependency (no spinner package).

`_change_page()` switches on `self._pages[client]` instead of `self._widgets[client]`, so a click
during `open()` switches to the placeholder instantly — **the click is never dropped**, and the
"Loading…" text tells the user why the content is not there yet. Section headers still fall out
naturally: they are in neither map.

`_client_disconnected()` (`mainwindow.py:692`) gains a cancel of the pending open task (see §3).

### 2. Parallel initial discovery

```python
async def _init_clients(self) -> None:
    await asyncio.gather(*(self._client_connected(Event(), c) for c in self.comm.clients))
```

Each `_client_connected` now returns as soon as its placeholder is registered; the heavy per-widget
`open()` chains run concurrently as their own tasks (see §1). Later connects (ModuleOpenedEvent
handlers) are already dispatched as separate tasks by the comm layer, so they stay concurrent too.

### 3. Remove the redundant per-connect global work from `_client_connected`

- **Drop `await self._update_client_list()` and `await self._check_warnings()` from
  `_client_connected()`.** Warnings are already covered by the periodic `_check_warning_task()`
  (`mainwindow.py:594`, every 5 s) plus the initial call in `open()`; add one `_check_warnings()`
  after the `_init_clients` gather so the state is fresh immediately at startup. This kills the
  O(N²) Shell command-model rebuild at startup and the duplicate all-clients scans per module.
- **Keep the log-filter client menu current cheaply**: `_update_client_list()` is split — the
  `_clients_menu` rebuild (cheap, purely local) stays called per connect/disconnect; the
  `shell.update_client_list()` → `CommandModel.init()` half is gated on the Shell page being
  visible (and otherwise skipped, since the Shell widget already listens to module open/close
  events itself via `shellwidget.py:203` and can rebuild lazily on first show).
- `_client_disconnected()` additionally:
  ```python
  task = self._pending_opens.pop(client, None)
  if task is not None:
      task.cancel()
  ```
  and remove the placeholder/page from `self._pages` alongside the existing nav-item/widget
  removal, so a module that vanishes mid-open leaves no ghost page. Note `task.cancel()` is not
  synchronous — the coroutine only unwinds at its next `await` inside `widget.open()` — so the
  `widget.discard()` call a few lines later in `_client_disconnected()` can still run concurrently
  with the tail of a not-yet-cancelled `open()`. This is pre-existing risk shape (open() is already
  unguarded against concurrent discard in theory), not newly introduced, but is worth a comment in
  the code since it's easy to assume `cancel()` finishes the job.
- **`discard_all_widgets()` (`mainwindow.py:375`) must also cancel `self._pending_opens`.** It
  exists specifically to stop async callbacks from firing after Qt starts tearing down widgets
  during `GUI._logout()`'s reconnect flow ("libshiboken: Internal C++ object already deleted").
  The placeholder design adds exactly the kind of background task that can trigger this: an
  `_open_client` task can still be running — touching `self.stackedWidget` and the widget it's
  about to swap in — when logout starts. Add, at the top of `discard_all_widgets()`:
  ```python
  for task in self._pending_opens.values():
      task.cancel()
  for task in list(self._pending_opens.values()):
      with contextlib.suppress(asyncio.CancelledError):
          await task
  self._pending_opens.clear()
  ```
  before the existing per-widget `discard()` loop, so no `_open_client` task is still mutating
  `stackedWidget`/a widget after teardown begins.

### 4. Harden `_showEvent` against the pre-existing double-init race

Two rapid show/hide/show cycles can spawn two concurrent `_showEvent` tasks, both seeing
`_initialized is False` and both running `_init()` → duplicate subscriptions. Memoize the init run:

```python
async def _showEvent(self, event: QtGui.QShowEvent) -> None:
    if not self._initialized and hasattr(self, "_init"):
        if self._init_task is None:
            self._init_task = asyncio.create_task(self._run_init())
        await self._init_task

async def _run_init(self) -> None:
    try:
        await self._init()
    finally:
        self._initialized = True
```

(Small, isolated; the placeholder design already guarantees `_init()` only ever runs after
`open()` finished, since the real widget is only inserted/shown post-open — no new
open/init concurrency is introduced.)

### 5. Fast-follow widget cleanups (independent of the above, same PR or next)

- `telescopewidget.py:_init()` — fire the five `subscribe_state` calls concurrently with
  `asyncio.gather` (each is independent; XmppComm's `_subscribe_state` already returns
  immediately and subscribes in background tasks, so this mainly removes the sequential await
  hops).
- `camerawidget.py:_init()` — pass an explicit short `timeout=` to each `wait_for_state()`
  (e.g. 2 s instead of the 10 s default) and gather the independent capability/state fetches, so a
  slow-publishing camera can't hold the page blank for ~70 s in the worst case.
- `shellwidget.py` — debounce `CommandModel.init()` rebuilds (and only rebuild when the Shell page
  is visible), instead of on every module connect.

## Decisions

- **Placeholder page, not "register early + show the half-built widget".** Showing the real widget
  before `open()` finishes would render a half-built UI (empty combo boxes, missing sidebar) and
  reintroduce an open/`_init` race (e.g. `TelescopeWidget._init` reads `self._interfaces`, which
  `open()` populates). A dedicated "Loading…" page keeps per-widget code untouched and makes the
  delay self-explanatory.
- **Loading indicator = simple centered label + module icon.** No new dependency (no
  `QProgressIndicator` package); the label is replaced by the real widget the moment `open()`
  completes.
- **`_update_client_list` / `_check_warnings` per connect: dropped.** The periodic warning task
  plus one post-gather call covers warnings; the Shell command model rebuild is gated on
  visibility. Per-connect O(N) work was the dominant startup cost behind the serialized
  `_init_clients`.
- **Pre-warming `_init()` at open time is explicitly out of scope.** It would make first-click
  content instant but adds state subscriptions for pages the user may never open (traffic and
  churn on every module the GUI is subscribed to). Revisit later if first-click latency after the
  placeholder swap still feels slow.

## Per-file change list

All files under `pyobs_gui/` (plus `tests/`):

1. `mainwindow.py` — `_add_client` restructure (§1: placeholder + background open + swap),
   `_change_page` → `self._pages`, `_init_clients` → `asyncio.gather` (§2), drop per-connect
   `_update_client_list`/`_check_warnings` and add the post-gather call (§3), `_client_disconnected`
   cancels pending opens and cleans `_pages` (§3), `_make_loading_page` helper (§1),
   `discard_all_widgets()` cancels and drains `_pending_opens` before discarding widgets (§3).
2. `base.py` — memoized init task in `_showEvent` (§4).
3. `shellwidget.py` — visibility-gated + debounced `CommandModel` rebuild (§5).
4. `telescopewidget.py` — `_init()` gather (§5).
5. `camerawidget.py` — explicit `wait_for_state` timeouts + gather in `_init()` (§5).
6. `tests/` — new tests (see Verification).

No `pyobs-core` changes.

## Verification

### New pytest coverage (offscreen Qt, existing `tests/` infrastructure)

- `MainWindow._add_client` with a fake slow-opening `BaseWidget` (its `open()` sleeps or awaits a
  controllable event): assert the nav item exists and `_pages[client]` is the placeholder
  immediately; `_change_page` to it shows the placeholder; when `open()` completes the real widget
  replaces the placeholder; if the page was current, `stackedWidget.currentWidget()` becomes the
  real widget (and `_init` fires). Fake `Comm` with `clients`, `proxy`, `register_event`,
  `subscribe_state`, `get_interfaces`, `clients_with_interface` mocks, per the `FakeComm` pattern
  in `tests/test_camerawidget.py`.
- `_client_disconnected` mid-open: pending open task is cancelled, placeholder removed, no ghost
  page.
- `_init_clients` parallel: two clients whose `open()` blocks on different events both reach the
  placeholder stage before either open completes (assert via event ordering, not wall-clock).
- `TelescopeWidget._init` gather: fake comm records that all five `subscribe_state` calls are
  in flight before any completes.
- Regression: existing `tests/` suite stays green (`pytest tests/`).

### Integration (LocalComm fixtures)

Drive the real `GUI` module headlessly against the existing `test/*.yaml` fixtures (`full.yaml`,
`telescope.yaml`, `camera.yaml`, ...) per the `verify` skill recipe: connect, assert each nav item
appears immediately, click a module name during its open window, assert the "Loading…" page shows,
then assert the real widget and its content arrive without a second click. For `telescope.yaml`,
assert the page fills (status labels populated, controls enabled) within a bounded time of the
first click.

### Manual (XMPP)

Real-network run: click each module right after it appears — page switches instantly to
"Loading…", then auto-fills; telescope page fills within a few seconds of the first click.

## Rollout / out of scope

- pyobs-gui only; no config, API, or pyobs-core changes. Rollback = revert the widget edits
  (the placeholder/`_pages` machinery is confined to `mainwindow.py`).
- Out of scope: pre-warming `_init()` at open time (Decision), moving `CommandModel.init`'s
  `inspect` work off the UI thread, `StatusWidget`'s own per-module RPC chains
  (`statuswidget.py:_add_module_details` — same "fills in later" UX but not part of the click
  problem), and any pyobs-core `wait_for_state` default-timeout change. Also out of scope (noted,
  pre-existing, unrelated to this plan): `ShellWidget.open()` (`shellwidget.py:164-165`) registers
  its `ModuleOpenedEvent`/`ModuleClosedEvent` handlers via `self.comm.register_event()` directly
  instead of the tracked `BaseWidget.register_event()` wrapper, so `discard()` never unregisters
  them — a leak on every logout/reconnect — and it duplicates the `CommandModel` rebuild the
  mainwindow-side `_update_client_list()` already triggers per connect. Worth its own fix later.
- Follow-up candidates (noted, not planned): auto-switch to a newly connected module when its
  nav item is already selected; show a spinner instead of the static label if the open takes
  long; pre-warm `_init` for the most recently used pages.
