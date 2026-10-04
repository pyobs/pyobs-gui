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

    sidebar:
      - module: guiding
        widget:
          class: mypackage.GuidingExtraSidebarWidget

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


Settings and desktop notifications
***********************************

The GUI can show a desktop notification when a module goes into ``ERROR`` or when an ``ERROR`` or
``CRITICAL`` log event arrives, so an operator who has the GUI open but is not looking at it notices.
No tray icon is needed. Notifications are only shown while the GUI is not the active application.
Clicking one brings the window forward (where the desktop allows it, otherwise it is highlighted in
the taskbar) and, for a module error, selects that module.

Configured GUI (YAML)
=====================

Notifications are **off** unless the configuration has a ``notifications:`` block. With the block
present they are on, and these values can be set (all optional, shown with their defaults)::

    class: pyobs_gui.GUI

    notifications:
      enabled: true
      min_log_level: ERROR        # ERROR or CRITICAL
      only_when_inactive: true    # nothing while the GUI is the active application
      muted_modules: []           # modules that never notify
      rate_limit: 10              # seconds, repeats from one module are combined into "N more"

A typo in the block is an error at startup. At most 5 notifications are shown in 30 seconds, the rest
is combined into one "+N more notifications". Modules that are already in ``ERROR`` when the GUI
connects are announced together in one notification.

Standalone GUI (login window)
=============================

The standalone GUI has a **Settings** button above "Log out". The settings are saved per account in
``settings.yaml`` in the user's config directory (``~/.config/pyobs/pyobs-gui/`` on Linux) and apply
immediately. There are two tabs:

* *Notifications*: the values above, plus **Send test notification**, which shows whether the desktop
  shows notifications at all.
* *VFS*: the VFS roots, which the standalone GUI otherwise does not have. Without a root for the
  path a camera publishes, images and the live view cannot be loaded. A root has a name, a class
  (e.g. ``pyobs.vfs.HttpFile``) and parameters as YAML, the same as in a ``vfs:`` block.

The file can contain tokens in clear text, so it is only readable by the user (on systems that have
such permissions). A file that cannot be read is never overwritten: fix or delete it.

If nothing appears
==================

Use the test button first. It reports an error if the system refuses, and says what to check if it
does not. Notifications were checked on KDE Plasma and GNOME (Wayland) and on Windows 11, not yet on
macOS.

* On every system, check that Do Not Disturb (Focus Assist on Windows) is off.
* Windows shows a notification only for an app that has an entry in the Start Menu. pyobs-gui creates
  ``pyobs-gui`` there when it first sends a notification. Windows gives no error when it drops a
  notification, so if the entry was deleted, restart the GUI.
* macOS asks for permission once. If it was refused, allow it for pyobs-gui in System Settings.

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

The GUI shows one page per connected module, matching its interfaces against an ordered registry
of **main widgets** (``MAIN_WIDGETS`` in ``mainwindow.py``) — see below for the current list — plus
three always-present "Tools" pages. No screenshots yet — this section was written from source, not
from a running GUI; add screenshots as a follow-up.

Main widgets vs. sidebar widgets
=================================
Every entry in the registry drives either a **main widget** (fills the page) or is declared as a
**sidebar widget** for one or more main widgets (lives only in the page's sidebar, e.g. filter
wheel, focuser, temperature, cooling and FITS-header controls). A module matching several main
widgets gets one nav entry whose page is a tab widget, one tab per main widget (e.g. a camera
module that is also a filter wheel shows a "Camera" tab, with filter controls in the shared
sidebar rather than a separate tab); one match keeps a plain, tab-bar-less page; the sidebar itself
is shared across every tab, so e.g. FITS-header info stays visible while switching tabs. Some
interfaces (``IFilters``, ``IFocuser``, ``ITemperatures``, ``ICooling``) are *sidebar-preferred*:
they fill a sidebar slot on another matched main widget by default, but still get their own page if
a module implements one of them standalone (e.g. a bare filter-wheel-only module).

Custom ``widgets:``/``sidebar:`` config
==========================================
Each ``widgets:`` entry (``module``, ``widget``, optional ``label``, ``icon``, ``interface``,
``overwrite``) targets one connected module:

- ``interface: ICamera`` replaces/merges only the ``ICamera``-derived tab for that module (same
  registry slot, so tab order is stable); ignored with a log message if the module doesn't
  implement it.
- No ``interface`` and no ``overwrite`` — the entry is appended as an **extra tab** alongside
  whatever the registry already matched.
- No ``interface`` and ``overwrite: true`` — the page becomes **exactly** the custom entries (the
  ``guiding`` example above).

``sidebar:`` entries (``module``, ``widget``) are always appended to the page's sidebar, visible
regardless of the module's matched interfaces.

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

Temperatures — drives ``ITemperatures``
==========================================
Live sensor readout. Normally a sidebar block on a camera/telescope page; a temperature-sensor-only
module gets its own page.

Cooling — drives ``ICooling``
================================
Set/get the cooling setpoint. Normally a sidebar block on a camera page; a cooling-only module
gets its own page.


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
