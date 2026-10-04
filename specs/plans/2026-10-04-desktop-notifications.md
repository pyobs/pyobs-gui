# Plan: desktop notifications for module ERROR and log ERROR/CRITICAL

Status: proposed. Design: `specs/2026-10-04-desktop-notifications.md`.
Issue: #168. Settings (`NotificationSettings`, the dialog) are implemented, see
`specs/plans/2026-10-04-settings-dialog.md`.

## Order and PRs

Machines: KDE is available locally, the others (GNOME, Windows, macOS) will take a while, so they
must not block the work.

- The policy (step 2) is pure Python and doesn't depend on the backend, it starts right away.
- The KDE spike (step 1) is quick and is the gate for starting the backend, manager and wiring
  (steps 3 to 5) with `desktop-notifier`. The other platforms are checked as machines become
  available. A platform that fails then gets its own backend behind the `Notifier` interface, which
  is what the interface is for.
- Release gate, before #168 is closed: every platform is either checked (result in the design
  doc) or listed as untested in the user docs. A platform without a working backend must degrade
  to one `WARNING` in the log, never an error or a crash (step 3).

Suggested PRs: (a) interface + policy, (b) backend + manager + wiring + dialog button.

## 1. Spike: does `desktop-notifier` work on all four platforms

Throwaway script, not committed, results go into the design doc's "Not verified yet" section
(replace each item with what was found). One script per machine: ask for authorization, send a
normal and a critical notification with `on_clicked`, print the thread the callback runs on,
send a second one while the script's own window is focused.

- [x] KDE (Plasma 6.6.6, Wayland), done 2026-10-04: toast shows, click fires `on_clicked` on the Qt
      thread. Raising the window from the click does **not** work (stays inactive), see the design
      doc. Still open for KDE: toast lifetime and critical urgency (`on_dismissed` never fired in
      70 s, needs a look at the screen), and KDE under X11.
- [x] GNOME (Shell 50.1, Wayland), done 2026-10-04: toast shows without a tray, click fires
      `on_clicked`, raising the window from the click does **not** work (same as KDE), see the
      design doc. Still open: toast lifetime and urgency (look at the screen), X11 (probably not
      available on GNOME 50), app identity in the notification list.
- [x] Windows (11 Pro 25H2, Python 3.13, run by an agent on the machine), done 2026-10-04: **no toast
      at all** without a Start Menu shortcut carrying the AppUserModelID (the registry key
      `desktop-notifier` writes is not enough, and nothing is reported as an error). With the
      shortcut: toast shows, click fires on the Qt thread, and the minimized window is restored
      and active after the click. Still open: app name and icon in the toast, seconds on screen
      for normal and critical, whether critical is sticky, whether `on_dismissed` fires when the
      user removes a toast from the Action Center.
- [ ] macOS (needs a machine, run from a pip install, no app bundle): authorization prompt appears
      and `has_authorisation()` reflects
      the answer, toast shows, click fires, behavior while the app is frontmost.
- [ ] Decision gate, per platform as results come in: write down "desktop-notifier" or
      "fallback" (QtDBus + Windows toast library, macOS needs its own backend) and update the
      design doc.

## 2. Interface and policy (no dependency, done)

- [x] `pyobs_gui/notifier.py`: `Notifier` protocol (`send(title, message, critical, on_clicked)`).
      The `FakeNotifier` that records calls comes with the manager tests in step 4, nothing uses it
      before that, and it belongs in `tests/`, not in the package.
- [x] `pyobs_gui/notifications.py`: `NotificationPolicy`, pure, injectable clock and application
      state. Events in (`start(modules)`, `module_state(module, state, error)`,
      `module_closed(module)`, `log(sender, level, message)`), notices out, plus `tick()` and
      `next_deadline()` for what is due by time alone (startup summary, trailing "N more", folded
      notices). The caller schedules the timer. The first presence per module after `start()` is
      initial state, the policy tracks that itself.
  - [x] Module `ERROR` transition notifies, `ERROR` -> `READY` and other states don't. A repeat
        of the same state and error text is not a transition.
  - [x] Log events at `min_log_level` and above notify, below don't.
  - [x] Muted modules: nothing, for state and log events, and not in the startup summary.
  - [x] Own sender (this GUI's module name) is ignored.
  - [x] Startup summary: initial `ERROR` states collected, one notification when all initial
        callbacks are in or after 3 s, names cut after a few. A single error is announced like
        any other. Later changes and late-appearing modules are normal events.
  - [x] Per-module `rate_limit`: first immediately, rest counted, one trailing "N more" at the end
        of the window, `0` turns it off.
  - [x] Global cap, 5 per 30 s, rest folded into one "+N more" (constants, not settings).
  - [x] `only_when_inactive`, with the application state passed in. Suppressed events don't count
        towards the rate limits. A trailing or folded notice is dropped if the application is
        active by the time it is due.
  - [x] `enabled = False` sends nothing and drops pending trailing notifications.
- [x] Tests for each line above with a fake clock (`tests/test_notifications.py`, 45). Checked
      by breaking the policy on purpose five ways (transition check, own sender, cap off by one,
      window end, inactive check): each is caught.

## 3. Backend (KDE, GNOME and Windows spikes done, macOS open)

- [x] Add the dependencies and relock: `desktop-notifier>=6.2,<7`, and `pywin32>=312` on Windows
      only (for the shortcut below).
- [x] `DesktopNotifierBackend` in `pyobs_gui/notifier_backend.py`: `app_name` `pyobs-gui`, urgency
      mapping (critical or normal), the library object built on first use, `on_clicked` relayed
      through a Qt signal so the callback always runs on the main thread, authorization checked
      (and asked for) before the first send and remembered once granted
      (`ensure_authorisation()`, which the manager and the dialog can call too). Errors are
      raised as `NotifierError` with a message for the user, which the dialog test button needs.
      Open: **no app icon**, the repository has no pyobs logo file, so the library's default
      (a Python icon) is shown. Needs a logo from Tim.
- [x] Failure handling: `GuardedNotifier` (in `pyobs_gui/notifier.py`) wraps a notifier for the
      application's own notifications: the first failure is logged once at `WARNING`, never
      `ERROR` (no log feedback loop), further ones are quiet until one succeeds again. The dialog
      test button uses the unguarded backend. On Windows a missing app identity is not an error
      at all, see the next item.
- [x] Windows app identity (`pyobs_gui/windows_identity.py`): before the library object is built
      the backend makes sure the Start Menu shortcut `pyobs-gui.lnk` exists, with the
      AppUserModelID `pyobs-gui` (what the library uses as its id), targeting however the app was
      started (the `pyobs-gui` launcher, or the interpreter with `-m pyobs_gui`). `desktop-notifier`
      only writes the registry key and cannot create the shortcut. An existing shortcut is left
      alone, a failure is a warning and the toast is still tried. **The COM part
      (`create_link_com`, pywin32) is untested**, everything around it is tested with a fake.
      Needs a run on Windows, see the open items below.
- [x] Tests: `tests/test_notifier_backend.py` (send arguments, urgency, built once and identity
      first, errors, authorization asked and remembered, click from another thread runs on the
      main thread, guard logs once and again after a success), `tests/test_windows_identity.py`.
      Checked by breaking the code on purpose four ways (click not relayed, authorization not
      remembered, guard logging every time, guard never resetting): each is caught.
- [ ] Windows: run `create_link_com` on a Windows machine (shortcut appears in the Start Menu, the
      toast shows afterwards, the shortcut is only created once). Same for a first run with a
      shortcut that already exists. Hand over to the Windows agent.
- [ ] Per-platform fallback backends, only for what the spikes mark as failing. None so far.

## 4. Manager and wiring (done, not yet tried live)

- [x] `NotificationManager` (`pyobs_gui/notificationmanager.py`, a `QObject`): owns the policy,
      a `Notifier` and one `QTimer` that is set from `policy.next_deadline()` after every call
      and fires `tick()`. Reads `gui.settings.notifications` at event time.
- [x] Presence: `comm.subscribe_presence(module, cb)` for every connected module at start, then
      for `ModuleOpenedEvent` (once per module), unsubscribe on `ModuleClosedEvent` and on close.
      The callback only emits a Qt signal, so it is handled on the main thread whichever thread
      comm uses. The policy tells initial state from transitions by itself.
- [x] Log events: the manager registers its own `LogEvent` handler, instead of being fed from
      `MainWindow.process_log_entry` as the design said. Same events, no change to the window,
      and the manager can be tested without one.
- [x] Click: `MainWindow.bring_to_front(module)` shows (restores if minimized), raises and
      activates the window, calls `QApplication.alert()` (the fallback where raising is refused,
      see the KDE/GNOME spike) and selects the page for a module `ERROR`. Page names are the
      module names (`_add_client`), a module without a page is a no-op. A log event only raises.
- [x] The manager is created by `GUI` (`_start_notifications()` after the window is shown), not by
      `MainWindow.open()`: `GUI` owns the settings and the module lifetime, and `MainWindow`
      stays testable without comm. A failure to start is a warning and doesn't keep the GUI from
      starting. It is stopped in `_logout()` before the comm is closed, and in `GUI.close()`.
      Log out and back in builds a new one through `open()`.
- [x] Permission: `ensure_authorisation()` of the backend is called when the manager starts with
      notifications enabled, and again when `settings_changed` fires with them enabled. A refusal
      is a warning in the log.
- [x] YAML mode: `GUI.__init__` uses `enabled=False` when `notifications` is not given (a
      `notifications:` block, even an empty one, switches it on). Standalone keeps the schema
      default, on.
- [x] Tests: `tests/test_notificationmanager.py` (subscriptions follow module open/close, state
      and log notices, own events ignored, startup summary and trailing notices via the timer,
      disabled, presence from another thread, close, permission, `bring_to_front`),
      `tests/test_gui_notifications.py` (start, click, failing start, close, logout order),
      `tests/test_settings.py` (YAML default). Checked by breaking the code on purpose seven ways
      (unsubscribe on close, dedupe, timer stop, own name, logout teardown, YAML default,
      page selection): each is caught.
- [ ] Live check on KDE and GNOME with `test/full.yaml`: an error in a dummy module shows a
      toast, the click selects the module and the window asks for attention, nothing while the
      window is active, the startup summary with a module already in `ERROR`. Not done, needs
      someone at the screen.
## 5. Dialog

- [ ] Notifications tab: "Send test notification" button. Runs through the backend, shows the
      error in the dialog if sending fails, and on macOS reports a refused authorization with
      the System Settings hint. On Windows a missing app identity gives no error, so the dialog
      text must say what to check if nothing appeared.
- [ ] Authorization is requested when notifications get enabled (startup in standalone mode, or
      the checkbox in the dialog).
- [ ] Tests: button calls the notifier, failure and refusal are shown, nothing sent when the
      dialog is cancelled.

## 6. Wrap-up

- [ ] Manual run on every platform from step 1: error in a dummy module (`test/full.yaml`), toast
      shows, click raises and selects, toast suppressed while the window is active, summary on
      connect with a module already in `ERROR`, flapping module folds into "N more".
- [ ] User docs: the `notifications:` YAML block, the dialog tab, what to do if nothing appears
      (per platform).
- [ ] `pyrefly`, `ruff`, `black`, full `pytest`.
- [ ] Update the status lines in `specs/index.md`, `specs/plans/index.md` and the design doc, and
      close #168.
