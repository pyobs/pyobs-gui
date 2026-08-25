pyobs-gui
=========

This is a [pyobs](https://www.pyobs.org) GUI for operating the whole system: one page per
connected module (camera, telescope, roof, focuser, ...), plus Shell/Events/Status tool pages.


Install *pyobs-gui*
---------------------
Clone the repository:

    git clone https://github.com/pyobs/pyobs-gui.git
    cd pyobs-gui

Install it with [uv](https://docs.astral.sh/uv/):

    uv sync


Running
-------
Two ways to start it:

- `uv run pyobs-gui` — standalone, interactive login. No YAML config needed; it prompts for XMPP
  credentials (with an optional "store password") and connects directly.
- `uv run pyobs <config.yaml>` — the standard `pyobs` CLI, driven by a config file whose top-level
  class is `pyobs_gui.GUI` (see `docs/source/index.rst` for a full example, including how to wire
  in a custom widget for a module).
