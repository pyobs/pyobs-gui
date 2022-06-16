#!/bin/bash
for f in *widget.ui; do
  echo "Processing $f file.."
  pyuic5 --from-imports "$f" > "${f%.ui}_ui.py"
done
