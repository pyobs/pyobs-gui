# Plan: scrollable fallback around each module page, instead of a hard window-width floor

Status: implemented (pyobs-gui `develop`, 2026-09-14) — `mainwindow.ui`'s `stackedWidget` wrapped
in `stackedWidgetScroll` as designed below. Risk #1 (wheel-over-spinbox) confirmed real via a
headless test (an unfocused `QDoubleSpinBox`'s value changed from a wheel event before the fix),
not just theoretical — fixed with `pyobs_gui/nowheelfilter.py`'s `NoWheelWhenUnfocused`, an
app-wide event filter installed in `GUI.new_event_loop()`. Risks #2/#3 spot-checked (camera page
at 700x400: renders correctly, horizontal scrollbar appears exactly where expected, no visual
corruption); not exhaustively swept across every widget type in the fleet.

## Problem

Today, `MainWindow`'s minimum window size is the sum of every currently-visible column's own
minimum: the nav list (`listPages`), the current `ModulePage`'s content, and (since
`2026-09-14-...` — see `../pyobs-core/specs/steering/fleet-open-items.md`) that page's sidebar,
once it has one. There's no fallback once that sum is too wide for the screen or the user's
preference — the window simply refuses to shrink further (or, before this session's sidebar fix,
silently clipped sidebar text below its real minimum instead of enforcing it, which was worse).

Individual floors have been found and fixed one at a time this session: `TelescopeWidget`'s
`QStackedWidget` sizing to its widest page, three `QFormLayout`s not wrapping long rows, the
sidebar's missing minimum width. `qfitswidget`'s Cuts/Stretch/Colormap toolbar row is a further,
still-open one (`2026-09-14-fitswidget-toolbar-overflow.md`). Each fix is worth doing on its own
merits, but there's no reason to believe these are the last ones — any future widget, or any page
nobody's specifically shrunk-tested yet, can reintroduce the same class of problem. There's
currently no general safety net; every instance has to be found and fixed individually.

## Design

Wrap `stackedWidget` (`pyobs_gui/qt/mainwindow.ui`, inside `splitterToolBox`, itself inside
`splitterLog` inside `splitterNav`'s second pane — currently the only widget in that splitter
pane) in a `QScrollArea`:

- `setWidgetResizable(True)` — the standard widget fills the viewport as long as the viewport is
  bigger than its `minimumSizeHint()`; once the viewport shrinks below that, Qt clamps the widget
  at its minimum and the scroll area's own scrollbars take over. This is exactly "scrollbars only
  once content can't shrink further" — built-in `QScrollArea` behavior, not something to hand-roll
  (same mechanism as the sidebar fix, just with scrollbars enabled instead of a hard minimum).
- Both `horizontalScrollBarPolicy` and `verticalScrollBarPolicy` at `ScrollBarAsNeeded` (unlike the
  sidebar's own scroll area, which deliberately keeps horizontal scrolling off in favor of a hard
  minimum — see `mainwindow.py`'s `ModulePage.__init__`). The two pages made different tradeoffs on
  purpose: the sidebar is one, well-known, bounded piece of content (capped at 320px) where "always
  fully legible, never scrollable" was worth a hard floor; the main content area hosts every
  current and future module widget, with no such bound, so a safety net beats a floor here.

No change to any individual widget's own `minimumSizeHint()` — this doesn't replace the per-widget
fixes already landed or planned, it catches whatever they don't (or haven't yet).

## Known risks to verify before shipping

1. **Mouse wheel over an embedded combo/spin box inside a `QScrollArea` is a known Qt papercut**:
   it often scrolls the outer view instead of changing the control's value, unless the control has
   keyboard focus. Needs checking against representative widgets with lots of spin/combo boxes
   (`TelescopeWidget`'s offset fields, `CameraWidget`'s Binning/ExpTime) before this ships. If it's
   a real problem, the standard fix is an event filter that ignores wheel events on a spin/combo
   box that doesn't have focus — `QAbstractSpinBox`/`QComboBox` both support `setFocusPolicy` +
   filtering `QEvent.Wheel`; a small reusable helper rather than a per-widget patch.
2. **App-wide, not scoped to known-bad pages.** Every `ModulePage` becomes potentially scrollable,
   including ones nobody's had a reason to shrink-test. Needs a visual pass across the different
   widget shapes in the fleet -- tables (`FitsHeadersWidget`), plots (`qfitswidget`), and the video
   widget in particular, since a live-updating display widget that expects to fill its allocated
   space might render oddly once "allocated space" can be smaller than it wants and scrolling is
   the answer instead of shrinking.
3. **Interaction with `MainWindow.resizeEvent`'s forced `splitterNav.setSizes()`** (`mainwindow.py`
   `_on_nav_splitter_moved`/`resizeEvent`, re-asserts the nav pane's remembered width on every
   resize, handing the second pane whatever's left). That second pane can already end up narrower
   than its content's minimum today (the exact scenario the sidebar fix addressed for one specific
   sub-widget) -- this plan turns "narrower than minimum" from "silently break" into "scroll",
   which is strictly better, but should be verified against this specific forced-resize path rather
   than assumed.

## Relationship to existing plans

- Makes `2026-07-29-gui-telescopewidget-layout.md`'s fix #4 (resize-driven reparenting into a
  narrow/wide layout at a breakpoint) unnecessary — that plan already flagged #4 as "only worth
  doing if (1)-(3) don't get the floor low enough," and a scroll fallback is a lower-effort way to
  handle whatever's left over than hand-built breakpoint reflow. Cross-link, not a rewrite: update
  that plan's own status once this one actually lands, rather than editing it preemptively now.
- Complementary to, not a replacement for, `2026-09-14-fitswidget-toolbar-overflow.md` and any
  future per-widget floor fix -- this is the net under the tightrope, not a reason to stop
  tightening it.

## Rollout

Pure `pyobs-gui` change (`mainwindow.ui` + whatever `mainwindow.py` wiring the new scroll area
needs, e.g. wheel-event filtering if risk #1 turns out to be real). No public API change, no new
dependency. Rollback is reverting the `.ui`/`.py` diff.
