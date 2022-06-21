#!/bin/bash
for f in *widget.ui; do
  echo "Processing $f file.."
  pyuic5 --import-from=. "$f" | sed -E "s/(from (.*widget))/from \.\.\2/"  > "${f%.ui}_ui.py"
done
pyuic5 --import-from=. mainwindow.ui > mainwindow.py
pyrcc5 resources.qrc > resources_rc.py