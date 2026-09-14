# Plan: qfitswidget — responsive Cuts/Stretch/Colormap toolbar (hide + overflow, not wrap)

Status: proposed

Repos: qfitswidget (all implementation here; surfaced from pyobs-gui work, see "Context" below)

## Context

Found while shrinking `pyobs-gui`'s `CameraWidget` page as far as it'll go (see
`2026-07-29-gui-telescopewidget-layout.md`'s sibling investigation, and
`../pyobs-core/specs/steering/fleet-open-items.md`'s 2026-09-14 entries): after fixing
`TelescopeWidget`'s own width floor and a `ModulePage` sidebar-clipping bug, `CameraWidget`'s
minimum width was still pinned at ~1052px. Traced (headless, `QT_QPA_PLATFORM=offscreen`,
`test/camera.yaml`) to `DataDisplayWidget.datadisplay` — a `qfitswidget.QFitsWidget` — reporting a
`minimumSizeHint()` of `(797, 184)`, entirely accounted for by one row:
`qfitswidget/qt/fitswidget.ui:146`'s `horizontalLayout_3`:

```
Cuts: [combo] [min spin] [max spin]   Stretch: [combo]   Colormap: [combo]   ☐reversed ☑trimsec
```

A single non-wrapping `QHBoxLayout` — nothing in `pyobs-gui` itself is responsible for this floor;
it's purely `qfitswidget`'s own toolbar row.

## Design: hide, then overflow — not wrap

Considered wrapping the row onto a second line (the same `WrapLongRows` fix already used for
`TelescopeWidget`'s form pages). Rejected for this specific row: unlike a control panel, this
toolbar sits directly above/below the image canvas, and this widget's whole job is showing that
image — stealing a row of height from it to avoid hiding a checkbox is the wrong trade here. Hide
+ overflow keeps the widget's height constant regardless of width.

### Tier 0 — always, not width-gated

The manual cuts min/max spin boxes are only meaningful when the Cuts combo is set to "Manual";
otherwise they're already shown disabled. Hide them whenever Cuts ≠ Manual, unconditionally — this
is a pure win independent of width, not a responsiveness measure.

### Tiers 1-3 — width-gated, checked in `resizeEvent`

Fixed pixel thresholds (`T1 > T2 > T3`, exact values TBD by testing against the real widget), each
one step narrower than the last:

1. **Width < T1**: hide the three labels (`labelCuts`, `labelStretch`, `labelColormap`). Nothing
   to preserve access to — add each hidden label's text as a tooltip on the combo it described, so
   the information isn't lost, just not always-on.
2. **Width < T2**: move `checkTrimsec` into the overflow menu (see below).
3. **Width < T3**: move `checkColormapReverse` into the overflow menu.

Reparenting back out of overflow happens in reverse tier order as width grows past each threshold
again. Hysteresis: use the same threshold both directions (no separate show/hide bands) unless
testing shows visible flicker right at a boundary — add a small dead zone only if that's a real
problem, not preemptively.

### Overflow button and menu

A small button (only visible once tier 2 or 3 has moved something into it) opens a `QMenu`. Hidden
widgets are embedded as **the actual live widget instances**, not copies: `QWidgetAction` +
`QWidgetAction.setDefaultWidget(widget)` puts a real, still-interactive `QCheckBox` inside the menu,
signal connections untouched. Reparenting is: remove from `horizontalLayout_3`, wrap in a
`QWidgetAction`, add to the overflow `QMenu`; and the reverse to bring it back. This is the
standard Qt mechanism for a toolbar overflow with real controls (vs. hand-rolling a popup `QFrame`
and re-implementing dismissal/keyboard nav `QMenu` already gives for free).

## Open questions

- Exact `T1`/`T2`/`T3` pixel values — pick against the real widget, not guessed in the abstract.
- Does `resizeEvent` need debouncing, or is per-event evaluation (three cheap comparisons) fine
  as-is? Likely fine; revisit only if profiling says otherwise.
- Any other `qfitswidget` consumer (outside `pyobs-gui`) that embeds `QFitsWidget` at a width this
  would ever actually engage at? If none, this is low-risk to ship without extra compat concern.

## Rollout

Pure `qfitswidget` change, no API break (nothing about `QFitsWidget`'s public surface changes,
only internal layout behavior). `pyobs-gui` picks it up via a normal dependency floor bump once
released — same pattern as prior `qfitswidget` bumps (e.g. `pyobs-gui`'s `1.1.1`→`1.1.2` floor bump
for the hover-overlay NaN-WCS fix). No `pyobs-gui` code change required by this plan itself.
