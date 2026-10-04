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

## 2. Interface and policy (no dependency, can start now)

- [ ] `pyobs_gui/notifier.py`: `Notifier` protocol (`send(title, message, critical, on_clicked)`)
      and a `FakeNotifier` for tests that records calls.
- [ ] `pyobs_gui/notifications.py`: `NotificationPolicy`, pure, injectable clock. Events in
      (`module_state(module, state, error, initial)`, `log(sender, level, message)`), decisions
      out (what to send, plus timers to schedule for the startup summary and trailing "N more").
  - [ ] Module `ERROR` transition notifies, `ERROR` -> `READY` and other states don't.
  - [ ] Log events at `min_log_level` and above notify, below don't.
  - [ ] Muted modules: nothing, for state and log events, and not in the startup summary.
  - [ ] Own sender (this GUI's module name) is ignored.
  - [ ] Startup summary: initial `ERROR` states collected, one notification when all initial
        callbacks are in or after 3 s, names cut after a few. Later changes and late-appearing
        modules are normal events.
  - [ ] Per-module `rate_limit`: first immediately, rest counted, one trailing "N more" at the end
        of the window, `0` turns it off.
  - [ ] Global cap, 5 per 30 s, rest folded into one "+N more" (constants, not settings).
  - [ ] `only_when_inactive`, with the application state passed in. Suppressed events don't count
        towards the rate limits.
  - [ ] `enabled = False` sends nothing and drops pending trailing notifications.
- [ ] Tests for each line above with a fake clock.

## 3. Backend (after the spike)

- [ ] Add the dependency (`desktop-notifier`, floor from the spike) and relock.
- [ ] `DesktopNotifierBackend` in `pyobs_gui/notifier.py`: `app_name` `pyobs-gui`, app icon,
      urgency mapping, `on_clicked` turned into a Qt signal emission (the callback may be on
      another thread), authorization check on enable.
- [ ] Failure handling: a failed send is logged once at `WARNING`, never `ERROR` (no log
      feedback loop), and later failures stay quiet. Note that on Windows a missing app identity
      is not an error at all, the toast is silently dropped (see the Windows spike result).
- [ ] Windows app identity: before the first toast, make sure a Start Menu shortcut with the
      AppUserModelID `pyobs-gui` exists, targeting however the app was started (interpreter or the
      `pyobs-gui` launcher). First check whether `desktop-notifier` can create it, otherwise
      create it ourselves (COM `IPropertyStore` via `pywin32` or `comtypes`, Windows-only
      dependency). No installer exists (the standalone binary was rejected). The registry key the
      library writes is not enough on Windows 11.
- [ ] Tests with a fake `DesktopNotifier`: send arguments, click marshalled to the main thread,
      failing backend logs once at `WARNING`.
- [ ] Per-platform fallback backends, only for what the spike marked as failing.

## 4. Manager and wiring

- [ ] `NotificationManager` (`QObject`): owns the policy, a `Notifier` and the timers
      (`QTimer` for the summary and the trailing notifications). Reads
      `gui.settings.notifications` at event time.
- [ ] Presence: subscribe to `comm.subscribe_presence(module, cb)` for every connected module
      (initial list at start, then `ModuleOpenedEvent`/`ModuleClosedEvent`), unsubscribe on
      close and on log out. The callback marks the first call per module as initial.
- [ ] Log events: feed from `MainWindow.process_log_entry`.
- [ ] Click: raise the window; for a module `ERROR` also `_select_page_by_name(module)`; for a log
      event only raise. Check that the page name really equals the module name.
- [ ] `MainWindow.open()` creates the manager, `discard_all_widgets()` tears it down. Log out and
      back in re-subscribes cleanly (test with the existing logout flow).
- [ ] YAML mode: `GUI.__init__` uses `enabled=False` when `notifications` is not given.
- [ ] Tests: subscriptions follow module open/close and log out, click behavior for state and log
      events, disabled by default in YAML mode, enabled by default in standalone.

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
