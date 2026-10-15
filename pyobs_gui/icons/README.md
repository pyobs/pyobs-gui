# pyobs GUI icon

White observing monitor and crosshair on magenta (`#d63384`), following the fleet's
white-symbol-on-colour app icons. Original artwork created for pyobs-gui and
approved on 2026-10-15; distributed under this repository's MIT licence.

`pyobs-gui.svg` is the editable source. PNG exports cover 16, 24, 32, 48, 64,
128, 256 and 512 pixels. `pyobs-gui.png` is the 256-pixel notification icon;
`pyobs-gui.ico` contains 16 through 256-pixel renditions for Qt and Windows.

These files must remain ordinary package data: desktop-notifier and the Windows
shortcut require filesystem paths, rather than Qt resource URLs. Nuitka includes
them with `--include-package-data=pyobs_gui` in `pysidedeploy.spec`.
