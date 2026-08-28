# Plan: pyobs-gui — generic `IStructuredConfig` widget (schema-driven config form)

Status: proposed (issue #154)
Audited: 2026-08-28

## Problem

Modules implementing `IStructuredConfig` (pyobs-core ≥ 2.0) publish a `ConfigSchema` describing
their whole (possibly nested) config, push current values as `ConfigAppliedState`, and accept a
new config in one `set_config()` call. pyobs-gui has no widget for this at all: the only consumer
in the ecosystem, pyobs-iagvt's `FTS`, hand-rolls a file-picker + YAML + pydantic construction UI
(`pyobs_iagvt/widgets/ftswidget.py`) instead of rendering the published schema. Every future
adopter of `IStructuredConfig` would otherwise need another bespoke UI.

The schema is deliberately rich enough to drive a form: per field it carries `type`
(`str`/`int`/`float`/`bool`/`enum`/`object`), `unit` (`pyobs.utils.enums.Unit`), `options` (enum
choices), `default`, and `nested` (recursive `object` fields). It is auto-derived from the module
author's own dataclass (`dataclass_to_schema`) or pydantic model (`pydantic_to_schema`), so no
hand-maintained schema to drift.

## Current state (audited 2026-08-28)

- `pyobs-core/pyobs/interfaces/IStructuredConfig.py` — interface: `capabilities = ConfigSchema`,
  `state = ConfigAppliedState(config, time)`, RPC `set_config(config: dict[str, ConfigValue])`.
  Design: `pyobs-core/specs/design/istructuredconfig.md` (implemented, commits `374fb358`/
  `a07fb3f0`).
- `pyobs-core/pyobs/utils/config_schema.py` — `ConfigSchema`/`ConfigFieldSchema`,
  `dataclass_to_schema()`, `pydantic_to_schema()`. Unsupported field types raise `TypeError`
  deliberately ("silent fallbacks there are worse than a loud failure").
- `pyobs-core/pyobs/comm/comm.py:529` — `get_capabilities(module, interface)` returns the
  deserialized capabilities dataclass (no changes needed).
- `pyobs-core/pyobs/comm/comm.py:599` — `subscribe_state(module, interface, cb)` delivers the
  current state immediately on subscribe.
- `pyobs-gui/pyobs_gui/base.py` — `BaseWidget`: one-shot `_init()` (`:306-312`), `run_background()`
  + `show_remote_error()` (`:30-45, 373-392`), ACL `permitted()` (`:398-412`), READY-state
  disabling in `_update_loop` (`:344-371`).
- `pyobs-gui/pyobs_gui/mainwindow.py:54-67` — `DEFAULT_WIDGETS` first-match-wins;
  `pyobs-gui/pyobs_gui/modulegui.py:28-32` — standalone `ModuleWindow.open()` repeats the same
  loop.
- No widget in `pyobs_gui/` consumes `IStructuredConfig`; `grep` for
  `ConfigFieldSchema`/`dataclass_to_schema`/`pydantic_to_schema` finds consumers only inside
  pyobs-core.
- Tests run headless offscreen (`tests/conftest.py` sets `QT_QPA_PLATFORM=offscreen`, session
  `QApplication`); widget tests exist (`tests/test_camerawidget.py`, …).

## Design

### 1. New widget: `pyobs_gui/structuredconfigwidget.py` → `StructuredConfigWidget(BaseWidget)`

`_init()` (one-shot, memoized retry-safe per `BaseWidget` conventions):

1. Fetch `ConfigSchema` once via `self.comm.get_capabilities(self.module, IStructuredConfig)`
   (static per module — store it, never re-fetch) and build the editor tree.
2. `self.comm.subscribe_state(self.module, IStructuredConfig, self._update_state)` — immediate
   delivery of current `ConfigAppliedState`, then live updates.

**Field-type → editor mapping** (recursive; `type="object"` → `QGroupBox` + `QFormLayout`):

| Schema `type` | Editor | Notes |
|---|---|---|
| `str` | `QLineEdit` | |
| `int` | `QSpinBox` | |
| `float` | `QDoubleSpinBox` | `unit` → suffix (e.g. ` arcsec`), decimals from magnitude |
| `bool` | `QCheckBox` | |
| `enum` | `QComboBox` | items = `options`; payload uses the exact option strings |
| `object` + `nested` | `QGroupBox` + recursion | e.g. `setup`/`main` in the FTS config |
| `object` w/o `nested` | read-only placeholder | freeform pydantic `dict`; render, don't guess |

- **Defaults:** `ConfigFieldSchema.default` pre-fills editors before the first state arrives;
  state always wins afterwards.
- **Dirty tracking:** assemble the nested `dict[str, ConfigValue]` from the editors and compare
  against the last-applied `ConfigAppliedState.config`; "Apply" enabled only when the payload
  differs. "Reset" restores last-applied values into the editors.
- **Apply:** `self.run_background(...)` → `self.comm.proxy(self.module, IStructuredConfig)`
  `.set_config(payload)`; errors surface via the shared `show_remote_error` path. Apply disabled
  while in flight (`_enable_buttons`) and when `not self.permitted("set_config")` (ACLs).
- **Module not READY:** handled for free by `BaseWidget._update_loop` disabling the widget.
- **Lists:** `ConfigValue` allows `list[...]` on the wire but `ConfigFieldSchema` has no list type
  today — out of scope; if encountered, render the field disabled with a tooltip.

### 2. Registration & placement (see also pyobs-gui #150)

`DEFAULT_WIDGETS` is first-match-wins per module, so:

- Add `IStructuredConfig: StructuredConfigWidget` to `DEFAULT_WIDGETS` **after** the specialized
  interfaces (`ISpectrograph`, `ICamera`, …) so e.g. the FTS keeps its `SpectrographWidget` and
  the generic form is a fallback for modules without a bespoke widget.
- Add a `DEFAULT_ICONS` entry (e.g. `fa5s.cog`).
- FTS overlap: it ships a bespoke config UI inside its spectrograph page. Long-term the generic
  form could replace that block, or sit alongside it once #150 (automatic tab pages for
  multi-widget modules) lands. Write the widget as a plain `BaseWidget` so it works both as a main
  page and as a sidebar/tab component without rework.

### 3. Tests (`tests/`)

- Schema → editors: every field type maps to the right editor class; nesting, unit suffixes, enum
  options, defaults.
- Assemble: widget tree → payload dict round-trips against a known schema (unit-test against a
  small nested dataclass-derived `ConfigSchema`); fake comm proxy asserts `set_config` receives
  the expected payload.
- Dirty/Apply/Reset logic; Apply disabled when unchanged or not permitted; remote-error path
  shows the messagebox (follow `tests/test_camerawidget.py` patterns).

## Acceptance criteria

- Any `IStructuredConfig` module gets an editable nested form automatically — no per-module code.
- Values arrive from `ConfigAppliedState` immediately on open and track updates; defaults fill in
  until then.
- Apply sends the assembled dict via `set_config`, gated by ACL + module state, failures via the
  standard error path.
- FTS (pyobs-iagvt) unchanged; generic widget appears as fallback page for `IStructuredConfig`
  modules.

## Out of scope

- No pyobs-core changes (`ConfigSchema`/`ConfigFieldSchema`/`IStructuredConfig` frozen); no
  list-type rendering; no YAML import/export (possible follow-up).
- Not depending on #150 — but designed to slot into it later.
