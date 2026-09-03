# `VideoWidget` split into two independent main widgets

Status: implemented, closed.

Dependency landed 2026-09-01: `2026-08-28-gui-main-vs-sidebar-widgets.md` merged to develop as
PR #157 (`b7a14a6`).

## What actually shipped (differs from the original draft below)

The original draft (kept below for history) planned to use the `paired_sidebar_widget` mechanism
from D6 of `2026-08-28-gui-main-vs-sidebar-widgets.md`: a live-view main widget permanently paired
with a `VideoControlsWidget` sidebar holding every control. That mechanism still exists in
`MainWidgetEntry`/`collect_main_widgets()`/`_open_client` (`mainwindow.py`), unused — nothing
implements it here.

What shipped instead: `VideoWidget` split into two fully independent main widgets, both matched on
`IVideo`, rendered as two separate tabs (`collect_main_widgets()` already renders every matching
main-role interface as its own tab, D2 — no new mechanism needed):

- `videowidget.py` (`VideoWidget`, tab "Live View"): the MJPEG live view (`widgetLiveView`,
  raw-socket plumbing) plus exposure-time/gain controls (`groupExposure`/`groupGain`) — unchanged
  from what was already the "Live View" tab's content inside the old combined widget.
- `videograbwidget.py` (new, `VideoGrabWidget`, tab "FITS Image"): image-type/count/broadcast
  controls, grab/abort buttons, "N exposure(s) left", and the FITS preview (`datadisplay`) —
  unchanged from what was already the "FITS Image" tab's content.

The controls were never moved anywhere — the split just promotes the two tabs that already existed
inside one `QTabWidget` into two independently-registered main widgets. Each keeps exactly the
state it already had (the live-view half never touched `exposures_left`; the grab half never
touched the socket), so there was no cross-widget state to migrate and no pairing mechanism needed.
`FitsHeadersWidget` (previously on the combined `VideoWidget` entry) moved to the `VideoGrabWidget`
entry, since headers only make sense once a FITS image exists.

**Known limitation, not fixed here**: two `MainWidgetEntry` rows now share the `IVideo` interface.
A custom `widgets:` config entry with `interface: IVideo` can only ever replace the *first* match
(`mainwindow.py`'s replace-in-place lookup keys on interface name, not registry position) — no
current config uses that combination, so it's noted in `mainwindow.py` rather than fixed.

**`pyobs_iagvt.widgets.diskdetectionwidget.WidgetVideoDiskDetection`** subclassed the old combined
`VideoWidget` and used pieces of *both* halves (`self.frame` for its "Detect Sun" checkbox,
`self.frame_2`/`self.datadisplay.data` for its fiberhole radio buttons and sun-detection input).
It wasn't wired into any `gui-iagvt.yaml`/config anywhere in the fleet (confirmed via a repo-wide
grep) — deleted outright (`pyobs-iagvt`) rather than split, along with its test.

**Not migrated, pre-existing and unrelated**: `_grab_image()`'s `IImageFormat` branch reads
`self.comboImageFormat.currentText()`, a widget that was never added to `videowidget.ui`/now
`videograbwidget.ui` — carried forward unchanged (with its existing `# type: ignore[attr-defined]`)
since it predates this split and no `IVideo`-implementing module in the fleet currently implements
`IImageFormat` to exercise it.

Files: `pyobs_gui/videowidget.py` (trimmed), `pyobs_gui/videograbwidget.py` (new),
`pyobs_gui/qt/videowidget.ui`/`videowidget_ui.py` (trimmed),
`pyobs_gui/qt/videograbwidget.ui`/`videograbwidget_ui.py` (new), `pyobs_gui/mainwindow.py`
(`MAIN_WIDGETS` gains the second `IVideo` row), `tests/test_videowidget.py` (trimmed to the
live-view tests), `tests/test_videograbwidget.py` (new, the grab-loop tests).

---

## Original draft (superseded by the above)

Depends on `2026-08-28-gui-main-vs-sidebar-widgets.md` (specifically its 2026-09-01 revision,
D6 — the `MainWidgetEntry.paired_sidebar_widget` field and `MAIN_WIDGETS`/`collect_main_widgets`/
`ModulePage` mechanism) landing first. This plan is that mechanism's first concrete consumer, and
finishes the part of D6 the base plan deliberately left undone (actually instantiating and wiring
a `paired_sidebar_widget` — the base plan only adds the registry field and a no-op-until-used code
path).

### Motivation

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

*(This turned out to be based on an incomplete read of `videowidget.ui`: the combined widget
already had two tabs — Live View and FITS Image — with controls already partitioned per tab and no
state shared between them. There was no coupling to cross a widget boundary once that was
understood, which is why the shipped design above doesn't need `paired_sidebar_widget` at all.)*

The rest of this section (generic wiring, state-split table, numbered steps, file-changes list) is
preserved only as a historical record of the original approach and no longer describes what's in
the repo — see "What actually shipped" above for the real state.
