# Desktop notifications for module ERROR and log ERROR/CRITICAL

Status: proposed (issue #168). Settings come from `specs/2026-10-04-settings-dialog.md`
(`NotificationSettings`, implemented).
Related, independent: pyobs-core `specs/design/push-notification-module.md` (mobile push relay,
for when nothing is running).

## Problem

An operator with pyobs-gui open but not looking at it (minimized, other monitor, other workspace)
should get an OS notification when a module goes into `ERROR` or an `ERROR`/`CRITICAL` log event
arrives. The GUI already sees both live, it just doesn't tell anyone.

## Decided (Tim, 2026-10-04)

- Target desktops: GNOME, KDE, Windows and macOS.
- **No tray icon**, not even a temporary one. This rules out `QSystemTrayIcon.showMessage()`, which
  the issue suggested. None of the target platforms needs a tray for notifications: KDE and GNOME
  use the `org.freedesktop.Notifications` D-Bus interface (KDE checked, GNOME inferred from the
  spec), Windows uses toasts, macOS uses Notification Center (both unchecked here).
- Clicking a notification raises the window. For a module `ERROR` it also selects that module's
  page; for a log event it only raises the window.
- Module `ERROR` -> `READY` does not notify (errors only).
- Modules already in `ERROR` when the GUI connects: one summary notification, not one per module.
- Default: on in standalone mode, off in YAML mode unless the YAML has a `notifications:` block.
- "Only when inactive" means the application is not the active one
  (`QGuiApplication.applicationState() != ApplicationActive`), not whether the window is visible.
- Rate limiting per module (the `rate_limit` setting) plus a global cap.

## Design

### Sending: `desktop-notifier`, behind a small interface

Without a tray icon, Qt has no native notification API, so a library is needed.

- **Recommended: `desktop-notifier`** (PyPI, 6.2.0 at time of writing). Checked in an ephemeral
  environment on Linux: `DesktopNotifier.send(title, message, urgency, ..., on_clicked, thread,
  timeout)` exists, no tray icon involved. Its dependencies per PyPI metadata: `dbus-fast` on Linux,
  `winrt-runtime` on Windows, `rubicon-objc` on macOS. It is asyncio based, which fits the qasync
  loop the GUI already runs on.
- Alternative: QtDBus (`org.freedesktop.Notifications`, no dependency, works under GNOME and KDE)
  on Linux plus `windows-toasts` or `winotify` on Windows. Two code paths, more code. This covers
  Linux and Windows only: there is no equivalent for macOS without adding something like
  `pyobjc`, which is one reason `desktop-notifier` is the first choice. Fallback for Linux and
  Windows if `desktop-notifier` fails the spike below; macOS would then need its own backend.

Either way the rest of the GUI only sees this interface, so the backend can be swapped:

```python
class Notifier(Protocol):
    async def send(self, title: str, message: str, critical: bool, on_clicked: Callable[[], None]) -> None: ...
```

`app_name` is `pyobs-gui` with the app icon (the library's default is "Python").

### What counts as an event

- **Module `ERROR`:** the transition to `ModuleState.ERROR` from the presence callback
  (`comm.subscribe_presence(module, cb)`, delivers the current state first, then every change,
  same as `StatusWidget` uses). The manager subscribes for every connected module itself, so it
  doesn't depend on which pages exist, and `show_modules` filtering does not hide errors.
  Subscriptions follow `ModuleOpenedEvent`/`ModuleClosedEvent` and are removed on log out.
- **Log events:** `LogEvent` with level `ERROR` or `CRITICAL` (per `min_log_level`), fed from
  `MainWindow.process_log_entry`, which already receives all of them.
- **Own events are ignored:** events whose sender is this GUI's own module name. The GUI logs its
  own errors (unreadable settings file, failed notification), and pyobs-core's notifier had an
  incident where its own log lines fed back into more alerts. Failing to send a notification is
  logged once at `WARNING`, never `ERROR`.
- `muted_modules`: nothing from these modules is considered, for state and log events, and they
  are left out of the startup summary.
- Settings are read at send time from `gui.settings.notifications`, so changes in the dialog apply
  without a restart.

### Startup summary

The first presence callback of each module that was connected at startup is initial state, not a
transition. Those in `ERROR` are collected, and one notification is sent when all initial
callbacks have arrived or after 3 s, whichever is first: "N modules in ERROR: a, b, c" (names cut
after a few). Modules that appear later, and any change after the first callback, are normal
events. A module that appears already in `ERROR` is therefore notified individually.

### Rate limiting

- **Per module, `rate_limit` seconds:** the first event sends immediately. Further events from the
  same module (state or log) within the window are counted, not sent. When the window ends with a
  non-zero count, one trailing notification "<module>: N more errors" is sent. `0` turns it off.
- **Global cap, fixed:** at most 5 notifications per 30 s. Above that they are counted and folded
  into one "+N more notifications" at the end of the window. The cap is a constant, not a setting,
  so the "every setting in the dialog and YAML" rule isn't affected. Revisit if it turns out to
  be wrong in practice.
- Both use an injectable clock, so the logic is tested without waiting.

### Authorization (macOS)

`desktop-notifier` has `has_authorisation()` and `request_authorisation()`. As far as I know macOS
asks the user once, on the first notification, and a refusal can only be undone in System
Settings. So the manager requests authorization when notifications are enabled (at startup in
standalone mode, or when the user turns it on in the dialog), and the test button reports a
refusal in the dialog ("Notifications are not allowed for pyobs-gui, see System Settings").
On the other platforms the library is expected to report authorized (not checked). See the spike list.

### Only when inactive

Checked at send time. If `only_when_inactive` and the application is active, nothing is sent (the
event is visible in the window anyway). Suppressed events don't count towards the rate limits.

### Click

The notification's `on_clicked` raises the window (`show()`, `raise_()`, `activateWindow()`), and
for a module `ERROR` selects that module with `MainWindow._select_page_by_name()`. Under Wayland the
raise may be refused (KDE: it is, see the spike list, item 3), so the handler also calls
`QApplication.alert()` to get the window noticed. The backend
callback may arrive on another thread (likely on Windows, unchecked), so it only emits a Qt
signal and the work happens on the main thread.

### Components

- `pyobs_gui/notifications.py`: `NotificationPolicy` (pure: events in, "send this" out, injectable
  clock; startup summary, rate limits, muting, own-sender filter) and `NotificationManager`
  (`QObject`: presence subscriptions, wiring to `MainWindow`, click handling).
- `pyobs_gui/notifier.py`: the `Notifier` interface and the `desktop-notifier` backend.
- `MainWindow` creates the manager in `open()` and tears it down in `discard_all_widgets()`, so
  log out and back in re-subscribes cleanly.
- Settings dialog, Notifications tab: a "Send test notification" button. It shows the backend
  error in the dialog if sending fails, which is the only place a user learns the desktop
  doesn't support it. A new addition, not in the settings design.
- YAML mode: `GUI.__init__` uses `enabled=False` when `notifications` is not given. The schema
  default stays `True`, which is what the standalone dialog starts from.

## Alternatives considered

- **`QSystemTrayIcon.showMessage()`** (the issue's suggestion): rejected, no tray icon wanted. It
  also silently does nothing on GNOME without an extension.
- **Subprocess `notify-send`:** Linux only, no click handling.
- **In-app only (window flashing, taskbar attention):** doesn't reach someone on another monitor
  or workspace, which is the point of the issue.

## Not verified yet, spike first

1. **Windows:** nothing here can test it. Does a toast appear without an installed shortcut or
   app identity, is the app name/icon right, does `on_clicked` fire, and on which thread.
2. **GNOME (checked 2026-10-04, GNOME Shell 50.1, Wayland, Kubuntu 26.04 with `gnome-session` added,
   `desktop-notifier` 6.2.0 under qasync):** the server reports notification spec version 1.2 and the
   capabilities `actions`, `body`, `body-markup`, `icon-static`, `persistence`, `sound` (no tray
   involved). `on_clicked` fires, and raising the window from the click does **not** work, same as
   on KDE: with the window in the background it stayed inactive after `showNormal()`/`raise_()`/
   `activateWindow()`. So the Wayland behavior is the same on both desktops, and the click handler
   has to rely on selecting the module page plus `QApplication.alert()`. Not checked: GNOME on X11
   (GNOME 50 seems to have no X11 session, no `gnome-session-xsession` package in the Ubuntu
   repository), toast lifetime, and whether the app needs a desktop entry to be listed properly
   in GNOME's notification list.
3. **KDE (checked 2026-10-04, Plasma 6.6.6, Wayland, `desktop-notifier` 6.2.0 under qasync):**
   toasts show without a tray, authorization reports granted, `on_clicked` fires and runs on the Qt
   main thread. **Raising the window from the click does not work under Wayland**: with the
   window in the background, `showNormal()`/`raise_()`/`activateWindow()` in the callback left it
   inactive (KWin keeps focus-stealing prevention, and the server reports notification spec
   version 1.2, so there is probably no activation token to pass on, from my recollection of the
   newer spec). Consequence for the design: the click handler still selects the module page, but
   brings the window to attention with `QApplication.alert()` instead of relying on a raise
   (to be checked on KDE under X11 and on GNOME). Not measured: how long a toast stays on screen
   and whether critical ones persist, because `on_dismissed` did not fire within 70 s for either
   a normal or a critical toast, so either it does not fire on expiry or they stay.
4. **Packaging:** `desktop-notifier` loads its backend per platform at runtime, which may not
   survive the `pyside6-deploy` standalone build. Build once and check.
5. **macOS:** nothing here can test it either. Does a build made with `pyside6-deploy` have a bundle
   identity that Notification Center accepts, does the authorization prompt appear and is the
   result reported correctly, does `on_clicked` fire. macOS normally doesn't show a banner for the
   frontmost app, which fits `only_when_inactive` but should be confirmed. All from memory.
6. **Urgency and expiry:** whether a "critical" notification stays on screen until dismissed on
   GNOME and KDE, and whether that is wanted for module `ERROR`. Start with normal urgency for
   log events and critical for module `ERROR`, and look at the result.

If 1, 2 or 4 fail for `desktop-notifier` on Linux or Windows, the alternative above replaces the
backend there without touching the rest. If 5 fails, macOS needs its own backend.

## Tests

- Policy: fake clock and fake notifier. Startup summary (including the 3 s timeout), per-module
  window and trailing "N more", global cap, `rate_limit = 0`, muted modules, own sender,
  `min_log_level`, inactive filtering, late-appearing module in `ERROR`, `ERROR` -> `READY` sends
  nothing.
- Manager: presence subscriptions follow module open/close and log out, click selects the module
  (state) or only raises (log).
- Backend: a fake `DesktopNotifier`, plus a failing one (logged once at `WARNING`, no loop).
- Manual, per OS (GNOME, KDE, Windows, macOS): toast shows, click raises the window, test button, app
  name and icon.
