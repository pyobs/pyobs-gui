# Plan: pyobs-gui — main widgets vs. sidebar widgets, automatic tab pages for multi-widget modules

Status: draft
Audited: 2026-08-28

This is the fleshed-out version of [pyobs-gui issue #150]
(https://github.com/pyobs/pyobs-gui/issues/150). The issue body stays the tracker; this doc
carries the verified problem statement, the resolved design decisions, and the implementation
checklist. **Decisions recorded here that the issue left open:** shared sidebar (D2), custom
config = merge per interface / `overwrite: true` replaces (D3), registry-provided tab
labels/icons (D1), single nav entry per module (D4), partial-open-failure keeps the page (D5).

## Problem

Split the widget concept into two explicit categories:

- **Main widget** — fills the entire page area of a module page.
- **Sidebar widget** — lives *only* in the sidebar of a module page; never a page of its own.

And the key behavioral change: **if a module matches several main widgets, its page automatically
becomes a tab widget, one tab per main widget** (e.g. a camera module that is also a focuser gets
a page with "Camera" and "Focuser" tabs). Today only the *first* matching widget wins and the rest
are silently dropped.

Four problems, verified against the code on `develop` (`25e9fee`):

1. **First-match-wins silently hides interfaces.** `DEFAULT_WIDGETS` (`mainwindow.py:54-67`)
   maps each interface to exactly one widget class, and `MainWindow._client_connected()`
   (`mainwindow.py:753-757`) walks that dict with a `break` after the first match. A module that
   implements several interfaces (camera + filter wheel, telescope + focuser + temperature
   sensors, camera + focuser, …) only ever shows one widget, and which one wins depends purely on
   dict order — invisible and arbitrary from the operator's point of view. The other interfaces
   are simply not operated from the GUI.
2. **The two categories are only implicit.** "Sidebar widget" already exists as a runtime concept
   — `BaseWidget.sidebar_widgets` / `add_to_sidebar()` (`base.py:169-171, 232-249`), built-in
   sidebar fills in `CameraWidget.open()` (`camerawidget.py:109-116`) and `TelescopeWidget.open()`
   (`telescopewidget.py:180-186`), and the custom `sidebar:` config key (`mainwindow.py:771-774`).
   But there is no explicit declaration of what is a main widget vs. a sidebar widget, no registry
   for sidebar widgets, and nothing stops a sidebar widget from being misused as a page or vice
   versa. `FilterWidget`, `FocusWidget`, `TemperaturesWidget` already serve both roles today
   (main pages *and* other pages' sidebar content) — the role is positional, not intrinsic.
3. **Custom widgets are limited to one main widget per module.** The `widgets:` config replaces
   the module's single widget (`mainwindow.py:760-766`); there is no way to give one module
   several custom main pages, or to replace just one of several interface-derived pages.
4. **The standalone module window duplicates the limitation.** `ModuleWindow.open()`
   (`modulegui.py:28-32`) repeats the first-match loop, so a module opened in standalone
   "show this one module" mode has the same single-widget ceiling.

### Additional findings from the audit (not in the issue)

- **`IMode` is registered but effectively broken.** `DEFAULT_WIDGETS` maps `IMode → ModeWidget`
  (`mainwindow.py:67`), but `IMode` is absent from `DEFAULT_ICONS` (`mainwindow.py:69-83`, falls
  back to the question-mark icon) and absent from `DEFAULT_CONFIG` (`mainwindow.py:86-101`).
  Consolidating the registries (D1) is a chance to make the three lists agree.
- **Icon inconsistency for `IFilters`:** `DEFAULT_ICONS` says `"ei.graph"` (`mainwindow.py:81`),
  `DEFAULT_CONFIG` says `"mdi.air-filter"` (`mainwindow.py:100`). The registry consolidation
  (D1) makes each interface's icon single-sourced.
- **`DEFAULT_CONFIG` (`mainwindow.py:86-101`) is dead code** — defined, never referenced
  anywhere else in the repo. Decide its fate in D1 (fold its data in / delete it).
- **The `overwrite:` config key is dead.** The docs example shows `overwrite: True`
  (`docs/source/index.rst:17`), but no code reads it; a custom `widgets:` entry always replaces
  the derived widget (last matching entry wins, `mainwindow.py:760-766`). D3 gives it real
  semantics.
- **The sidebar area lives inside each widget, not in `MainWindow`.** `widgetSidebar` exists only
  in `camerawidget.ui:1371`, `telescopewidget.ui:1709`, `spectrographwidget.ui:1045`; the main
  window's page stack (`stackedWidget`, `qt/mainwindow_ui.py:143-145`) hosts self-contained
  widgets. Consequence for D2: a *shared* sidebar needs a container page that owns a sidebar area
  of its own — this is the biggest structural piece of the plan.
- **`BaseWidget.get_fits_headers()` aggregates over `sidebar_widgets` only** (`base.py:414-427`),
  i.e. a module's FITS headers come from its sidebar widgets (the `FitsHeadersWidget` block), not
  from the main widget. This matters for the teardown/aggregation design (§ "FITS headers").

## Goals

- "Main widget" vs. "sidebar widget" becomes an explicit, documented distinction.
- A module matching **multiple** main widgets gets one nav entry whose page is a tab widget, one
  tab per main widget; one match keeps today's page exactly (no tab bar); zero matches shows no
  page (today's behavior).
- Custom config supports multiple main widgets per module and explicit sidebar widgets, with
  per-interface merge semantics.
- Identical behavior in standalone module mode (`ModuleWindow`).
- Disconnect / teardown of a multi-widget page discards every tab and sidebar widget without
  leaks; `get_fits_headers` aggregates across the whole page.

## Decisions

### D1 — Explicit registries (main widgets)

Replace the `interface → widget` dict plus the separate icon dict with one ordered list of
entries carrying interface, widget class, human-readable label and icon. Ordering = today's
`DEFAULT_WIDGETS` order (that order is the tab order and the "first match wins the nav icon" tie
break, so keep it stable):

```python
@dataclass(frozen=True)
class MainWidgetEntry:
    interface: type[Interface]
    widget: type[BaseWidget]
    label: str          # tab text for multi-widget pages
    icon: str           # qtawesome name; tab icon + nav-icon fallback
    sidebar: tuple[tuple[type[Interface] | None, type[BaseWidget]], ...] = ()

MAIN_WIDGETS: list[MainWidgetEntry] = [
    MainWidgetEntry(ICamera, CameraWidget, "Camera", "fa5s.camera", sidebar=(
        (None, FitsHeadersWidget),               # always
        (IFilters, FilterWidget),
        (ICooling, CoolingWidget),
        (ITemperatures, TemperaturesWidget),
    )),
    MainWidgetEntry(ITelescope, TelescopeWidget, "Telescope", "msc.telescope", sidebar=(
        (IFilters, FilterWidget),
        (IFocuser, FocusWidget),
        (ITemperatures, TemperaturesWidget),
    )),
    MainWidgetEntry(IRoof, RoofWidget, "Roof", "ph.house"),
    MainWidgetEntry(IFocuser, FocusWidget, "Focuser", "mdi.image-filter-center-focus"),
    MainWidgetEntry(IAutoFocus, AutoFocusWidget, "Auto focus", "mdi.chart-bell-curve"),
    MainWidgetEntry(IAcquisition, AcquisitionWidget, "Acquisition", "mdi.target"),
    MainWidgetEntry(IAutoGuiding, AutoGuidingWidget, "Auto guiding", "mdi.crosshairs-gps"),
    MainWidgetEntry(IWeather, WeatherWidget, "Weather", "fa5s.cloud-sun"),
    MainWidgetEntry(IVideo, VideoWidget, "Video", "fa5s.video"),
    MainWidgetEntry(ISpectrograph, SpectrographWidget, "Spectrograph", "ei.graph"),
    MainWidgetEntry(IFilters, FilterWidget, "Filter wheel", "mdi.air-filter"),
    MainWidgetEntry(IMode, ModeWidget, "Mode", "ei.video"),
]
```

- `DEFAULT_ICONS` merges into the entries and is deleted. Fix the `IMode` gap and the `IFilters`
  icon along the way (use the `DEFAULT_CONFIG` value `"mdi.air-filter"` for `IFilters`).
- `DEFAULT_CONFIG` is unreferenced dead code; **delete it** (its only data not already in
  `DEFAULT_WIDGETS` is the Shell/Events/Status "always" entries, which are built unconditionally
  in `MainWindow.open()`, `mainwindow.py:320-341`). If a maintainer objects, fold the always-rows
  into a documented constant instead.
- Widget authors can later override `label`/`icon` per class via class attributes — explicitly
  out of scope for v1 (documented in the registry docstring instead).

### D2 — Shared sidebar (per issue recommendation, confirmed)

**A module page's sidebar is a property of the module, not of one tab.** Concretely:

- **Single main widget:** the page is the widget itself, and the sidebar attaches to the widget —
  exactly today's UX (`widget.add_to_sidebar()`, no tab bar, no container).
- **≥ 2 main widgets:** the page is a new container widget (`ModulePage`, see "Design details")
  holding the `QTabWidget` plus its own sidebar column. `add_to_sidebar()` targets the container,
  so FITS headers / filter / focus / temperatures blocks stay visible while switching tabs.
- **Where the fills come from:** the sidebar-fill *triggers* move out of
  `CameraWidget.open()`/`TelescopeWidget.open()` and into the page-assembly layer, driven by the
  `sidebar` tuple on each matched `MainWidgetEntry` (D1). For a single-widget page the assembler
  calls `widget.add_to_sidebar()` with the entry's fills (visually identical to today); for a
  container page it calls `container.add_to_sidebar()` with the **union** of all matched
  entries' fills. Gating stays interface-based (`comm.has_proxy(client, IFilters)` etc., the same
  checks `camerawidget.py:111-116` and `telescopewidget.py:181-186` do today).
- **Why the fills must move (tension in the issue, resolved here):** the issue says "the built-in
  per-widget sidebar fills stay where they are" and also recommends a shared sidebar. Both cannot
  hold simultaneously — if `CameraWidget.open()` keeps filling *its own* `widgetSidebar`, a camera
  tab inside a container gets a per-tab sidebar instead of a shared one. Moving the trigger to the
  assembler, keyed off declarative per-entry fills, is the minimal change that yields a genuinely
  shared sidebar.
- **Custom `sidebar:` config** (`mainwindow.py:771-774`) keeps its contract and targets the page's
  sidebar host (widget for single, container for multi).
- **Custom classes** that fill their own sidebar in `open()` keep working (their code is
  untouched); they just also get no *declared* fills, since a custom entry's `MainWidgetEntry`
  has an empty `sidebar` tuple unless the class declares `sidebar_fills` (see "Custom config",
  D3 — optional class attribute, uniform application rule).
- **Empty sidebar:** the container hides its sidebar column when it ends up with zero sidebar
  widgets (so e.g. a focuser+filter-wheel tab page gains no stray empty column). A single-widget
  page without a `widgetSidebar` area (roof, weather, …) behaves exactly as today: no sidebar.
  Known wrinkle, kept for parity: a custom `sidebar:` entry for such a widget is opened but
  invisible today, and stays that way in v1; the container page is where custom sidebar entries
  are guaranteed visible. Flagged as a possible follow-up.

### D3 — Custom config: merge per interface, `overwrite: true` replaces

New `widgets:` entry contract (each entry: `module`, `widget`, optional `label`, `icon`,
`interface`, `overwrite`):

- `interface: ICamera` → replaces/merges **only** the `ICamera`-derived tab for that module (same
  registry slot, so tab order is stable). Ignored with a log if the module doesn't implement it.
- No `interface` + **no** `overwrite` → the entry is **appended as an extra tab** (new capability:
  several custom main widgets per module).
- No `interface` + `overwrite: true` → the page is **exactly the custom entries** (today's
  semantics, now explicit). The docs example (`docs/source/index.rst:11-19`, `module: guiding`,
  `overwrite: True`) keeps behaving as it does today.
- `label`/`icon` become the tab text/icon (default: widget class name / `DEFAULT_ICONS[None]`).

Sidebar config (`sidebar:`) is unchanged: a list of `{module, widget}` appended to the page's
sidebar after the declared fills.

### D4 — Nav list stays one entry per module

Tabs are internal to the page; per-tab nav entries would be a much bigger change and are
explicitly **out of scope**. Nav icon: the first matched entry's icon; a custom entry's `icon`
(if any) wins for the nav icon when it is the sole/replacing entry. Existing Ctrl+4..0 page
shortcuts key off module names and keep working unchanged (`mainwindow.py:565-622`).

### D5 — Partial open failure keeps the page

Today a failing `open()` tears down the entire client page (`_fail_open`,
`mainwindow.py:507-523`). With several tabs, the same rule would let one flaky interface kill all
others, so:

- Open all of a module's main widgets concurrently (`asyncio.gather` with `return_exceptions`).
- A failed widget's open is logged and **that tab is removed and discarded**; the page stays with
  the remaining tabs.
- If **all** fail → today's `_fail_open` path (remove nav item, placeholder, registry entry).
- A container left with a single tab keeps the tab bar (stable container identity from
  registration to teardown; cosmetic — unwrapping to the bare widget is a possible follow-up).
- Sidebar-widget open failures (inside `add_to_sidebar` → `_open_child`) are logged and the
  widget dropped from the sidebar — a deliberate small improvement over today, where a sidebar
  open failure propagates up through the main widget's `open()` and kills the whole page.

## Design details

### Registry and collection (shared helper)

Add one module-level helper usable by both `MainWindow` and `ModuleWindow` (put it in
`mainwindow.py`; `modulegui.py` already imports `DEFAULT_WIDGETS` from there):

```python
def collect_main_widgets(matchable: Any, custom: list[dict[str, Any]] | None = None) -> list[WidgetChoice]
```

`matchable` is the comm proxy (MainWindow) or the `Module` instance (ModuleWindow);
`isinstance(matchable, entry.interface)` works for both. `WidgetChoice` carries
`(widget, label, icon)` plus the entry's `sidebar` tuple. The helper:

1. Walks `MAIN_WIDGETS` in order, keeping **every** entry whose interface matches → derived
   choices.
2. Applies `custom` entries per D3 (interface replacement keeps the slot; appends land after;
   `overwrite: true` replaces the derived list entirely).
3. Returns the ordered choice list (empty → caller shows no page, exactly today's
   `mainwindow.py:768-769` behavior).

`ModuleWindow.open()` (`modulegui.py:24-36`) replaces its copy of the first-match loop with
`collect_main_widgets(module)` + the same assembly below. (`ModuleWindow` gets no custom-config
support in v1 — it doesn't have that config surface today either; parity means the *multi-widget /
sidebar* behavior, not config.)

### Container: `ModulePage`

New small class in `mainwindow.py` (no `.ui` needed):

```python
class ModulePage(QtWidgets.QWidget):
    """One module's page when it has ≥ 2 main widgets: a QTabWidget of tabs plus a shared
    sidebar column. The sidebar is a property of the module, not of one tab."""
    def __init__(self, entries: list[WidgetChoice], modules: list[str],
                 comm, vfs, observer) -> None: ...
    async def add_to_sidebar(self, widget: BaseWidget) -> None: ...   # mirrors BaseWidget.add_to_sidebar (base.py:232-249)
    async def discard(self) -> None: ...                              # discard every tab widget + sidebar widget
    def get_fits_headers(self, namespaces=None, **kwargs) -> dict: ...  # aggregate tabs + sidebar
    def hide_if_empty_sidebar(self) -> None: ...
```

- Layout: `QHBoxLayout { QTabWidget (one tab per entry: label, icon) | sidebar QWidget }`; the
  sidebar column is hidden when empty (D2).
- `add_to_sidebar()` copies `BaseWidget.add_to_sidebar`'s logic (`base.py:232-249`) but targets
  the container's own sidebar area — the container carries the `comm/vfs/observer` it needs to
  open children (`_open_child`, `base.py:144-145`).
- `discard()` mirrors `BaseWidget.discard()` (`base.py:261-284`) without the `_init_task` part
  (each tab cancels its own init): unregister event handlers, then `await widget.discard()` for
  every tab **and** every sidebar widget. `MainWindow._client_disconnected` and
  `discard_all_widgets` (`mainwindow.py:387-402`) then work unchanged on `_widgets[client]`,
  which is the container.
- `get_fits_headers()` aggregates over each tab's `get_fits_headers()` (custom classes may still
  hold their own sidebar widgets) **plus** the container's own sidebar widgets' headers — this is
  what keeps `ModuleGUI.get_fits_header_before` / `MainWindow.get_fits_headers`
  (`modulegui.py:90-104`, `mainwindow.py:843-857`) correct.

### Page assembly in `MainWindow`

- `_client_connected()` (`mainwindow.py:722-783`): replace the first-match loop and the
  custom-widget replacement with:
  1. `choices = collect_main_widgets(proxy, self.custom_widgets)`; empty → `return False`.
  2. Determine the page host *upfront*: 1 choice → the widget itself; ≥ 2 → a `ModulePage`
     built from the choices (created via `create_widget` so tabs are tracked in
     `_base_widgets` like today).
  3. `await self._add_client(client, icon, host, choices)` — nav item, `_widgets[client] = host`
     registered immediately (shortcuts / `_client_disconnected` keep working mid-open, as today,
     `mainwindow.py:457-459`), placeholder page added, one background `_open_client` task.
- `_open_client()` (`mainwindow.py:469-505`) becomes multi-widget:
  1. `results = await asyncio.gather(*(w.open(modules=[client], comm=..., observer=..., vfs=...) for w in choices), return_exceptions=True)`.
  2. Failed opens: log, `await widget.discard()`, drop the widget (and its tab) from the host.
     All failed → `_fail_open` (existing path).
  3. Apply sidebar fills: for each surviving choice, for each `(interface, klass)` in the unioned
     `sidebar` tuples where `interface is None or await comm.has_proxy(client, interface)` →
     `host.add_to_sidebar(create_widget(klass, module=client))`; then the custom `sidebar:`
     entries (`mainwindow.py:771-774`).
  4. Swap placeholder → host at the same `stackedWidget` index, preserving the
     was-current/show-event logic (`mainwindow.py:486-505`).
- **Lazy init:** no new machinery. Hidden tabs don't run `_init()`/update loops until first shown
  (`base.py:286-308` show-gated `_showEvent`), so tabs behind the current one neither subscribe
  nor poll.
- `_client_disconnected()` (`mainwindow.py:785-841`): unchanged shape — it already handles
  "the page may be a placeholder or the widget"; with a host, `_pages[client]` is the placeholder
  then the host, and `host.discard()` forwards to tabs + sidebar (D2). `_current_widget`
  bookkeeping (`mainwindow.py:813-815`) works on the host.

### Sidebar fills: the class-attribute option

For custom-config resilience the *declared* fills can also be read off the widget class when no
entry-level `sidebar` exists:

```python
class CameraWidget(BaseWidget, Ui_CameraWidget):
    sidebar_fills = [(None, FitsHeadersWidget), (IFilters, FilterWidget),
                     (ICooling, CoolingWidget), (ITemperatures, TemperaturesWidget)]
```

The assembler applies `getattr(entry.widget, "sidebar_fills", entry.sidebar)` uniformly (D2), so
a site that wires `CameraWidget` in via custom `widgets:` config keeps today's sidebar fills. The
in-`open()` fill blocks (`camerawidget.py:109-116`, `telescopewidget.py:180-186`) are deleted.

## Consequences

- **Behavior change (intended):** multi-interface modules finally expose every interface from the
  GUI — the core of the issue.
- **Sidebar plumbing moves** from widget `open()` to the assembly layer; widget classes lose
  their in-`open()` fills but keep their (now vestigial for tab pages) internal `widgetSidebar`
  areas. Removing the vestigial areas from the three `.ui` files is a cosmetic follow-up, not
  required for correctness.
- **`overwrite:` becomes real config**; docs example unchanged in effect.
- **Registry consolidation** fixes the `IMode` and `IFilters` inconsistencies and deletes dead
  `DEFAULT_CONFIG`.
- **Tests** calling `_add_client(client, icon, widget)` directly
  (`tests/test_mainwindow_startup.py:131,166,188,210`) must be updated for the new signature
  (single-entry list keeps them one line each).
- Non-goals: per-tab nav entries, per-tab sidebars, per-class label/icon overrides, unwrapping a
  1-tab container, `ModuleWindow` custom-config support, removing vestigial `.ui` sidebar areas,
  config-driven `DEFAULT_CONFIG`-style page sets.

## Tests

New `tests/test_multiwidget_pages.py` (offscreen pytest, same `qapp`/fake-comm infra as
`tests/test_mainwindow_startup.py`):

- Proxy implementing `ICamera` + `IFocuser` → one nav entry; `_pages[client]` is a `ModulePage`;
  tab texts "Camera"/"Focuser"; sidebar fills (FitsHeadersWidget etc.) land on the container.
- Single interface → page is the bare widget (`not isinstance(page, ModulePage)`), no tab bar.
- No matching interface → `_client_connected` returns `False`, no nav item.
- Custom config: two `widgets:` entries → two tabs; `interface:` entry replaces the same-
  interface tab (slot order kept); `overwrite: true` → exactly the custom entries.
- Disconnect a multi-widget module → `discard()` called on every tab and every sidebar widget
  (spy widgets record it), stack has no ghost pages, `_widgets`/`_pages` entries gone.
- `get_fits_headers` aggregates across tabs + sidebar (sidebar `FitsHeadersWidget` stub returns
  known entries).
- Partial open failure (one of two widgets' `open()` raises) → failed tab removed and discarded,
  page kept; all fail → client torn down (existing `_fail_open` semantics).
- `ModuleWindow`: a module object implementing two interfaces → `setCentralWidget` is a
  `ModulePage` with two tabs.

Existing suite (`test_mainwindow_startup.py`) keeps passing after the `_add_client` signature
update; run `pytest -q` offscreen (`QT_QPA_PLATFORM=offscreen`, already the conftest default).

## Docs

- `docs/source/index.rst`: update the widget-selection paragraph (registry + automatic tab pages),
  document main vs. sidebar widgets and the new `widgets:`/`sidebar:` contract (label, icon,
  interface, overwrite), keep the example semantics accurate.
- This plan is indexed in `pyobs-gui/specs/index.md`; mark `Status: implemented` with the PR when
  landed.

## Implementation checklist

- [ ] Add `MainWidgetEntry` + `MAIN_WIDGETS` registry (D1); delete `DEFAULT_WIDGETS`,
      `DEFAULT_ICONS`, and dead `DEFAULT_CONFIG`; fix `IMode`/`IFilters` data
- [ ] Add `collect_main_widgets(matchable, custom)` helper with D3 merge/overwrite semantics
- [ ] Add `ModulePage` container: tabs + shared sidebar column, `add_to_sidebar`/`discard`/
      `get_fits_headers`, hide-empty-sidebar (D2)
- [ ] Rework `_client_connected`/`_add_client`/`_open_client`: collect all, host-upfront,
      gather-open with per-tab failure handling (D5), sidebar fill application
- [ ] Move sidebar fills out of `CameraWidget.open()`/`TelescopeWidget.open()` into
      `sidebar_fills` class attributes; delete old fill blocks
- [ ] Update `_client_disconnected` / `discard_all_widgets` verification for host pages
      (should be a no-op change, verify)
- [ ] Update `ModuleWindow.open()` (`modulegui.py:24-36`) to use the shared helper + assembly
- [ ] Update `tests/test_mainwindow_startup.py` for the `_add_client` signature; add
      `tests/test_multiwidget_pages.py` (see Test plan)
- [ ] Update `docs/source/index.rst`; index this plan in `specs/index.md`
- [ ] Manual smoke: GUI against a fixture module implementing `ICamera` + `IFocuser` (and
      `ITelescope` + `IFocuser`): tabs switch, sidebar persists, per-tab state is live, disconnect
      leaves no ghost page
