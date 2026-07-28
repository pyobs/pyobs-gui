"""Phase 0 spike for specs/plans/gui-widget-plugins-and-packaging.md.

Minimal, isolated PySide6 + qasync program, meant to be frozen with pyside6-deploy in
--mode=standalone, to answer three open questions before more is built on top of them:

1. Does pyside6-deploy/Nuitka even produce a working standalone binary for this app shape at all?
2. Does an external plugin directory (added to sys.path only at runtime, never seen by Nuitka's
   static analysis) still import correctly from inside the frozen binary?
3. Do qtawesome (icon fonts) and keyring (backend auto-discovery) survive freezing unmodified?

The plugin directory path is read from an environment variable at *runtime*, deliberately -- this
mirrors how the real plugin_paths config will work (known only once the binary actually runs, not
at build time), so Nuitka has no way to have bundled it even if it wanted to.

Non-interactive: does not call app.exec(). Writes results to spike_results.txt next to the
executable and to stdout, then exits.
"""

from __future__ import annotations

import os
import sys

results: dict[str, str] = {}

# --- PySide6 itself survives freezing (create early: qtawesome needs a live QApplication) ---
try:
    from PySide6 import QtWidgets

    app = QtWidgets.QApplication(sys.argv)
    results["pyside6_qapplication"] = "OK"
except Exception as e:
    app = None
    results["pyside6_qapplication"] = f"FAIL: {e!r}"

# --- plugin loading from a directory outside the build entirely ---
plugin_dir = os.environ.get("SPIKE_PLUGIN_DIR", "")
if plugin_dir:
    sys.path.insert(0, plugin_dir)

try:
    import my_plugin_widget

    results["plugin_import"] = f"OK: {my_plugin_widget.plugin_marker()}"
except Exception as e:
    results["plugin_import"] = f"FAIL: {e!r}"

# --- qtawesome icon fonts ---
try:
    import qtawesome as qta

    icon = qta.icon("fa5s.camera")
    results["qtawesome"] = "FAIL: icon isNull" if icon.isNull() else "OK"
except Exception as e:
    results["qtawesome"] = f"FAIL: {e!r}"

# --- keyring backend auto-discovery ---
try:
    import keyring
    import keyring.backend

    available = keyring.backend.get_all_keyring()
    available_str = ", ".join(f"{type(b).__module__}.{type(b).__name__}(prio={b.priority})" for b in available)

    backend = keyring.get_keyring()
    keyring.set_password("pyobs-gui-spike", "spike-user", "spike-password")
    pw = keyring.get_password("pyobs-gui-spike", "spike-user")
    keyring.delete_password("pyobs-gui-spike", "spike-user")
    roundtrip = "OK" if pw == "spike-password" else f"MISMATCH: got {pw!r}"
    results["keyring"] = (
        f"OK: chosen={type(backend).__module__}.{type(backend).__name__}, "
        f"roundtrip={roundtrip}, available=[{available_str}]"
    )
except Exception as e:
    results["keyring"] = f"FAIL: {e!r}"

out = "\n".join(f"{k}: {v}" for k, v in results.items())
print(out)

out_dir = os.path.dirname(os.path.abspath(sys.argv[0]))
with open(os.path.join(out_dir, "spike_results.txt"), "w") as f:
    f.write(out + "\n")

sys.exit(0)
