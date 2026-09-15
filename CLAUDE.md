# CLAUDE.md

Entry points for working in this repo.

## What this is

`pyobs-gui` is a PySide6/Qt GUI for operating a whole `pyobs` system: one page per connected
module (camera, telescope, roof, focuser, ...), plus Shell/Events/Status tool pages. Run standalone
with interactive login (`uv run pyobs-gui`) or via the standard `pyobs` CLI with a config file
whose top-level class is `pyobs_gui.GUI` (see `docs/source/index.rst`).

## Design history and planning

This repo keeps its own implementation plans directly under `specs/` (`YYYY-MM-DD-<slug>.md`,
listed in `specs/index.md`), following the same conventions as `pyobs-core`'s `specs/` tree. Older
design docs, plans, and ADRs that concern `pyobs-gui` live in `pyobs-core`'s `specs/` tree instead,
tagged with a `Repos:` line — see `specs/index.md` for the current cross-repo list and
`pyobs-core/CLAUDE.md`'s "Cross-repo docs" section for the convention.

## Tooling

- Lint: `ruff` (config in `pyproject.toml`; excludes `pyobs_gui/qt/`)
- Format: `black`
- Type checking: `pyrefly` (`project-includes = ["pyobs_gui", "tests"]`; a `mypy.ini` also exists
  in the repo root but is not the active type checker — use `pyrefly`)
- Tests: `pytest` (`asyncio_mode = "strict"`)
