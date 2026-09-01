# Plan: split `VideoWidget` into a main widget + paired sidebar widget

Status: draft

Dependency landed 2026-09-01: `2026-08-28-gui-main-vs-sidebar-widgets.md` merged to develop as
PR #157 (`b7a14a6`), including the `paired_sidebar_widget` field and wiring — unblocked.

Depends on `2026-08-28-gui-main-vs-sidebar-widgets.md` (specifically its 2026-09-01 revision,
D6 — the `MainWidgetEntry.paired_sidebar_widget` field and `MAIN_WIDGETS`/`collect_main_widgets`/
`ModulePage` mechanism) landing first. This plan is that mechanism's first concrete consumer, and
finishes the part of D6 the base plan deliberately left undone (actually instantiating and wiring
a `paired_sidebar_widget` — the base plan only adds the registry field and a no-op-until-used code
path).

## Motivation

pyobs-gui#150 / the base plan's D6 proposes `paired_sidebar_widget`: an interface backed by two
widget classes that always render together — a main-content one and a permanently-paired sidebar
one — as opposed to the cross-interface, promotable `sidebar_preferred` case (D1). `VideoWidget`
is the natural first candidate: today `videowidget.py` combines the MJPEG live-view display with a
full set of exposure controls (image type, exposure time, gain, grab/abort, count, broadcast) in
one class. Splitting it means the live view becomes the main tab content and the controls become a
permanent sidebar block next to it — freeing up screen space for the video and mirroring how
`CameraWidget` already keeps its own controls next to (not on top of) its preview.

The base plan deferred this because it isn't pure registry wiring: the two halves currently share
instance state directly inside one class, and splitting them means that coupling has to cross a
widget boundary.

## Generic wiring this plan adds to the assembly helper

The base plan's `collect_main_widgets`/`_open_client` assembly (D6) adds a `paired_sidebar_widget`
entry's widget to the sidebar unconditionally when its main entry survives into `main`, but
doesn't yet give the two widget instances a way to talk to each other. Add, at the point both
instances are constructed (synchronous `create_widget()` calls, before either's async
`open()`/`_init()` runs):

```python
if entry.paired_sidebar_widget is not None:
    sidebar_widget = create_widget(entry.paired_sidebar_widget, module=client)
    main_widget.paired_sidebar = sidebar_widget   # type: ignore[attr-defined] -- set by
    sidebar_widget.paired_main = main_widget      # convention, not a BaseWidget field; each pair
                                                   # declares its own typed attribute (see below)
    host.add_to_sidebar(sidebar_widget)
```

Plain attribute assignment, not a `link_paired_sidebar()` override hook — simplest thing that
works, and avoids inventing base-class API surface for a mechanism with exactly one consumer so
far. `VideoWidget`/`VideoControlsWidget` each declare their own typed `Optional[...]` attribute
(see State split below) rather than relying on `BaseWidget` to know about pairing at all.

## State split

| Stays in `VideoWidget` (main) | Moves to `VideoControlsWidget` (paired sidebar) |
|---|---|
| `widgetLiveView`/`frameLiveView`, MJPEG socket plumbing (`_received_data`, `_showEvent`, `hideEvent`, `_on_ssl_errors`) — unchanged | `groupExposure`, `groupGain`, `comboImageType`, `labelImageType`, `buttonGrabImage`, `buttonAbort`, `spinCount`, `checkBroadcast`, `labelExposuresLeft`, `spinExpTime`, `spinGain` |
| `datadisplay` open/`grab_data()` | `_init()`'s `has_image_type`/`has_exposure_time`/`has_gain` visibility checks (`videowidget.py:114-122`) |
| `exposures_left`, exposure loop (`_grab_image`, `_expose_task_func`, `abort_sequence` → renamed `abort()`) | state subscriptions + handlers for `IExposureTime`/`IGain`/`IImageType` (`videowidget.py:175-180, 185-192`) |
| new public API: `start_exposures(count, broadcast, image_type)` (old `grab_image()` body minus reading the now-relocated spin/combo/checkbox values) and `abort()` | `exposure_time_changed`/`gain_changed` (`videowidget.py:331-353`) — unaffected logic, just relocated; each still calls `self.comm` directly |
| new `exposures_left_changed = Signal(int)`, emitted wherever `signal_update_gui.emit()` fired for exposure-count changes | grab/abort button handlers call `self.paired_main.start_exposures(...)`/`self.paired_main.abort()`; connects to `self.paired_main.exposures_left_changed` in its own `_init()` to drive `labelExposuresLeft` text and `buttonAbort.setEnabled(...)` |
| `paired_sidebar: Optional["VideoControlsWidget"]` | `paired_main: Optional["VideoWidget"]` |

`self._interfaces` (currently fetched once in `VideoWidget._init()` and reused by both the grab
loop and the visibility checks) is **not** shared — each widget independently calls
`self.comm.get_interfaces(self.module)` in its own `_init()`. It's a single cheap RPC call; sharing
it would mean ordering `_init()` between the two widgets, for no real savings.

## Steps

1. Confirm `2026-08-28-gui-main-vs-sidebar-widgets.md` has landed (registry + `collect_main_widgets`
   + `ModulePage` exist, including its 2026-09-01 revision).
2. Add the generic `paired_sidebar_widget` instantiation/wiring to `_open_client` (see above) —
   this is shared infrastructure, do it as its own commit so it's separately reviewable from the
   `VideoWidget`-specific split.
3. New `pyobs_gui/videocontrolswidget.ui` + `pyobs_gui/qt/videocontrolswidget_ui.py`: move the
   controls widgets (see State split table) out of `videowidget.ui` into a new form. Keep
   `frameLiveView` and nothing else in `videowidget.ui`.
4. New `pyobs_gui/videocontrolswidget.py` (`VideoControlsWidget(BaseWidget, Ui_VideoControlsWidget)`):
   move the control-side logic per the table. `_init()` no-ops safely if `self.paired_main` is
   `None` (shouldn't happen via the assembly helper, but standalone construction — e.g. in a test —
   must not crash).
5. Trim `pyobs_gui/videowidget.py` down to the main-widget half per the table; add
   `start_exposures()`/`abort()`/`exposures_left_changed`.
6. Register the pairing in `mainwindow.py`'s `MAIN_WIDGETS`:
   `MainWidgetEntry(IVideo, VideoWidget, "Video", "fa5s.video",
   paired_sidebar_widget=VideoControlsWidget)`.
7. Update `get_fits_headers()` if `VideoControlsWidget` or `VideoWidget` publish any FITS header
   entries today — check both classes for `get_fits_headers` overrides before assuming this is a
   no-op.
8. Tests: offscreen pytest fixture with an `IVideo`-only module — confirm the page shows the live
   view with no controls, the sidebar shows the controls, clicking "Grab" in the sidebar starts an
   exposure sequence visible on the main widget, and disconnecting discards both halves (no leaked
   comm handlers on either side).
9. Manual verification against a real/dummy video-capable module: confirm the live stream still
   renders, exposure time/gain/image-type controls still reflect published state changes, grab/
   abort still work end-to-end, and the "N exposure(s) left" label updates during a sequence.
10. `ruff` + `pyrefly` on all touched/new files.

## File changes

- New: `pyobs_gui/videocontrolswidget.py`, `pyobs_gui/qt/videocontrolswidget.ui`,
  `pyobs_gui/qt/videocontrolswidget_ui.py`.
- `pyobs_gui/videowidget.py` — trimmed to the main-widget half; new public API.
- `pyobs_gui/qt/videowidget.ui` — controls removed, `frameLiveView` only.
- `pyobs_gui/mainwindow.py` — `MAIN_WIDGETS` entry gains `paired_sidebar_widget`; `_open_client`
  gains the generic wiring from "Generic wiring" above.
- `tests/` — new coverage per step 8.
