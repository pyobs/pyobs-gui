#!/bin/bash
for f in *widget.ui; do
  echo "Processing $f file.."
  pyside6-uic --from-imports "$f" -o "${f%.ui}_ui.py"
done
pyside6-uic --from-imports mainwindow.ui > mainwindow_ui.py
pyside6-rcc resources.qrc > resources_rc.py