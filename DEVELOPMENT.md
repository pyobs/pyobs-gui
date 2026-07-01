# Development

Backlog of planned work for pyobs-gui. Newest/most important items at the top.

## Status page: show more information per module

`StatusWidget` (`pyobs_gui/statuswidget.py`) currently shows a 3-column table:
module name, version, status. Extend it to show more per-module detail:

- **Name** — already shown (`self.comm.clients`).
- **Version** — already shown, read once via `comm.get_capabilities(module, IModule)`.
- **Interfaces** — list of interfaces the module implements. Available via
  `await comm.get_interfaces(module)`, returns `list[type[Interface]]`.
- **State** — already shown via `StatusItem`/`subscribe_presence`
  (`ModuleState`: `CLOSED`, `READY`, `ERROR`, `LOCAL`).
- **Status** — free-form status/error string, currently folded into the
  `StatusItem` label (e.g. `ERROR: <error_string>`). Consider splitting into
  its own column.
- **Capabilities** — `comm.get_capabilities(module, interface)` per interface;
  decide which interfaces are worth querying and how to summarize the result
  (currently only used for `IModule.version`).

### Decision: expandable tree view

Replace `QTableWidget` with `QTreeWidget`. Top-level row per module keeps the
current 3 columns (Module, Version, Status — with `StatusItem` still living
in the Status cell via `setItemWidget`). Expanding a module row reveals one
child row per detail, each spanning all columns as plain text:

- `Interfaces: <comma-separated interface class names>` — from
  `await comm.get_interfaces(module)`, fetched once on module-open. Note:
  `Interface.version` (used internally to build the XMPP capabilities/state
  namespace) always comes from pyobs-gui's own locally installed
  `pyobs.interfaces` classes, never from the remote module — XMPP only sends
  interface *names* over the wire, and `_interface_names_to_classes` resolves
  those locally. So an interface-version mismatch between a module and
  pyobs-gui isn't detectable or displayable here; it would just show up as
  `get_capabilities`/`subscribe_state` silently returning nothing, which the
  error handling below already covers.
- `Capabilities (<Interface>): field=value, ...` — one child row per
  interface where `interface.capabilities is not None` (the `Interface` base
  class exposes `capabilities: ClassVar[type | None]`, so this is generic,
  not hardcoded per interface). Fetched once via
  `comm.get_capabilities(module, interface)` and formatted via
  `dataclasses.fields()`.
- `State (<Interface>): field=value, ...` — one child row per interface
  where `interface.state is not None`. Unlike capabilities this is live: use
  `comm.subscribe_state(module, interface, callback)` (delivers current value
  immediately, then pushes updates) and marshal the callback onto the Qt
  thread the same way `StatusItem.signal_presence` does today (callback ->
  `Signal.emit` -> slot sets the child item's text).

Sketch — `telescope` expanded, others collapsed:

```
┌─────────────────────────────┬─────────┬──────────────────────────────┐
│ Module                      │ Version │ Status                       │
├─────────────────────────────┼─────────┼──────────────────────────────┤
│ ▼ telescope                 │ 1.4.2   │ [ READY            ]         │
│     Interfaces: ITelescope, IMotion, IFocuser, IFilters               │
│     Capabilities (IFilters): filters=['clear', 'R', 'V', 'I']         │
│     State (IFilters): filter='clear', time=Time('2026-07-01T10:32')  │
│     State (ITelescope): ra=182.3, dec=45.1, focused=True              │
├─────────────────────────────┼─────────┼──────────────────────────────┤
│ ▶ camera1                   │ 2.0.1   │ [ READY            ]         │
├─────────────────────────────┼─────────┼──────────────────────────────┤
│ ▶ roof                      │ 1.1.0   │ [ ERROR: stuck     ] [Clear] │
├─────────────────────────────┼─────────┼──────────────────────────────┤
│ ▶ weather                   │ 0.9.3   │ [ OFFLINE          ]         │
└─────────────────────────────┴─────────┴──────────────────────────────┘
```

`▼`/`▶` are Qt's native tree expand/collapse arrows on the Module column — no
custom drawing needed. Version/Status columns are blank for child rows since
those items span all three columns (`setFirstColumnSpanned(True)`). The
Status cell keeps today's colored `StatusItem` widget (green/red/gray/yellow
background) exactly as-is. Child rows are flat — one level deep, not
themselves expandable.

### Decision: error handling

A module disconnecting mid-fetch (`get_interfaces`/`get_capabilities`/
`subscribe_state` racing a `ModuleClosedEvent`) is not an error worth
surfacing — wrap the per-module detail fetching in `_add_module` in a single
try/except, log at debug, and stop adding detail rows for that module. The
`_module_closed` handler already removes the row once the disconnect event
arrives, so there's nothing further to reconcile.

`_module_closed` does not need to unsubscribe state callbacks itself: `Comm`
already registers its own internal `_client_disconnected` handler for
`ModuleClosedEvent`, which pops `_state_subscriptions[sender]` and calls
`unsubscribe_state` for each one automatically (`comm.py:239-255`). So
`_module_closed` in `StatusWidget` only needs to remove the tree row, same as
today.