pyobs-gui
#########

This is a `pyobs <https://www.pyobs.org>`_ (`documentation <https://docs.pyobs.org>`_) module providing a GUI
for operating the whole system.


Example configuration
**********************

This is an example configuration for a GUI that defines one custom widget for the ``guiding`` module::

    class: pyobs_gui.GUI

    widgets:
      - module: guiding
        overwrite: True
        widget:
          class: mypackage.GuidingWidget

    comm:
      jid: test@example.com
      password: ***

    timezone: Europe/Berlin
    location:
      longitude: 9.944333
      latitude: 51.560583
      elevation: 201.

    vfs:
      class: pyobs.vfs.VirtualFileSystem
      roots:
        cache:
          class: pyobs.vfs.HttpFile
          download: http://localhost:37075/
        webcam:
          class: pyobs.vfs.HttpFile
          download: http://localhost:37077/


Available classes
******************

There is one single class for the GUI.

GUI
===
.. autoclass:: pyobs_gui.GUI
   :members:
   :show-inheritance:


Widgets
*******

The GUI shows one page per connected module, picking a widget by the module's interfaces
(``DEFAULT_WIDGETS`` in ``mainwindow.py``), plus three always-present "Tools" pages. No screenshots
yet — this section was written from source, not from a running GUI; add screenshots as a follow-up.

Shell
=====
Always present. A command console: type shell-like commands against any connected module, with
tab-completion driven by the module's own docstrings, and a per-module command history.

Events
======
Always present. Live feed of events broadcast by connected modules, and lets you send one back.

Status
======
Always present. Per-module connection/presence indicator plus a live, expandable tree of each
connected module's published state.

Camera — drives ``ICamera``
============================
Expose/abort control: binning, gain, image format/type, exposure time, full-frame vs. windowed
readout, and (if the module supports it) data sequences.

Telescope — drives ``ITelescope``
====================================
Init/park/stop and move-to-target, offsets in both RA/Dec and Alt/Az, Simbad and JPL Horizons
target lookup, and tracking of orbital elements or solar-system bodies.

Roof — drives ``IRoof``
==========================
Open/close/stop the roof, with live motion and pointing state.

Focuser — drives ``IFocuser``
================================
Set an absolute focus value, apply/reset a focus offset.

Auto Focus — drives ``IAutoFocus``
=====================================
Run or abort an autofocus sequence.

Acquisition — drives ``IAcquisition``
========================================
Acquire a target, abort an in-progress acquisition.

Auto Guiding — drives ``IAutoGuiding``
=========================================
Start/stop guiding and set the guide-exposure time.

Weather — drives ``IWeather``
================================
Live sensor values plus a history plot.

Video — drives ``IVideo``
============================
Live view (MJPEG/raw stream), grab a still, adjust exposure time/gain/image type.

Spectrograph — drives ``ISpectrograph``
==========================================
Grab a spectrum, abort an in-progress exposure.

Filter wheel — drives ``IFilters``
=====================================
Set the active filter.


Keyboard shortcuts
*******************

Global, not per-widget — bound with the ``Ctrl``/``Ctrl+Alt`` modifier specifically so no
text/numeric-entry widget can mistake one for ordinary input.

===============  ==========================================================
Shortcut          Action
===============  ==========================================================
``Ctrl+1``        Switch to Shell (fixed)
``Ctrl+2``        Switch to Events (fixed)
``Ctrl+3``        Switch to Status (fixed)
``Ctrl+4``..``Ctrl+9``, ``Ctrl+0``
                  Switch to whichever module page is bound to that slot
                  (no-op if unbound or that module isn't connected)
``Ctrl+Alt+4``..``Ctrl+Alt+9``, ``Ctrl+Alt+0``
                  Bind the currently selected page to that slot, overwriting
                  any previous binding
===============  ==========================================================
