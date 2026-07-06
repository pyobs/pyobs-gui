# Navbar keyboard shortcuts

**Status:** design proposal, not yet implemented.

## Motivation

The module sidebar (`listPages` in `pyobs_gui/mainwindow.py`) is mouse-only today. As more
modules connect, switching pages means scrolling/scanning a growing list. Strategy games solve
the analogous "many things, pick one fast" problem with control groups: select something, hit
a modifier+number to bind it to slot `N`, then a (lighter) modifier+number always jumps back to
it. This doc proposes the same scheme for the navbar.

## Key scheme

All shortcuts always require at least `Ctrl`, deliberately — see "Why Ctrl always, not bare
digits" below.

- **Fixed, non-reassignable**: `Ctrl+1` = Shell, `Ctrl+2` = Events, `Ctrl+3` = Status. These are
  the three always-present "Tools" pages (each individually optional via the `show_shell`/
  `show_events`/`show_status` constructor flags). If a page wasn't created, its key simply does
  nothing.
- **User-assignable**: `4, 5, 6, 7, 8, 9, 0` (7 slots). While any page is selected in the navbar,
  `Ctrl+Alt+N` binds that page to slot `N`. Afterwards, pressing `Ctrl+N` switches to whichever
  page is currently bound to slot `N`. Rebinding (`Ctrl+Alt+N` while a different page is selected)
  silently overwrites the previous binding for that slot — no confirmation, matching game
  convention. Binding a Tools page is allowed too (e.g. `Ctrl+Alt+4` while "Shell" is selected just
  means both `Ctrl+1` and `Ctrl+4` now go to Shell) — no special-casing needed.
- **Session-only**: bindings live only in memory for the lifetime of the running `MainWindow`;
  nothing is persisted to disk. No settings-persistence mechanism (`QSettings` or otherwise)
  exists anywhere in pyobs-gui today, and none is needed for this.

## Why `Ctrl` always, not bare digits

An earlier version of this design used bare digit keys (`4` to recall, `Ctrl+4` to bind), and an
empirical test (see the git history of this doc / prior discussion) confirmed that actually works
correctly for every widget checked (`QLineEdit`, `QSpinBox`, `QListWidget`'s own type-ahead search,
`QPushButton`) — Qt's `QEvent.Type.ShortcutOverride` mechanism means text/numeric-entry widgets
already claim digit keypresses for themselves before shortcut dispatch runs. But that guarantee is
per-widget-type and was only checked for the widget types known to exist in this app today; a
future or third-party custom widget could plausibly bind raw digit keys for its own purpose
without implementing that protection correctly. Requiring `Ctrl` (or `Ctrl+Alt`) sidesteps the
question entirely: no text-entry or numeric-entry widget anywhere treats `Ctrl+3` as "type a 3",
so there is nothing to verify per-widget — the guarantee is structural, not empirical. The
tradeoff is one extra key for recall (`Ctrl+N` instead of bare `N`), which still fits the
strategy-game feel closely enough.

## State

```python
# module-level, next to the existing _PAGE_ORDER
_FIXED_SHORTCUTS: Dict[str, str] = {"1": "Shell", "2": "Events", "3": "Status"}
_ASSIGNABLE_SLOTS: List[str] = ["4", "5", "6", "7", "8", "9", "0"]
```

```python
# in __init__, near the existing self._widgets: Dict[str, QtWidgets.QWidget] = {}
self._slot_bindings: Dict[str, str] = {}   # e.g. {"4": "camera", "0": "Status"}
```

Keys are the literal key-character strings (`"4"`, `"0"`, …), not ints — avoids ambiguity around
slot `"0"` and lets `QKeySequence(digit)` / `QKeySequence(f"Ctrl+{digit}")` be built directly from
the same string.

## Binding is by page name, not by widget or list-item instance

Module pages are dynamic — they appear when a module connects (`ModuleOpenedEvent` ->
`_client_connected`) and disappear when it disconnects (`ModuleClosedEvent` ->
`_client_disconnected`). Storing `self._slot_bindings` as slot -> page *name* rather than a
widget/item reference means a module that disconnects and reconnects later in the same session
automatically keeps its old binding: `_client_disconnected` deletes `self._widgets[client]` but
never touches `self._slot_bindings`, so `_recall_slot` for that slot just sees its bound name is
no longer in `self._widgets` and silently no-ops; on reconnect, `_client_connected` repopulates
`self._widgets[client]` under the same name and the old binding "comes back to life" with zero
extra bookkeeping. **No changes needed to `_client_connected`/`_client_disconnected` at all.**

## Visual badge — a true superscript digit, via a custom item delegate

The user wants a persistent, colored badge next to the name, in actual math-exponent style: a
small digit raised above the baseline right after the name (e.g. "camera" with a tiny raised `4`)
— not a literal caret character.

Unicode has dedicated superscript-digit glyphs (`⁰ ¹ ² ³ ⁴ ⁵ ⁶ ⁷ ⁸ ⁹`, U+2070/U+00B9/U+00B2/U+00B3/
U+2074–U+2079) that render small and raised in virtually every font already — no manual
baseline-shifting or font-size math needed, `painter.drawText()` with the right glyph just works:

```python
_SUPERSCRIPT_DIGITS = {"0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
                        "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹"}
```

`QListWidgetItem.text()` is currently overloaded as *both* the displayed label and the canonical
identity key used everywhere (`_change_page`'s `client = item.text()` lookup into `self._widgets`,
`_client_disconnected`'s text-scan removal, `PagesListWidgetItem.__lt__`'s text-based sort).
Baking the superscript glyph into `.text()` itself would require refactoring all of those to a
separate `UserRole`-based identity key first. A `QStyledItemDelegate` avoids that refactor
entirely: paint the glyph as an overlay at render time, while `.text()` stays exactly what it is
today (the plain name, still the canonical identity key everywhere).

```python
class NavPageItemDelegate(QtWidgets.QStyledItemDelegate):
    """Paints listPages rows normally, then overlays a small colored superscript digit right
    after the name for any page currently bound to a slot. Reads slot_bindings live (not a
    snapshot), so it always reflects the latest bindings without needing to be reconstructed."""

    def __init__(self, slot_bindings: Dict[str, str], parent: QtCore.QObject | None = None):
        super().__init__(parent)
        self._slot_bindings = slot_bindings  # same dict instance MainWindow mutates

    def paint(self, painter: QtGui.QPainter, option: QtWidgets.QStyleOptionViewItem, index: QtCore.QModelIndex) -> None:
        super().paint(painter, option, index)  # unchanged icon + name + selection rendering

        name = index.data(QtCore.Qt.ItemDataRole.DisplayRole)
        slot = next((s for s, bound_name in self._slot_bindings.items() if bound_name == name), None)
        if slot is None:
            return

        # position the glyph just after the rendered name, in an accent color
        fm = option.fontMetrics
        icon_w = option.decorationSize.width() + 4 if index.data(QtCore.Qt.ItemDataRole.DecorationRole) is not None else 0
        text_x = option.rect.left() + icon_w + 4
        text_w = fm.horizontalAdvance(name)

        painter.save()
        painter.setFont(option.font)  # the glyph is already small/raised; no font-size change needed
        painter.setPen(option.palette.color(QtGui.QPalette.ColorRole.Highlight))
        painter.drawText(
            QtCore.QRect(text_x + text_w + 1, option.rect.top(), 20, option.rect.height()),
            QtCore.Qt.AlignmentFlag.AlignVCenter,
            _SUPERSCRIPT_DIGITS[slot],
        )
        painter.restore()
```

Install once in `__init__`, after `setupUi`:

```python
self.listPages.setItemDelegate(NavPageItemDelegate(self._slot_bindings, self))
```

Since the delegate holds a reference to the *same* `self._slot_bindings` dict `_bind_slot` mutates
(not a copy), no extra syncing is needed — but Qt still needs to be told to repaint after a
binding changes, since nothing else triggers that automatically. Add one line to `_bind_slot`:

```python
self.listPages.viewport().update()
```

The exact badge offset in the sketch above (icon width + fixed spacing) is a starting point, not
pixel-final — expect to tune it visually once implemented (see verification). Color uses the
palette's `Highlight` role so it adapts to the active Qt theme instead of a hardcoded color. The
status-bar toast in `_bind_slot` (see below) stays as a complementary "just happened" confirmation
alongside the persistent badge.

## Shortcut wiring

17 `QShortcut` objects total (`QtGui.QShortcut`/`QtGui.QKeySequence` — **not** `QtWidgets`, that's
a Qt5-ism), created once in `__init__` via a new `self._setup_shortcuts()` call (after `setupUi`
and the new state above): 3 fixed (`Ctrl+1/2/3`) + 7 `Ctrl+N` recall + 7 `Ctrl+Alt+N` bind. Each is
a long-lived object whose handler does a *dynamic* lookup at press-time — module pages come and
go, but slot numbers are fixed for the app's lifetime, so shortcuts are never recreated.

```python
def _setup_shortcuts(self) -> None:
    self._shortcuts: List[QtGui.QShortcut] = []

    for key, name in _FIXED_SHORTCUTS.items():
        sc = QtGui.QShortcut(QtGui.QKeySequence(f"Ctrl+{key}"), self)
        sc.activated.connect(lambda name=name: self._go_to_page(name))
        self._shortcuts.append(sc)

    for slot in _ASSIGNABLE_SLOTS:
        recall = QtGui.QShortcut(QtGui.QKeySequence(f"Ctrl+{slot}"), self)
        recall.activated.connect(lambda slot=slot: self._recall_slot(slot))
        self._shortcuts.append(recall)

        bind = QtGui.QShortcut(QtGui.QKeySequence(f"Ctrl+Alt+{slot}"), self)
        bind.activated.connect(lambda slot=slot: self._bind_slot(slot))
        self._shortcuts.append(bind)
```

**Gotcha**: the `slot=slot`/`name=name` default-argument capture is required — without it, every
lambda in the loop closes over the same loop variable and all shortcuts end up firing for the
*last* value (`"0"`). `self._shortcuts` is kept mainly so the objects are inspectable/debuggable;
Qt's parent-child ownership (`self` as parent) would keep them alive either way.

Default `QShortcut` context is `Qt.ShortcutContext.WindowShortcut` (fires whenever the window is
active, regardless of which child widget has focus) — exactly right here, no `setContext(...)`
needed.

```python
def _go_to_page(self, name: str) -> None:
    """Fixed Ctrl+1/2/3 handler. No-ops if the page was never created."""
    if name not in self._widgets:
        return
    self._select_page_by_name(name)

def _select_page_by_name(self, name: str) -> None:
    """Selects the listPages row for `name`; selection change drives the existing
    currentRowChanged -> _change_page path, so this never touches stackedWidget directly."""
    for row in range(self.listPages.count()):
        item = self.listPages.item(row)
        if item is not None and item.text() == name:
            self.listPages.setCurrentRow(row)
            return

def _bind_slot(self, slot: str) -> None:
    """Ctrl+Alt+N: binds the currently selected page to slot N, silently overwriting any
    previous binding for that slot."""
    item = self.listPages.currentItem()
    if item is None:
        return
    name = item.text()
    if name not in self._widgets:  # defensive; headers are NoItemFlags and unselectable anyway
        return
    self._slot_bindings[slot] = name
    self.statusBar().showMessage(f"Bound Ctrl+{slot} to '{name}'", 3000)

def _recall_slot(self, slot: str) -> None:
    """Ctrl+N: switches to whatever is bound to slot N. No-ops if unbound or disconnected."""
    name = self._slot_bindings.get(slot)
    if name is None or name not in self._widgets:
        return
    self._select_page_by_name(name)
```

Place these four methods right after `_change_page`, since they're the same "navbar page
switching" cluster.

**Conflict safety**: since every shortcut here requires at least `Ctrl`, there's no need for the
per-widget-type empirical verification a bare-digit scheme would need (see "Why Ctrl always,
not bare digits" above) — no text/numeric-entry widget anywhere treats `Ctrl+3` or `Ctrl+Alt+3`
as ordinary input, so this is safe by construction rather than by testing each widget type. Still
worth a quick manual sanity check after implementation (see Verification below), mainly to confirm
nothing *else* in the app (e.g. a future custom widget) has already claimed one of these
combinations for something unrelated.

## File changes

Everything lives in `pyobs_gui/mainwindow.py` — new constants near `_PAGE_ORDER`, new
`self._slot_bindings` state and `self._setup_shortcuts()` call in `__init__`, and five new
methods (`_setup_shortcuts`, `_go_to_page`, `_select_page_by_name`, `_bind_slot`, `_recall_slot`).
No `.ui` changes.

## Verification (once implemented)

1. Start `test/full.yaml`. Confirm `Ctrl+1`/`Ctrl+2`/`Ctrl+3` jump to Shell/Events/Status. Confirm
   they no-op (no crash, no switch) when a page was disabled (e.g. `show_shell: false` in the YAML
   config).
2. Focus the Shell command-input line edit, type a command containing digits (e.g. `status 123`);
   confirm the digits appear as typed text and no page switch happens. Repeat with a numeric spin
   box (e.g. Camera's exposure time) — this should already be a non-issue given the `Ctrl`
   requirement, but worth a quick check anyway.
3. Select the "camera" page, press `Ctrl+Alt+4`; confirm the status-bar toast and the superscript
   badge appear, and that `Ctrl+4` returns to it from anywhere else in the app.
4. Stop the dummy camera module (triggers `ModuleClosedEvent`); confirm its nav entry disappears
   and pressing `Ctrl+4` does nothing (no exception). Reconnect it under the same name; confirm its
   nav entry reappears (badge included) and `Ctrl+4` immediately works again, with no need to
   re-press `Ctrl+Alt+4`.
5. With slot `4` still bound to "camera", select "telescope" and press `Ctrl+Alt+4`; confirm the
   toast shows the new binding with no confirmation prompt, the badge moves to "telescope", and
   `Ctrl+4` now goes to telescope.
6. ruff + pyrefly on `mainwindow.py`.
