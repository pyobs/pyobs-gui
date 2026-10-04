# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Entries for releases before this file existed were generated from commit subjects.

## [2.6.1] - 2026-10-04

- Require pyobs-core 2.14.0, which has the slimmed base dependencies

## [2.6.0] - 2026-10-04

- Declare astroquery, imported directly by telescopewidget
- Fix live view test: write the JPEG stand-in via a file
- Fix pyrefly errors in the live view
- Require qfitswidget>=1.2.0 (QImageWidget)
- Live view: use qfitswidget's QImageWidget for the stretch/cuts controls
- Skip hideEvent task when no event loop is running
- Slim dependencies: sunpy without extras, pyside6-essentials, declare pandas
- docs: settings and desktop notifications user docs, plan and status updates (#168)
- Add test notification button to the settings dialog (#168)
- docs: desktop notifications plan, KDE live check done
- Import pydantic before PySide6 so pyobs <config> can load pyobs_gui
- docs: desktop notifications plan, step 4 done
- Add NotificationManager and wire desktop notifications into the GUI (#168)
- docs: desktop notifications plan, step 3 done except Windows COM check
- Add desktop-notifier backend, failure guard and Windows app identity (#168)
- docs: desktop notifications plan, step 2 done
- Add Notifier protocol and NotificationPolicy for desktop notifications (#168)
- docs: drop packaging from the notification spike (standalone binary was rejected)
- docs: record Windows notification spike result and app identity (#168)
- docs: record KDE and GNOME notification spike results (#168)
- docs: plan for desktop notifications (#168)
- docs: design for desktop notifications (#168)
- Require pyobs-core 2.13.5 for VirtualFileSystem.set_roots()
- docs: settings dialog plan, step 5 and settings path
- Add standalone settings dialog (notifications, VFS roots) and wire settings into GUI
- docs: settings dialog plan, step 4 progress
- VideoWidget: re-resolve stream URLs when the settings change
- docs: tick settings dialog plan step 3
- Add GUI settings schema, per-account SettingsStore and notifications config
- docs: settings dialog audit findings and #185 plan status
- Show a clear error when a VFS root is not configured (#185)
- docs: design and plan for settings schema, YAML config and standalone settings dialog
- Live view: choose MJPEG (server stretch) or raw stream (client stretch)
- Fix pyrefly bad-override in test_basewidget_discard

## [2.5.3] - 2026-09-29

- Require pyobs-core>=2.13.0

## [2.5.2] - 2026-09-29

- Discard embedded child widgets, e.g. DataDisplayWidget
- specs: reference pyobs-core BaseVideo live-view design

## [2.5.1] - 2026-09-23

- Maintenance release (dependency and metadata updates only).

## [2.5.0] - 2026-09-17

- feat: prefer server-side IDataSequence sequences in SpectrographWidget
- docs: fitswidget-toolbar-overflow released -- qfitswidget v1.1.3, pyobs-gui v2.4.2

## [2.4.2] - 2026-09-15

- Fix sidebar min/max width bug that clipped real (non-sparse) content
- Fix sidebar-toggle icon direction: point where the click will move it, not current state
- Wrap stackedWidget in a QScrollArea as a general width/height-floor fallback
- Add plan: QScrollArea fallback around stackedWidget
- ModulePage: give the sidebar a real minimum width, plus a collapse toggle
- TelescopeWidget: size the move-type stack to the current page, wrap long form rows
- docs: gui-standalone-binary rejected -- real build came out several GB
- Suppress spurious astropy do_format RuntimeWarning in telescope widget
- Add CLAUDE.md entry point pointing to specs/ conventions and tooling

## [2.4.1] - 2026-09-04

- Fix pyobs-core floor: ConfigFieldSchema.description needs >=2.7.2, not 2.7.1

## [2.4.0] - 2026-09-04

- feat: show field description below the input widget
- feat: hide EXPERT fields instead of disabling them

## [2.3.1] - 2026-09-04

- bumped core pin
- feat: basic/expert field visibility in StructuredConfigWidget
- Close out main-vs-sidebar-widgets plan: issue #150 closed, released v2.3.0
- Close out video-widget-split doc with release refs

## [2.3.0] - 2026-09-03

- Fix ModeWidget's edit button staying permanently disabled without IMotion
- Fix CameraWidget control panel clipping its right edge
- Split VideoWidget into two independent main widgets, no sidebar pairing needed

## [2.2.0] - 2026-09-03

- fix: build matplotlib figures via the OO API, not pyplot
- fix: gate camera/roof widget state subscriptions on interface support
- fix: drop stale top-level name: field from test/*.yaml fixtures
- test: add structuredconfig.yaml fixture for manual StructuredConfigWidget verification
- feat: generic IStructuredConfig widget, schema-driven config form (#154)
- docs: mark main-vs-sidebar-widgets plan implemented (#150, PR #157)
- feat: make ModulePage sidebar vertically scrollable
- fix: align FitsHeadersWidget sidebar box with Temperatures/Cooling
- fix: address PR #157 review findings 1-5 plus nits
- fix: gate FitsHeadersWidget to ICamera/IVideo, not every module
- docs: document main/sidebar widgets and widgets:/sidebar: config contract
- Add tests for multi-widget pages and the new MAIN_WIDGETS registry
- Implement main-vs-sidebar widget registry and tab pages (#150)
- docs(specs): fix double-tab and invisible-sidebar bugs in #150 plan, add VideoWidget split follow-up
- docs: mark irobotic-widgets plan implemented/closed (#825, PR #155)
- Re-enable whole-row selection in ScheduleWidget table
- Hide row headers and disable focus/selection rect in ScheduleWidget table
- Cap autonomous-warning label height; use equal-width stretched columns
- Auto-size ScheduleWidget columns; raise test config's blocked_probability
- Add RoboticWidget/ScheduleWidget for IRobotic/IRoboticScheduler (#825)
- docs: plan RoboticWidget/ScheduleWidget for IRobotic/IRoboticScheduler (#825)
- docs: fix stale irobotic.md status in specs index
- docs(specs): add main vs. sidebar widget tab-pages plan (issue #150)
- docs(specs): add generic IStructuredConfig widget plan (issue #154)
- fix: make _nuitka_astropy_patch a no-op outside Nuitka builds (fixes #151) (#152)
- Require stable pyobs-core>=2.0.0
- Add Dependabot auto-merge workflow
- Drop Sphinx <9/sphinx-rtd-theme <4 caps to match the rest of the fleet
- Add widget catalog and keyboard shortcuts to docs, rewrite README
- feat(videowidget): send Authorization header on raw-socket MJPEG stream (#142)
- docs: mark widget startup responsiveness plan implemented, closed
- feat: make module widgets appear and respond immediately at startup (#141)
- Index the BaseVideo HTTP token-auth plan from pyobs-core
- docs: address review findings in widget startup plan
- docs: fix widget startup plan's placeholder-swap bug, harden teardown

## [2.1.0] - 2026-09-01

- fix: drop stale top-level name: field from test/*.yaml fixtures
- test: add structuredconfig.yaml fixture for manual StructuredConfigWidget verification
- feat: generic IStructuredConfig widget, schema-driven config form (#154)
- docs: mark main-vs-sidebar-widgets plan implemented (#150, PR #157)
- feat: make ModulePage sidebar vertically scrollable
- fix: align FitsHeadersWidget sidebar box with Temperatures/Cooling
- fix: address PR #157 review findings 1-5 plus nits
- fix: gate FitsHeadersWidget to ICamera/IVideo, not every module
- docs: document main/sidebar widgets and widgets:/sidebar: config contract
- Add tests for multi-widget pages and the new MAIN_WIDGETS registry
- Implement main-vs-sidebar widget registry and tab pages (#150)
- docs(specs): fix double-tab and invisible-sidebar bugs in #150 plan, add VideoWidget split follow-up
- docs: mark irobotic-widgets plan implemented/closed (#825, PR #155)
- Re-enable whole-row selection in ScheduleWidget table
- Hide row headers and disable focus/selection rect in ScheduleWidget table
- Cap autonomous-warning label height; use equal-width stretched columns
- Auto-size ScheduleWidget columns; raise test config's blocked_probability
- Add RoboticWidget/ScheduleWidget for IRobotic/IRoboticScheduler (#825)
- docs: plan RoboticWidget/ScheduleWidget for IRobotic/IRoboticScheduler (#825)
- docs: fix stale irobotic.md status in specs index
- docs(specs): add main vs. sidebar widget tab-pages plan (issue #150)
- docs(specs): add generic IStructuredConfig widget plan (issue #154)

## [2.0.1] - 2026-08-28

- fix: make _nuitka_astropy_patch a no-op outside Nuitka builds (fixes #151) (#152)

## [2.0.0] - 2026-08-26

- Require stable pyobs-core>=2.0.0
- Add Dependabot auto-merge workflow
- Drop Sphinx <9/sphinx-rtd-theme <4 caps to match the rest of the fleet
- Add widget catalog and keyboard shortcuts to docs, rewrite README
- feat(videowidget): send Authorization header on raw-socket MJPEG stream (#142)
- docs: mark widget startup responsiveness plan implemented, closed
- feat: make module widgets appear and respond immediately at startup (#141)
- Index the BaseVideo HTTP token-auth plan from pyobs-core
- docs: address review findings in widget startup plan
- docs: fix widget startup plan's placeholder-swap bug, harden teardown
- docs: add widget startup responsiveness plan
- Fix MJPEG live view through TLS reverse proxy
- docs: mark remote-call error-handling plan implemented, fix stale specs index
- Catch exceptions on remote method calls and show them in a messagebox (fixes #134) (#138)
- Fix VideoWidget to use VideoCapabilities.mjpeg instead of removed .video field
- Remove upper bound on Python version
- Fix sender name in DataDisplayWidget.grab_data
- Rename specs/README.md to index.md
- Add exposure count to SpectrographWidget
- Fix pre-existing pyrefly errors in weatherwidget and camerawidget test
- Fix image display in DataDisplayWidget
- Upgrade uv.lock to clear open Dependabot alerts
- Fix asyncio task reentrancy in focus widget dialogs
- Show 4 decimal digits for Heliprojective Radial Mu/Psi spin boxes
- Only use server-side IDataSequence sequences when broadcasting
- Stop forcing the Alt/Az offset plot to include the origin
- Type the PLY grammar namespace as Any to fix pyrefly CI failure
- Plot sensor history in WeatherWidget's reserved plot frame
- Move DEV_*.md design docs and DEVELOPMENT.md into pyobs-core/specs/
- Bundle package distribution metadata for importlib.metadata lookups
- Bundle slixmpp plugins, drop QtWebEngine from the standalone binary
- Build recipe for the standalone pyobs-gui binary
- Add pyobs-gui console script entry point
- Revert "v2.0.0.dev5"
- Enlarge nav sidebar and log panel defaults, swap clear-log icon to a trash bin
- Replace the client-select list with icon toolbuttons next to the log
- Fix shiboken crash from stale StatusWidget callbacks after logout
- Fetch telescope location from the module itself when no local observer exists
- Add a "logged in as" sidebar and standalone logout flow to MainWindow
- Standalone binary groundwork: pyside6-deploy spike and the login window (#116)
- Require pyobs-core>=2.0.0.dev48
- Point to the new pyobs-gui standalone-binary docs
- Read IRunning state instead of calling the removed is_running() RPC
- Fix ruff/pyrefly CI failures in weatherwidget and compassmovewidget
- Add pointer to pyobs-core for design/planning docs
- Replace custom widgets in CameraWidget UI with standard Qt widgets
- Revert camera widget to plain spin boxes, set all values in expose()
- Remove mypy dev dependency
- Fix live-view socket and grab_data call in VideoWidget
- Adopt PyobsError rename and bump pyobs-core to dev28
- Update test configs to use DummyAltAzTelescope instead of DummyTelescope
- Add TODO for PyObsError rename coming in pyobs-core
- Use IDataSequence for counted exposures, when available
- Discard widgets' event registrations on client disconnect
- Adapt WeatherWidget to new IWeather state-based interface, bump pyobs-core lock
- Wire up IPointingBody and IPointingHeliocentricPolar
- Wire up Orbit Elements tracking, gated on IPointingOrbitalElements
- Adapt TelescopeWidget to renamed IPointingHeliographicStonyhurst interface
- Add dependabot config to target develop branch
- Adapt ModeWidget to name-based IMode.set_mode group parameter
- Implement navbar keyboard shortcuts
- added dev file
- Add design doc for navbar keyboard shortcuts
- new dev document
- Redesign module sidebar: compact single-row items, section headers, resizable width
- Add offset-magnitude and lon/lat plots to AutoGuidingWidget, fix exposure-time pre-fill
- Follow AcquisitionResult/AcquisitionAttempt offset field consolidation, integer attempt ticks
- Add 2D offset trajectory plot to AcquisitionWidget
- Add AcquisitionWidget and AutoGuidingWidget
- Add AutoFocusWidget for IAutoFocus, wire up dummy test config
- Introduce design proposals for IAutoGuiding, IAutoFocus, and IAcquisition widgets
- Grey out actions denied by pyobs-core ACLs, hide fully-denied modules
- Document ACL follow-up options: reactive-only vs proactive greying-out
- Unsubscribe status widget presence callback when a module closes
- Note pyobs-core 2.0 ACL follow-up work in DEVELOPMENT.md
- Fix phantom state subscription for composite interfaces in status view
- Let clicking anywhere in a status row toggle expand/collapse
- Disable focus on status tree so clicks leave no focus rectangle
- Show module interfaces, capabilities and live state in status view
- Replace stale RPC calls with wait_for_state in CompassMoveWidget
- Update to pyobs-core 2.0.0.dev10, apply FitsHeaderEntry to fits header methods
- docs: add DEVELOPMENT.md with backlog and implementation details for pyobs-gui
- chore: update dependencies for astropy-iers-data and pyobs-core to latest versions
- refactor: reformat long conditionals in TelescopeWidget and EventsWidget for readability
- refactor: simplify module name check in FitsHeadersWidget
- refactor: remove unused Proxy import and use context managers for proxy handling in VideoWidget
- refactor: add type ignore comments for attribute definitions in TelescopeWidget
- refactor: remove unused Proxy import and update type hints in StatusWidget
- refactor: remove unused Proxy import and update type hints in SpectrographWidget
- refactor: remove unused Proxy import and update type hints in ShellWidget
- refactor: remove unused Proxy import and simplify module passing in ModuleWindow
- refactor: update type hints in ModeWidget and remove unused Proxy import
- refactor: use context managers for proxy handling in MainWindow to ensure proper cleanup and improve stability
- refactor: remove unused proxy imports and update type hints in EventsWidget
- refactor: use proxy-based capability checks and async operations for offset handling in CompassMoveWidget
- refactor: simplify state management by replacing interface-based checks with client state retrieval in BaseWidget
- refactor: remove deprecated property-based bindings in ModeWidget for cleaner state management
- refactor: remove unused imports in ModifiedMixin and DataDisplayWidget for cleanup
- refactor: replace interface-based state usage with explicit state classes across all widgets for improved clarity and maintainability
- docs: remove DEVELOPMENT.md as Phase 4 migration is complete and the document is no longer needed
- refactor: migrate ModeWidget to use capability-based mode handling and state subscriptions, improve UI logic and maintain backward compatibility
- refactor: update DEVELOPMENT.md to document DummyVideo addition, widget testing updates, and final Phase 4 status
- refactor: optimize VideoWidget with state subscriptions, interface caching, and improved VFS error handling; add widget testing configurations
- test: remove unused `shared.world` configuration from test YAML files
- fix: handle initialization of temperature data correctly, avoid issues with empty or uninitialized DataFrames
- fix: correct sender comparison in DataDisplayWidget to avoid false negatives
- refactor: update DEVELOPMENT.md to document required pyobs-core changes for MultiModule and GUI integration
- test: add configuration files for widget testing with dummy modules
- refactor: update DEVELOPMENT.md to reflect widget migration progress, clarify state subscription usage, and add testing details
- refactor: update DEVELOPMENT.md to mark widget migrations as complete and document final changes to state subscriptions and RPC interactions
- refactor: migrate video widget to state subscriptions, streamline UI updates, and remove event-based logic
- refactor: migrate temperatures widget to state subscriptions, streamline UI updates, and remove event-based logic
- refactor: migrate spectrograph widget to state subscriptions, streamline UI updates, and remove event-based logic
- refactor: migrate roof widget to state subscriptions, streamline UI updates, and remove event-based logic
- refactor: migrate mode widget to state subscriptions, streamline UI updates, and remove event-based logic
- refactor: migrate camera widget to state subscriptions, remove event-based logic, and streamline UI updates
- refactor: migrate telescope widget to state subscriptions, streamline UI updates, and remove legacy event-based logic
- refactor: use state subscriptions for focus widget, replace event-based logic, and streamline UI interactions
- docs: update DEVELOPMENT.md to reflect filter and motion state changes
- refactor: simplify filter widget by using state subscriptions and removing event-based logic
- docs: add development notes for pyobs-gui Phase 4 updates and API changes
- refactor: re-enable status widget and clean up commented-out code
- refactor: streamline status handling and UI updates, remove redundant state logic
- refactor: adjust full frame handling with updated capability structure
- use capabilities for full frame
- gain and window state integration, adjust UI alignment, refine exposure and data handling
- working on state implementation
- show current values and add dirty inputs
- use IWindow.State
- states
- gain state
- use intenral State
- CoolingWidget working
- ICooling to v2.0
- add pyrefly pre-commit hook
- add pyrefly GitHub Actions workflow
- fix more pyrefly type errors
- fixed path
- switch to ruff, add pyrefly, fix type errors
- to PySide6
- tidying up for ruff
- tidying up
- moved from flake8 to ruff

## [1.8.8] - 2026-07-09

- fix `textStatus` assignment to use `_motion_status` directly

## [1.8.7] - 2026-06-29

- postpone `butAbort` visibility setup until `open()` is called

## [1.8.6] - 2026-06-26

- fixed pyobs-core dependency version

## [1.8.5] - 2026-06-16

- Maintenance release (dependency and metadata updates only).

## [1.8.4] - 2026-06-16

- Maintenance release (dependency and metadata updates only).

## [1.8.3] - 2026-06-16

- Maintenance release (dependency and metadata updates only).

## [1.8.2] - 2026-06-16

- fix RA/Dec display: avoid Angle.to_string() incompatible with numpy 2.x
- guard against NaN RA/Dec from uninitialized telescope

## [1.8.1] - 2026-06-08

- don't use .value or .name on StrEnum
- MotionStatus is a StrEnum now, so no .value needed
- changed all Time imports from astropy.time to pyobs.utils.time.

## [1.8.0] - 2026-06-08

- new min pyobs version
- entry.time can no be in isot format
- formatting
- re-added future import
- changing old-style type hints to new style
- removed from __future__ import annotations everywhere

## [1.7.4] - 2026-05-29

- fixed attribs

## [1.7.3] - 2026-05-28

- upped min pyobs-core version
- changed underscore parameters for vfs, comm, etc
- renamed Object parameters (comm, observer, ...) to start with an underscore

## [1.7.0] - 2025-12-17

- faster startup by not waiting for all other clients first
- .

## [1.6.0] - 2025-12-04

- refactored shell command and its response into own classes

## [1.5.1] - 2025-12-01

- new qfitswidget and Qt6
- new qfitswidget
- reverted back to old method
- fixed bugs
- fixed sorting of clients
- clean up
- pyside6
- fixed uic errors
- pyside6 changes
- working on pyside6 change
- mypy
- cleaning up
- added some   # type: ignore
- cleaning up for pyside6
- matplotlib
- resources
- initial conversion
- setting gain and offset separately
- log brightness and contrast
- return QVariant instead of empty string
- reconnect slots
- fixed simbad query
- fixed bug
- type hints
- BaseWidget.module() never returns None
- ignore types for self.setupUi(self)
- removed ignore
- ignore qt auto-generated files
- ignore astropy
- BaseWidget now inherits from QWidget
- removed file

## [1.5.0] - 2025-07-24

- Maintenance release (dependency and metadata updates only).

## [1.4.1] - 2025-07-24

- new lock file

## [1.4.0] - 2025-07-02

- pypi
- pypi actions
- removed slixmpp from deps, since it's already in pyobs-core
- dev deps
- pre-commit
- ran black
- ran flake
- added flake8
- working on poetry->uv migration

## [1.3.0] - 2025-05-08

- python version

## [1.2.0] - 2025-01-07

- since qfitswidget requires Python 3.10, this will also
- updated devs to latest version

## [1.1.0] - 2024-09-02

- ModeWidget working
- adding widgets
- working on ModeWidget
- datetime.utcnow() to datetime.utc(timezone.utc)

## [1.0.12] - 2024-07-08

- python 3.12

## [1.0.11] - 2024-03-21

- fixed docs

## [1.0.10] - 2023-10-09

- updated deps
- updating deps
- allow python 3.11

## [1.0.9] - 2023-09-12

- updating deps
- fixed roof buttons

## [1.0.8] - 2023-07-18

- fixed bug with Tx/Ty.degrees instead of .degree

## [1.0.7] - 2023-07-14

- fixed mupsi movement

## [1.0.6] - 2023-07-12

- removed debug output
- added icons to default config
- working on new default config for GUI
- added helper functions for getting required module from list
- all widgets now take a list of modules instead of a single one in their open method
- fixed bug
- changed default unit in GUI to arcsec, and in logic to degree
- renaming helioprojective to helioprojective mu/psi and added helioprojective radial
- getting pyobs fit for Python 3.11 that will ship with Debian 12

## [1.0.5] - 2023-03-22

- fixed bug

## [1.0.4] - 2023-03-07

- removed debug output

## [1.0.3] - 2023-03-07

- custom icons
- temperature plot
- changed cooling GUI

## [1.0.2] - 2022-11-29

- closing GUI
- set own_comm to False for module
- removed debug output
- added closeEvent
- made Module.name a property
- fixed bug
- GUI is shown
- widget for filter wheel
- working on local GUI for single module

## [1.0.0] - 2022-09-13

- updated dependencies
- added license

## [0.21.0] - 2022-08-25

- handle optional event parameters, closes #124
- store signature
- working on handling optional parameters better
- fixed focus buttons, closes #173
- updated dependencies

## [0.20.1] - 2022-07-28

- fixed layout
- always show vertical scrollbars in module list
- Instead of checking whether there are any autonomous modules, we are now checking whether those modules are actually running before displaying the warning message.
- default values for mu/psi

## [0.20.0] - 2022-06-27

- adaptions for new IData
- renamed get_cooling_status to get_cooling
- refactored ICamera/IVideo/ISpectrograph to use IData (formerly IImageGrabber) and IExposure (formerly part of ICamera and ISpectrograph)

## [0.19.4] - 2022-06-23

- cleaning up
- Create event loop from static method in module before instanciating the module
- test
- testing quit

## [0.19.3] - 2022-06-22

- fixed coordinate conversion for HELIOPROJECTIVE_RADIAL
- removed except blocks
- set update_task to None on hide
- replaced qtimer with asyncio task

## [0.19.2] - 2022-06-21

- make it work again

## [0.19.1] - 2022-06-21

- removed old icons
- use qtawesome for icons
- new icons
- icon alignment

## [0.19.0] - 2022-06-20

- changed filename
- open datadisplay widget
- moved code into _init
- added method to extract widgets into new windows
- extracted CompassMoveWidget
- video and spectrograph
- fixed script
- removed debug output
- removed unnecessary plugins
- seems to work with both pyobs and designer
- started working on designer compatible file layout
- moved code from __init__ into open
- at least it starts again...
- base
- offset fixes

## [0.18.4] - 2022-05-07

- fixed: DeprecationWarning: Using or importing the ABCs from 'collections' instead of from 'collections.abc' is deprecated since Python 3.3, and in 3.10 it will stop working

## [0.18.3] - 2022-05-03

- Fixed the name of a function. This caused neither gain nor exposuretime to be changed through the gui.

## [0.18.2] - 2022-04-12

- text formatting
- Fixed the conversion of helioprojective radial coordinates to heliographic stonyhurst coordinates.
- added sunpy dependency

## [0.18.1] - 2022-03-14

- added gain to video widget

## [0.18.0] - 2022-03-13

- added gain
- fixed update of status
- example config
- fixed rtd

## [0.16.0] - 2022-01-18

- basic docs
- log more errors to shell (invalid module or method)
- changed color scheme
- print OK instead of None on method calls that return nothing
- show exceptions in shell, fixes #82
- added column with version
- added status page
- added await
- update client list when modules (dis)connect
- fixed auto-complete list to select from, see #83
- use create_future
- check module state on update
- added CRITICAL log level
- raising new InvocationError on remote errors
- testing new exceptions
- added more digits to exposure time
- fixed bug
- type hints
- unified PyQt5 imports
- use black with a line length of 120
- added PyQt5-stubs
- added type hints
- black formatted
- added black and run it in pre-commit

## [0.15.0] - 2021-12-29

- changed used Python version to 3.9
- Handle case when value is none
- Pushed requirements to Python>=3.9 and astropy>=5.0, closes #55
- replaced all occurrences of "thread" with "task"
- sending event async
- fixed bug
- made all events async
- catch CancelledError for background task
- fixed bug when not broadcasting
- async data download
- asyncio
- proxy() is async now
- using async vfs.read_fits
- removed lock
- removed all use of threading module
- async event handler
- open widgets
- use asyncio.Event instead of threading.Event
- started working on asyncio implementation
- only scroll logs to bottom, if slider is at max position fixes #18
- added JPL Horizons query for RA/Dec coordinates

## [0.14.2] - 2021-11-23

- added planet/moon/sun ephemerides
- removed the whole poetry build process

## [0.14.1] - 2021-11-18

- new pypi action
- added ignore_dev_requirements: "yes"
- replaced setup.py and requirements.txt with Poetry
- added custom sidebar widgets
- changed WidgetImageGrabber to WidgetDataDisplay and adopted it for use with ISpectrograph
- handle NewSpectrumEvent
- don't use get_exposure_time_left
- added widget for ISpectrograph
- remove client from dict on disconnect and put lock around (dis)connected code
- hopefully fixed problem with not all modules showing up
- warning when weather module is running but not active
- fixed bug
- v0.14
- renamed IFitsHeaderProvider to IFitsHeaderBefore and get_fits_headers() to get_fits_header_before()
- added support for helioprojective radial coordinates
- don't show kwargs on event page
- removed call to label()
- Added type hints
- use Proxy interfaces
- renamed set/get_*_offsets to set/get_offsets-*
- renamed some interfaces (IPointing* and IOffsets*)
- changed IMuPsi to ICoordsHGS
- cosmetic change
- going back to one module per widget
- New parameter widgets for custom widgets
- default widgets
- basing all widgets on a more common BaseWidget
- new range for offsets
- moving to helioprojective coordinates
- unified resetting offsets
- new way for showing coordinate systems, added helioprojective
- Flat fielding
- renamed ICameraWindow to IWindow
- renamed ICameraExposureTime to IExposureTime
- renamed ICameraBinning to IBinning
- image types and multiple images
- removed imports
- exposure time
- .
- gui
- WidgetImageGrabber in WidgetVideo
- WidgetCamera seems to work with WidgetImageGrabber
- started working on extracting WidgetImageGrabber from WidgetCamera
- use a WidgetCamera inside WidgetVideo
- some changes to work with IImageGrabbers and not just ICameras
- use grab_image() instead of expose()
- explicitly cast float to int
- renamed WidgetWebcam to WidgetVideo
- renamed IWebcam->IVideo and BaseWebcam->BaseVideo
- taking video URL from vfs
- added widget for IWebcam
- added show_modules parameter to restrict access to given modules
- added parameters show_shell and show_events
- moved requirements into requirements.txt
- v0.13
- documentation
- added __module__
- updated docstrings
- moved IMotion.Status to utils.enums.MotionStatus
- moved ExposureStatus to utils.enums
- fixed bug (_update_thread is never None)
- fixed types to make mypy happy
- fixed type hints
- added combo box for exposure time unit
- add warning to logger when GUIs update_func fails
- fixed bug when auto-saving
- allow for negative offsets in dialog
- Moved "images" module to top-level
- download images in thread
- sorting page icons
- catch exception
- size of page selector
- instead of manually connection signals/slot, use pyqtSlot()
- show security question when disabling broadcast
- changed order of setting max and current values
- added new checkbox to avoid broadcasting new images
- hide controls if not required
- changed signature of ICameraBinning's list_binnings() to return list of X,Y tuples
- fetching available binnings from module
- added combo box for setting image format
- set maximum values for window
- made binning a check box and added option for image format

## [0.12.2] - 2021-02-06

- adopted for name change from qfitsview to qfitswidget

## [0.12.1] - 2021-01-05

- fixed bug
- fixed broken merge
- v0.12
- using new IImageType and ImageType enum
- moved exposure time specific stuff from ICamera into new ICameraExposureTime and removed exposure_time parameter from ICamera.expose()
- Revert "Removed count parameter from ICamera.expose()"
- GUI handles exposing multiple images on its own without count in ICamera.expose()
- generic types don't seem to have a __name__
- moved some imports into methods
- renamed download_fits_image() and download_image() to read_*()
- validate telescope coordinates
- changed tab order of widgets in camera widget
- fixed crash when trying to navigate to old commands, but none were given before
- added focal_length, pixel_size and fits headers
- moved more code from DummyTelescope into SimTelescope
- changed handling of name/label for module
- removed possibility for network configs
- v0.11
- made changes in _off_ra/dec/alt/az members threadsafer
- new warning
- show warning if there is an active mastermind
- checkboxes for sending events

## [0.10.1] - 2020-05-14

- removed aplpy from dependencies
- added POSITIONED to valid states
- v0.10
- removed parent for Layout
- PyQt 5.14 seems to fail installing, so fix to 5.13 for now
- handling Nones
- showing dome Az in GUI
- ITelescope inherits IRaDec and therefore track_radec is renamed to move_radev
- renamed IEquatorialMount to IRaDecOffsets and IAltAzMount to IAltAzOffsets
- swap sign for RA offsets
- error checking
- added weather widget
- added POSITIONED to initialized states
- v0.9
- only add fits headers for camera that belongs to this widget
- added additional custom headers
- colorize buttons
- fixed layout
- fixed bug
- more colours and different layout for filters
- removed debug output
- added missing resources
- moving offsets
- finishing new GUI
- working on new telescope page layout
- added error handling for MPC queries
- added MPC query
- removed pyobs-core from requirements
- added button for resetting focus offset
- new way of setting focus via input dialog
- message when no simbad results were found
- renamed run() on PyobsModule to main()
- update filter and focus on regular basis
- enumerate commands and results in shell and fix crash bug
- converting np.float to float
- show current filename
- replaced colon by whitespace in filename pattern
- added checkbox for adding fits headers, which is unchecked by default
- fixed bugs
- - changed MotionStatusChangedEvent to give status of all interfaces - added MotionStatusMixin - fixed DummyTelescope to use it - fixed GUI to use it
- fixed method signatures and implemented namespaces for FITS headers
- get_fits_headers from IFitsHeaderProvider now accepts a list of namespaces
- moved multiple exposures from GUI into camera module
- added qfitsview to required packages
- catching ModuleNotFoundError for pwd on Windows
- added pyobs-core to required packages
- distutils -> setuptools
- v0.8
- error handling
- fixed bug with redrawing image every second
- added pyobs_gui.qt
- measuring exptime in seconds
- more init in _init
- trying to speed up things a little bit
- replaced SendToArchive with generic ImageWatcher
- added fits header gui
- returning dict
- doing multiple exposures in GUI, not in camera module
- showing events
- limiting image types to object, bias, and dark
- saving and auto-saving of images
- disable auto-update of image/headers
- using init/park
- renamed get_alt_az->get_altaz and get_ra_dec->get_radec
- renamed track->track_radec, move->move_altaz, offset->offset_altaz
- sending events from gui
- removed percent open for now
- more output
- working on simple task
- using run() method for running gui
- accept negative numbers
- changed NEWLINE with ENDMARKER
- changed enter/leave to Qt show/hide events
- environment -> observer
- using QFitsView instead of AplPy for displaying image
- added widget for script runner
- using tokenize for parsing input
- changed version number to 0.2
- checking sender in event handlers
- for XMPP, senders for events and proxy names are now usernames only and not full JIT anymore
- plots
- show degree sign for alt/az
- show alt/az for input ra/dec
- added simbad query and missing files
- reacting to connecting/disconnecting clients
- set full frame to binned size
- new icons
- show FocusWidget for IFocuser
- disabled WidgetTemperatures because of missing files
- fixed base class
- sorted temperatures
- new ITemperatures interface
- cooling display works
- lock for roof movement
- moved update thread into BaseWidget
- basic dummy roof and widget
- filter for camera
- moved sidebar stuff into BaseWidget
- showing fits headers
- async init of widgets
- working on layout
- removed sidebar, moved client list next to log
- showing image based on NewImageEvent
- only show coordinates when available
- camera expose() always returns a list now
- disabled plot for now
- cleaned up
- changed to use events and stuff
- working on type-casting request and response for remote calls
- using events instead of constant polling
- added new ExposureStatusChanged event
- got ascom working again
- checking type
- first attempts on track plot
- setting filter and focus
- moving alt/az
- disable gui until first update finished
- working on telescope GUI
- started working on telescope GUI
- GUI is a normal pyobs module now
- renamed pytel to pyobs
- working with cameras that don't support windowing or binning
- gracefully exit threads
- added camera panel
- show whole exception
- styling
- changed layout with logs and help always visible
- working on new GUI
- allow single as well as double quotes for strings
- working
- initial commit
