# Live view: MJPEG (server stretch) or raw stream (client stretch)

Status: in progress (issue #182). Server side: pyobs-core #926, released in pyobs-core v2.13.0
(design: pyobs-core `specs/design/basevideo-live-view.md`).

## Scope

- Per-camera choice of live-view mode in `VideoWidget`: **MJPEG** (default) or **Raw**.
- New "Live view" group in the left panel, under ExpTime/Gain: Mode, Stretch, Cuts, Lo, Hi,
  Quality (MJPEG only), Max rate (Raw only).
- Settings (mode + stretch/cuts/lo/hi/quality/max rate) remembered per camera module via
  `QSettings("pyobs", "pyobs-gui")`, key `liveview/<module>/...`.
- **Out of scope:** zoom/pan and the server-side crop (`x`/`y`/`w`/`h`) that goes with it. Follow-up
  issue.

## Design

- **Stream URLs** come from `VideoCapabilities` (`mjpeg`, `raw`), each opened through the VFS as an
  `HttpFile` to get URL and Authorization header (as today for MJPEG). If `raw` is `None`, the Raw
  entry is disabled in the Mode combo; if `mjpeg` is `None` but `raw` isn't, Raw is used.
- **Parsing** moves out of the widget into `pyobs_gui/livestream.py`: incremental, Qt-free parsers
  (`MjpegParser`, `RawParser`) fed with socket bytes, returning complete frames. Both strip and
  check the HTTP response header first; a non-200 status (e.g. 400 for bad parameters) is logged
  with the response body instead of silently showing nothing. The raw parser reads an exact byte
  count per part (from `DTYPE`/`NAXISn` in `X-Pyobs-Frame-Meta`), never scanning the binary
  payload for the boundary. HTTP/1.0 request stays (no chunked encoding).
- **MJPEG mode:** stretch settings go into the query string; any change reconnects.
- **Raw mode:** frames decoded and stretched with `pyobs.utils.stretch.stretch_to_uint8()` in a
  worker thread, latest-frame-wins (a frame arriving while one is being processed replaces the
  pending one). The last raw frame is kept, so changing stretch/cuts re-renders immediately without
  reconnecting. `max_rate` from the Max rate control.
- **Fit to widget:** both modes request a downsampled stream, factor
  `floor(min(full_w / view_w, full_h / view_h))` (at least 1), sent as `scale` (MJPEG) or `bin`
  (Raw). Floor, so the delivered image is never smaller than the view. Full frame size is learned
  from the first frame (`NAXISn * SWBIN` for raw, JPEG size × scale for MJPEG); a resize recomputes
  it (debounced) and reconnects only if the factor changed.
- **Cuts "auto"** omits `cuts` (MJPEG: module's configured default; Raw: `StretchParams` default,
  i.e. full for 8 bit, minmax otherwise). Lo/Hi only enabled for percentile/manual.

## Checklist

- [x] Bump `pyobs-core>=2.13.0`, update `uv.lock`
- [x] `livestream.py` parsers + tests
- [x] `videowidget.ui` group + regenerate `videowidget_ui.py`
- [x] `VideoWidget`: mode switching, query building, raw decode worker, fit factor, settings
- [x] Tests for `VideoWidget` (request building, mode switch, fit factor, raw render, settings)
- [x] Parsers checked against a live DummyVideo (MJPEG with stretch params, raw full and binned,
  400 on bad parameters)
- [ ] Manual GUI test with `test/video.yaml` (DummyVideo), both modes
- [ ] Follow-up issue for zoom + server-side crop

## Known problem (pyobs-core)

`stretch_to_uint8()` used to downsample (to float32) *before* resolving the cuts, so with `scale > 1`
`cuts=full` raised and the server closed the MJPEG stream, and "auto" on 8-bit data turned into
minmax. The same applied to the raw stream with `bin > 1`, whose meta didn't carry the original
dtype.

Fixed in pyobs-core: `stretch_to_uint8()`/`compute_cuts()` resolve the cuts from the input dtype, take
an optional `dtype` for already-binned data, and the raw meta carries `SRCDTYPE` (dtype before
binning). `render_raw()` passes `SRCDTYPE` through. Released in pyobs-core v2.13.4, which is the
floor here.
