"""Standalone entry point for an interactive-login pyobs-gui -- bypasses the config-file-driven
`pyobs` CLI entirely. This is what a compiled binary (see
specs/plans/gui-widget-plugins-and-packaging.md) targets: no YAML config, no credentials on disk
unless the user opts into "store password" in the login window.
"""

from __future__ import annotations

from pyobs.application import Application

from .gui import GUI
from .login import login_and_build_gui


def main() -> None:
    app = Application(module_factory=login_and_build_gui, loop_module_class=GUI)
    app.run()


if __name__ == "__main__":
    main()
