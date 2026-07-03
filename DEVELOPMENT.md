# Development

Backlog of planned work for pyobs-gui. Newest/most important items at the top.

## pyobs-core 2.0 ACLs — hide/grey out actions an operator isn't permitted to use

`pyobs-core` 2.0 is adding per-module access control (see its own `DEVELOPMENT.md`,
[Access Control (ACLs)](https://github.com/pyobs/pyobs-core/blob/develop/DEVELOPMENT.md#access-control-acls))
— design only there so far, nothing implemented yet.

**Reactive handling already works today, no change needed here:** `BaseWidget._background_task`
(`pyobs_gui/base.py:271-277`) already catches `exc.PyObsError` generically around every RPC call
and routes it to `show_error` (`base.py:282-285`), a plain message box with the exception's text.
The designed `exc.ForbiddenError` is a `RemoteError` is a `PyObsError`, so a denied call already
surfaces as a normal error dialog — confirmed by reading the actual code, not assumed.

**Open, once `pyobs-core` lands `IModule.get_permitted_methods()` (its Phase 8, not yet
implemented):** widgets already have a disable/enable mechanism built for a different purpose —
`_enable_buttons.emit(disable, False)` / `w.setEnabled(enable)` (`base.py:268,287-289`) — currently
only used to disable buttons while their own background task is running. The natural fix is to
reuse the same mechanism for "not permitted," fetched once per widget alongside the
capabilities/state it already pulls from its target proxy at setup, rather than only finding out
via an error dialog after the operator clicks.
