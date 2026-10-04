"""Which events become a desktop notification, and when -- see
specs/2026-10-04-desktop-notifications.md.

`NotificationPolicy` is pure: events go in, notices to show come out, time comes from an injected
clock, and nothing is scheduled. Whoever owns it (the manager) calls `tick()` at `next_deadline()`
to get what is due by time alone: the startup summary, "N more" for a module that kept failing,
and notices held back by the global cap.
"""

from __future__ import annotations

import time
from collections import deque
from dataclasses import dataclass
from typing import TYPE_CHECKING

from pyobs.utils.enums import ModuleState

if TYPE_CHECKING:
    from collections.abc import Callable, Iterable

    from .settings import NotificationSettings

# at most this many notifications in this many seconds, the rest is folded into one
GLOBAL_CAP = 5
GLOBAL_WINDOW = 30.0
# how long to wait for the first presence of every module that was connected at startup
STARTUP_WAIT = 3.0
# longer log messages are cut
MAX_MESSAGE = 200
# module names listed in the startup summary
MAX_NAMES = 5


@dataclass(frozen=True)
class Notice:
    title: str
    message: str
    critical: bool
    # module whose page a click selects, None: a click only raises the window
    module: str | None = None


@dataclass
class _Window:
    """Rate limit window of one module: what happened in it after the notification it started."""

    end: float
    suppressed: int = 0
    select_module: bool = False


def _truncate(text: str) -> str:
    return text if len(text) <= MAX_MESSAGE else text[: MAX_MESSAGE - 3] + "..."


class NotificationPolicy:
    def __init__(
        self,
        settings: Callable[[], NotificationSettings],
        own_name: str,
        clock: Callable[[], float] = time.monotonic,
        app_active: Callable[[], bool] = lambda: False,
    ) -> None:
        """
        Args:
            settings: Current notification settings, read whenever an event arrives.
            own_name: Name of this GUI's own module. Its events are ignored, it logs its own
                problems, and reacting to those would feed back into more notifications.
            clock: Seconds, only differences matter.
            app_active: Whether the application is the active one (checked when an event arrives).
        """
        self._settings = settings
        self._own_name = own_name
        self._clock = clock
        self._app_active = app_active

        self._states: dict[str, tuple[ModuleState, str]] = {}
        self._windows: dict[str, _Window] = {}

        # startup summary: modules whose first presence is still missing, and the errors found
        self._startup_pending: set[str] = set()
        self._startup_errors: dict[str, str] = {}
        self._startup_deadline = 0.0

        # global cap
        self._sent: deque[float] = deque()
        self._folded = 0
        self._fold_deadline = 0.0

    # ── events ───────────────────────────────────────────────────────────────

    def start(self, modules: Iterable[str]) -> list[Notice]:
        """Begin the startup phase: the first presence of each of these modules is initial state,
        not a transition. The errors among them are announced together once all have reported,
        or after `STARTUP_WAIT`."""
        self._startup_pending = set(modules)
        self._startup_errors = {}
        self._startup_deadline = self._clock() + STARTUP_WAIT
        return [] if self._startup_pending else self._flush_startup()

    def module_state(self, module: str, state: ModuleState, error: str = "") -> list[Notice]:
        """A presence update. Only the transition into ERROR notifies."""
        settings = self._settings()
        previous = self._states.get(module)
        self._states[module] = (state, error)
        if not settings.enabled:
            self._reset()
            return []
        notices = self._expire(self._clock())
        ignored = module == self._own_name or module in settings.muted_modules

        if module in self._startup_pending:
            self._startup_pending.discard(module)
            if state == ModuleState.ERROR and not ignored:
                self._startup_errors[module] = error
            if not self._startup_pending:
                notices += self._flush_startup()
            return notices

        if state != ModuleState.ERROR or ignored or previous == (state, error):
            return notices
        notices += self._event(module, f"{module}: ERROR", error or "Module is in ERROR state", True, True)
        return notices

    def module_closed(self, module: str) -> list[Notice]:
        """A module went away: forget it, and stop waiting for its first presence."""
        self._states.pop(module, None)
        self._windows.pop(module, None)
        if module in self._startup_pending:
            self._startup_pending.discard(module)
            if not self._startup_pending and self._settings().enabled:
                return self._flush_startup()
        return []

    def log(self, sender: str, level: str, message: str) -> list[Notice]:
        """A log event from `sender`. Notifies if `level` reaches `min_log_level`."""
        settings = self._settings()
        if not settings.enabled:
            self._reset()
            return []
        notices = self._expire(self._clock())
        levels = {"ERROR", "CRITICAL"} if settings.min_log_level == "ERROR" else {"CRITICAL"}
        if sender == self._own_name or sender in settings.muted_modules or level.upper() not in levels:
            return notices
        notices += self._event(
            sender, f"{sender}: {level.upper()}", _truncate(message), level.upper() == "CRITICAL", False
        )
        return notices

    def tick(self) -> list[Notice]:
        """What is due by time alone. Call at `next_deadline()`, calling it more often is harmless."""
        if not self._settings().enabled:
            self._reset()
            return []
        now = self._clock()
        notices = self._expire(now)
        if self._startup_pending and now >= self._startup_deadline:
            notices += self._flush_startup()
        return notices

    def next_deadline(self) -> float | None:
        """Clock time at which `tick()` has something to do, None if nothing is pending."""
        if not self._settings().enabled:
            return None
        deadlines = [window.end for window in self._windows.values() if window.suppressed > 0]
        if self._startup_pending:
            deadlines.append(self._startup_deadline)
        if self._folded > 0:
            deadlines.append(self._fold_deadline)
        return min(deadlines) if deadlines else None

    # ── internals ────────────────────────────────────────────────────────────

    def _reset(self) -> None:
        """Notifications are off: drop everything that was waiting to be announced."""
        self._windows.clear()
        self._startup_pending = set()
        self._startup_errors = {}
        self._folded = 0

    def _event(self, key: str, title: str, message: str, critical: bool, select_module: bool) -> list[Notice]:
        """An event that passed the filters on its content. Applies the inactive check and the
        per-module rate limit, then hands over to the global cap."""
        settings = self._settings()
        if settings.only_when_inactive and self._app_active():
            return []

        now = self._clock()
        window = self._windows.get(key)
        if window is not None and now < window.end:
            window.suppressed += 1
            window.select_module = window.select_module or select_module
            return []
        if settings.rate_limit > 0:
            self._windows[key] = _Window(end=now + settings.rate_limit, select_module=select_module)
        return self._deliver(Notice(title, message, critical, key if select_module else None))

    def _deliver(self, notice: Notice) -> list[Notice]:
        """Global cap: send, or count it for the "+N more" notice."""
        now = self._clock()
        self._purge_sent(now)
        if len(self._sent) < GLOBAL_CAP:
            self._sent.append(now)
            return [notice]
        self._folded += 1
        self._fold_deadline = self._sent[0] + GLOBAL_WINDOW
        return []

    def _purge_sent(self, now: float) -> None:
        while self._sent and self._sent[0] <= now - GLOBAL_WINDOW:
            self._sent.popleft()

    def _expire(self, now: float) -> list[Notice]:
        """Rate limit windows that ended, and the global cap once it has room again. Anything that
        became pointless meanwhile is dropped: the module got muted, or the user is looking at the
        application now."""
        notices: list[Notice] = []
        settings = self._settings()
        looking = settings.only_when_inactive and self._app_active()
        for key, window in list(self._windows.items()):
            if now < window.end:
                continue
            if window.suppressed == 0 or key in settings.muted_modules:
                del self._windows[key]
                continue
            n = window.suppressed
            select = key if window.select_module else None
            # still failing, so the next window starts right away
            window.end = now + settings.rate_limit
            window.suppressed = 0
            if not looking:
                notices += self._deliver(
                    Notice(f"{key}: {n} more", f"{n} more since the last notification", False, select)
                )

        if self._folded > 0 and now >= self._fold_deadline:
            self._purge_sent(now)
            if looking:
                self._folded = 0
            elif len(self._sent) < GLOBAL_CAP:
                self._sent.append(now)
                notices.append(Notice(f"+{self._folded} more notifications", "Open pyobs-gui for details.", False))
                self._folded = 0
            else:
                self._fold_deadline = self._sent[0] + GLOBAL_WINDOW
        return notices

    def _flush_startup(self) -> list[Notice]:
        errors = self._startup_errors
        self._startup_pending = set()
        self._startup_errors = {}
        if not errors or not self._settings().enabled:
            return []
        if len(errors) == 1:
            ((module, error),) = errors.items()
            return self._event(module, f"{module}: ERROR", error or "Module is in ERROR state", True, True)
        settings = self._settings()
        if settings.only_when_inactive and self._app_active():
            return []
        names = sorted(errors)
        shown = ", ".join(names[:MAX_NAMES])
        if len(names) > MAX_NAMES:
            shown += f" and {len(names) - MAX_NAMES} more"
        return self._deliver(Notice(f"{len(names)} modules in ERROR", shown, True))


__all__ = ["Notice", "NotificationPolicy"]
