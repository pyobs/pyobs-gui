# Plan: qfitswidget — responsive Cuts/Stretch/Colormap toolbar (hide + overflow, not wrap)

Status: implemented, closed — released in qfitswidget v1.1.3, `pyobs-gui`'s floor bumped to match
and released in v2.4.2. See "Implementation notes" below for the full list of real bugs found and
fixed during live verification (eight, not three), and one design change from what this doc
originally proposed (thresholds are measured at runtime, not hardcoded).

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

- ~~Exact `T1`/`T2`/`T3` pixel values~~ — resolved by not hardcoding them at all, see
  "Implementation notes" below.
- Does `resizeEvent` need debouncing, or is per-event evaluation (three cheap comparisons) fine
  as-is? Verified fine in practice, not revisited further.
- Any other `qfitswidget` consumer (outside `pyobs-gui`) that embeds `QFitsWidget` at a width this
  would ever actually engage at? Not checked — low-risk either way, since the new behavior is
  strictly additive (nothing disappears until the row genuinely doesn't fit).

## Implementation notes

**Design change from the original proposal**: rather than hardcoding `T1`/`T2`/`T3` pixel
constants picked once against a snapshot measurement (Tim's own objection, mid-implementation —
a hand-picked number silently drifts the moment font/DPI/style/label text changes), the thresholds
are derived once, at construction (`_measure_toolbar_tier_widths()`), by actually toggling each
tier's widgets and reading `horizontalLayout_3.sizeHint()` at each step. `resizeEvent` itself is
unchanged in shape from the original design — still three fixed-threshold comparisons per resize,
just against runtime-measured numbers instead of literals.

**Three real bugs found only by testing, not by reading the code**:

1. Restoring a widget from the overflow menu via `widget.setParent(...)` + `addWidget()` +
   `action.deleteLater()` left it a dangling C++ object (`libshiboken: ... already deleted` on the
   next access) — `QWidgetAction` retains internal ownership bookkeeping over a widget handed to
   `setDefaultWidget()` that a plain reparent doesn't release. Fixed with `QWidgetAction`'s own
   `releaseWidget()`, the documented mechanism for reclaiming a widget given to a menu/toolbar this
   way.
2. Even after that fix, restored widgets stayed invisible: `QLayout.addWidget()` reparents
   internally, and Qt's documented behavior is that reparenting always hides a widget as a side
   effect, regardless of a `setVisible(True)` call made *before* the reparent. Fixed by moving
   `setVisible(True)` to *after* `addWidget()`.
3. `resizeEvent` originally read `self.width()`; switched to `event.size().width()` — normally
   identical, but relying on `self.width()` made the logic impossible to unit-test with a
   directly-constructed `QResizeEvent` (found while writing the verification script, not a
   real-world bug, but `event.size()` is the more correct/robust source regardless).

All three confirmed via a headless script (`QT_QPA_PLATFORM=offscreen`, directly-constructed
`QResizeEvent`s to sidestep window-manager minimum-size clamping on a bare top-level widget):
full tier progression (900→550→420→350px) hides/overflows in the right order, restoring back to
900px brings everything back visible with state intact (a checkbox toggled *while* in the overflow
menu keeps its new value), and Tier 0 (manual cuts fields) correctly show only in "Custom" mode.

**Two more real bugs found in real-app testing** (not caught by the isolated tests above, since
neither involves anything other than `QFitsWidget` on its own):

4. **Chicken-and-egg deadlock once embedded in a resizable `QScrollArea`** (as it is in
   `pyobs-gui`, via `stackedWidgetScroll`): Qt decides whether to actually shrink a widget or just
   show a scrollbar instead based on `minimumSizeHint()`, *before* ever delivering a smaller
   `resizeEvent`. Without overriding it, the default reflects `horizontalLayout_3`'s *current*
   (uncompacted) children -- so the outer scroll area concludes "this needs ~600px", shows a
   scrollbar, and `resizeEvent` never actually receives a width small enough to trigger its own
   hide/overflow logic at all. Fixed by overriding `minimumSizeHint()` to report the
   fully-compacted floor (`_TOOLBAR_OVERFLOW_REVERSED_WIDTH`) as the width, not whatever the
   current visible state happens to need. Confirmed via a nested `QScrollArea` test mirroring the
   real embedding: without the override, the widget never shrinks below ~600px and a scrollbar
   appears immediately; with it, compaction runs first (labels hide, then trimsec overflows) and a
   scrollbar only appears once the true ~380px floor is actually reached.
5. **Flicker from missing hysteresis** (Tim, live-testing): a width sitting right at a tier
   boundary flips that tier's visibility on every resize event landing near it -- and real resize
   events do land within single-digit pixels of each other there, both from a live drag and from a
   follow-up resize event that reparenting itself can trigger. The plan above flagged this as a
   risk to add "only if it's a real problem, not preemptively" -- confirmed real. Fixed with a
   `_HYSTERESIS_MARGIN` (24px) dead zone: activating a tier still uses the plain threshold, but
   deactivating it requires clearing `threshold + margin`, not just crossing back over the same
   line. Verified synthetically: 30 alternations landing exactly at a boundary produced 1 state
   toggle instead of ~30.

6. **Widgets never returned when growing the window back, for real** (Tim, live-testing again):
   the `releaseWidget()` + `deleteLater()` fix for bug 1 above was verified in isolation
   (`verify_toolbar_overflow2.py`, which calls `resizeEvent()` directly, synchronously, once) but
   still crashed the same way in the real app. Root cause: that test never pumps the Qt event
   loop, so `action.deleteLater()`'s deferred deletion never actually runs within it -- the crash
   only shows up once a real event loop gets a chance to process that deletion (confirmed: adding
   `app.processEvents()` calls after a real `QScrollArea.resize()` reproduces it every time).
   Rather than chase the exact timing of `releaseWidget()` vs. deferred deletion further, sidestepped
   the question entirely: `_overflow_actions` now holds one `QWidgetAction` per overflow-able
   widget, created once in `__init__` and reused for the widget's whole lifetime -- `_set_overflow`
   only toggles the action's menu membership and the widget's `setDefaultWidget()`/layout parent,
   never deletes anything. Stress-tested with a real event loop: 7 shrink/grow cycles including a
   checkbox toggled *while* overflowed, no crash, state preserved correctly every time.
   **Meta-lesson**: every one of bugs 4-6 above was only caught because Tim kept testing the
   actual running app after each fix and reporting exactly what he still saw, not because the
   increasingly-elaborate headless tests found them first -- each headless test was faithful to
   what it modeled, but none of them modeled the specific thing (nested nested QScrollArea
   deciding scroll-vs-shrink, a live event loop actually processing a deferred deletion) that
   turned out to matter. Worth remembering next time a fix "passes its own test" but the person
   who asked for it says it still doesn't work: the test's fidelity is the first thing to doubt.
7. **Also found**: `uv run` auto-syncs the venv against `pyproject.toml`/`uv.lock` before every
   invocation, which silently reverted a manual `uv pip install -e ~/code/pyobs/qfitswidget` back
   to the pinned PyPI `1.1.2` release on every single relaunch -- meaning bugs 4 and 5's fixes
   were never actually running in the app during several rounds of "still broken" reports; the
   editable install was correct, but got undone before each test. Use
   `uv run --no-sync pyobs test/camera.yaml` (or any `uv run --no-sync ...`) when testing an
   editable-installed dependency locally; plain `uv run` will keep silently discarding it.

8. **Only `trimsec` ever overflowed, `reversed` never did** (Tim, live-testing again): a second,
   one-tier-deeper instance of bug 4's exact shape. `minimumSizeHint()` capped at
   `_TOOLBAR_OVERFLOW_REVERSED_WIDTH` -- but that's the *threshold* for overflowing `reversed`,
   measured with `reversed` still visible, not the width once it's hidden too. Using it as the
   floor told Qt this row could never get smaller than the point where `reversed` is still shown,
   so a resizeEvent narrow enough to overflow it was never delivered. Fixed by measuring a fourth,
   genuinely-fully-compacted width (`_TOOLBAR_FULLY_COMPACTED_WIDTH`, everything optional hidden)
   in `_measure_toolbar_tier_widths()` and using that -- not the reversed-threshold -- as
   `minimumSizeHint()`'s cap. Verified: full progression now reaches all four states in order
   (900→full, 500→labels hidden, 400→+trimsec overflowed, 300→+reversed also overflowed, widget
   clamped at its true floor, scrollbar only then) and restores correctly growing back.

`black` clean; `mypy --strict` shows the same 28 pre-existing errors as before this change (all in
unrelated matplotlib/numpy-typing code), zero new ones.

## Rollout

Pure `qfitswidget` change, no API break (nothing about `QFitsWidget`'s public surface changes,
only internal layout behavior). `pyobs-gui` picks it up via a normal dependency floor bump once
released — same pattern as prior `qfitswidget` bumps (e.g. `pyobs-gui`'s `1.1.1`→`1.1.2` floor bump
for the hover-overlay NaN-WCS fix). No `pyobs-gui` code change required by this plan itself.
