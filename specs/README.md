# Design/planning docs

This repo has no `specs/` structure of its own. Design docs, implementation plans, and ADRs that
concern `pyobs-gui` — including ones actually implemented here — live in `pyobs-core`'s `specs/`
tree instead (`specs/design/`, `specs/plans/`, `specs/adrs/`), each tagged with a `Repos:` line
naming every repo it concerns. See `pyobs-core/CLAUDE.md`'s "Cross-repo docs" section.

Relevant so far:

- `pyobs-core/specs/plans/gui-interactive-login.md` — interactive login/settings dialog to replace
  the current YAML-config-file requirement.
- `pyobs-core/specs/plans/pyobs_2_0_work_plan.md` — the `IRunning.is_running()` removal item
  required updating `mainwindow.py`'s two RPC calls to that method to read `IRunning`'s pushed
  state instead.
