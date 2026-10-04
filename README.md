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


Standalone binary (experimental)
--------------------------------
`pysidedeploy.spec` builds a standalone Linux binary with Nuitka (about 760 MB, 20 minutes on 16 cores,
needs gcc and ccache or clang). Build it from a clean, non-editable install, otherwise Nuitka cannot map
the `pyobs-gui` distribution to its package and aborts:

    uv sync --no-dev
    uv pip install --reinstall --no-deps .
    uv pip install pip "Nuitka==4.0" patchelf
    PATH="$PWD/.venv/bin:$PATH" pyside6-deploy -c pysidedeploy.spec --force -f

The result is `dist/pyobs-gui.dist/pyobs_gui.bin`. Known issue: astropy's cds/ogip/vounit unit parsers do not
work in the compiled binary (see `pyobs_gui/_nuitka_astropy_patch.py`), so those formats log a `UnitsWarning`.
