from typing import Any

import pytest
from pyobs.utils.enums import ModuleState

from pyobs_gui.notifications import GLOBAL_CAP, GLOBAL_WINDOW, MAX_MESSAGE, STARTUP_WAIT, NotificationPolicy, Notice
from pyobs_gui.settings import NotificationSettings

ERROR = ModuleState.ERROR
READY = ModuleState.READY


class Clock:
    def __init__(self) -> None:
        self.now = 1000.0

    def __call__(self) -> float:
        return self.now

    def advance(self, seconds: float) -> None:
        self.now += seconds


class Env:
    """A policy with settings, clock and application state the test can change."""

    def __init__(self, **settings: Any) -> None:
        self.settings = NotificationSettings(**settings)
        self.clock = Clock()
        self.active = False
        self.policy = NotificationPolicy(
            settings=lambda: self.settings,
            own_name="gui",
            clock=self.clock,
            app_active=lambda: self.active,
        )

    def tick_at_deadline(self) -> list[Notice]:
        deadline = self.policy.next_deadline()
        assert deadline is not None
        self.clock.now = deadline
        return self.policy.tick()


@pytest.fixture
def env() -> Env:
    return Env()


# ── module state ──────────────────────────────────────────────────────────


def test_transition_into_error_notifies(env: Env) -> None:
    assert env.policy.module_state("cam", READY) == []
    assert env.policy.module_state("cam", ERROR, "no filter wheel") == [
        Notice("cam: ERROR", "no filter wheel", True, "cam")
    ]


def test_error_without_text_still_says_something(env: Env) -> None:
    (notice,) = env.policy.module_state("cam", ERROR)
    assert notice.message


def test_leaving_error_notifies_nothing(env: Env) -> None:
    env.policy.module_state("cam", ERROR, "x")
    assert env.policy.module_state("cam", READY) == []
    assert env.policy.module_state("cam", ModuleState.CLOSED) == []


def test_other_states_notify_nothing(env: Env) -> None:
    for state in (READY, ModuleState.STARTING, ModuleState.LOCAL, ModuleState.CLOSED):
        assert env.policy.module_state("cam", state) == []


def test_repeated_identical_error_is_not_a_new_transition() -> None:
    env = Env(rate_limit=0)
    assert len(env.policy.module_state("cam", ERROR, "x")) == 1
    assert env.policy.module_state("cam", ERROR, "x") == []
    assert len(env.policy.module_state("cam", ERROR, "y")) == 1
    env.policy.module_state("cam", READY)
    assert len(env.policy.module_state("cam", ERROR, "y")) == 1


# ── log events ────────────────────────────────────────────────────────────


@pytest.mark.parametrize("level", ["DEBUG", "INFO", "WARNING"])
def test_log_below_error_is_ignored(env: Env, level: str) -> None:
    assert env.policy.log("cam", level, "msg") == []


def test_log_error_and_critical_notify(env: Env) -> None:
    assert env.policy.log("cam", "ERROR", "boom") == [Notice("cam: ERROR", "boom", False, None)]
    assert env.policy.log("dome", "CRITICAL", "fire") == [Notice("dome: CRITICAL", "fire", True, None)]


def test_min_log_level_critical() -> None:
    env = Env(min_log_level="CRITICAL")
    assert env.policy.log("cam", "ERROR", "boom") == []
    assert len(env.policy.log("cam", "CRITICAL", "boom")) == 1


def test_long_log_messages_are_cut(env: Env) -> None:
    (notice,) = env.policy.log("cam", "ERROR", "x" * 1000)
    assert len(notice.message) == MAX_MESSAGE and notice.message.endswith("...")


def test_log_click_only_raises_but_state_click_selects_the_module(env: Env) -> None:
    assert env.policy.log("cam", "ERROR", "boom")[0].module is None
    assert env.policy.module_state("dome", ERROR, "x")[0].module == "dome"


# ── muting and own events ─────────────────────────────────────────────────


def test_muted_modules_are_ignored_for_state_and_log() -> None:
    env = Env(muted_modules=["weather"])
    assert env.policy.module_state("weather", ERROR, "x") == []
    assert env.policy.log("weather", "CRITICAL", "x") == []
    assert len(env.policy.module_state("cam", ERROR, "x")) == 1


def test_muting_applies_to_the_current_settings(env: Env) -> None:
    assert len(env.policy.log("weather", "ERROR", "x")) == 1
    env.clock.advance(60)
    env.settings.muted_modules = ["weather"]
    assert env.policy.log("weather", "ERROR", "x") == []


def test_own_events_are_ignored(env: Env) -> None:
    assert env.policy.log("gui", "CRITICAL", "could not load settings") == []
    assert env.policy.module_state("gui", ERROR, "x") == []


# ── startup summary ───────────────────────────────────────────────────────


def test_startup_errors_are_announced_together_once_all_have_reported(env: Env) -> None:
    assert env.policy.start(["a", "b", "c"]) == []
    assert env.policy.module_state("a", ERROR, "x") == []
    assert env.policy.module_state("b", READY) == []
    assert env.policy.module_state("c", ERROR, "y") == [Notice("2 modules in ERROR", "a, c", True, None)]
    assert env.policy.next_deadline() is None


def test_startup_summary_after_timeout_if_a_module_never_reports(env: Env) -> None:
    env.policy.start(["a", "b", "c"])
    env.policy.module_state("a", ERROR, "x")
    env.policy.module_state("b", ERROR, "y")
    assert env.policy.next_deadline() == env.clock.now + STARTUP_WAIT
    env.clock.advance(STARTUP_WAIT - 0.1)
    assert env.policy.tick() == []
    env.clock.advance(0.2)
    assert env.policy.tick() == [Notice("2 modules in ERROR", "a, b", True, None)]
    assert env.policy.next_deadline() is None


def test_a_single_startup_error_is_announced_like_any_other(env: Env) -> None:
    env.policy.start(["a", "b"])
    env.policy.module_state("b", READY)
    assert env.policy.module_state("a", ERROR, "x") == [Notice("a: ERROR", "x", True, "a")]


def test_startup_without_errors_notifies_nothing(env: Env) -> None:
    env.policy.start(["a", "b"])
    env.policy.module_state("a", READY)
    assert env.policy.module_state("b", READY) == []


def test_start_without_modules_waits_for_nothing(env: Env) -> None:
    assert env.policy.start([]) == []
    assert env.policy.next_deadline() is None


def test_startup_summary_lists_a_few_names_only(env: Env) -> None:
    names = [f"m{i}" for i in range(8)]
    env.policy.start(names)
    notices = []
    for name in names:
        notices += env.policy.module_state(name, ERROR, "x")
    assert notices == [Notice("8 modules in ERROR", "m0, m1, m2, m3, m4 and 3 more", True, None)]


def test_muted_modules_are_left_out_of_the_summary() -> None:
    env = Env(muted_modules=["weather"])
    env.policy.start(["a", "b", "weather"])
    env.policy.module_state("weather", ERROR, "x")
    env.policy.module_state("a", ERROR, "x")
    assert env.policy.module_state("b", READY) == [Notice("a: ERROR", "x", True, "a")]


def test_modules_after_the_summary_are_normal_events(env: Env) -> None:
    env.policy.start(["a"])
    env.policy.module_state("a", ERROR, "x")
    # a module that was not there at startup, appearing in ERROR, notifies on its own
    assert env.policy.module_state("late", ERROR, "y") == [Notice("late: ERROR", "y", True, "late")]


def test_changes_after_the_first_presence_are_transitions(env: Env) -> None:
    env.policy.start(["a", "b"])
    env.policy.module_state("a", READY)
    env.policy.module_state("b", READY)
    assert env.policy.module_state("a", ERROR, "x") == [Notice("a: ERROR", "x", True, "a")]


def test_a_module_closing_during_startup_is_not_waited_for(env: Env) -> None:
    env.policy.start(["a", "b"])
    env.policy.module_state("a", ERROR, "x")
    assert env.policy.module_closed("b") == [Notice("a: ERROR", "x", True, "a")]


# ── per-module rate limit ─────────────────────────────────────────────────


def test_first_event_sends_the_rest_in_the_window_are_counted(env: Env) -> None:
    assert len(env.policy.log("cam", "ERROR", "1")) == 1
    for _ in range(3):
        env.clock.advance(1)
        assert env.policy.log("cam", "ERROR", "again") == []
    assert env.policy.next_deadline() == 1000.0 + 10
    assert env.tick_at_deadline() == [Notice("cam: 3 more", "3 more since the last notification", False, None)]


def test_a_module_that_keeps_failing_gets_one_notice_per_window(env: Env) -> None:
    env.policy.log("cam", "ERROR", "1")
    env.clock.advance(1)
    env.policy.log("cam", "ERROR", "2")
    assert len(env.tick_at_deadline()) == 1
    # the next window started with that notice, and nothing happens in it
    deadline = env.policy.next_deadline()
    assert deadline is None or deadline > env.clock.now
    env.clock.advance(1)
    env.policy.log("cam", "ERROR", "3")
    assert env.tick_at_deadline() == [Notice("cam: 1 more", "1 more since the last notification", False, None)]


def test_after_a_quiet_window_the_next_event_sends_immediately(env: Env) -> None:
    env.policy.log("cam", "ERROR", "1")
    env.clock.advance(11)
    assert env.policy.next_deadline() is None
    assert len(env.policy.log("cam", "ERROR", "2")) == 1


def test_events_after_the_window_ended_bring_the_trailing_notice_with_them(env: Env) -> None:
    env.policy.log("cam", "ERROR", "1")
    env.clock.advance(1)
    env.policy.log("cam", "ERROR", "2")
    env.clock.advance(20)  # nobody called tick()
    notices = env.policy.log("cam", "ERROR", "3")
    assert [n.title for n in notices] == ["cam: 1 more"]


def test_modules_have_separate_windows(env: Env) -> None:
    assert len(env.policy.log("a", "ERROR", "x")) == 1
    assert len(env.policy.log("b", "ERROR", "x")) == 1


def test_state_and_log_of_one_module_share_a_window(env: Env) -> None:
    assert len(env.policy.module_state("cam", ERROR, "x")) == 1
    assert env.policy.log("cam", "ERROR", "y") == []
    # a state change was part of it, so a click on the trailing notice selects the module
    assert env.tick_at_deadline() == [Notice("cam: 1 more", "1 more since the last notification", False, "cam")]


def test_rate_limit_zero_turns_the_window_off() -> None:
    env = Env(rate_limit=0)
    assert len(env.policy.log("cam", "ERROR", "1")) == 1
    assert len(env.policy.log("cam", "ERROR", "2")) == 1
    assert env.policy.next_deadline() is None


def test_trailing_notice_is_dropped_if_the_module_got_muted(env: Env) -> None:
    env.policy.log("cam", "ERROR", "1")
    env.policy.log("cam", "ERROR", "2")
    env.settings.muted_modules = ["cam"]
    assert env.tick_at_deadline() == []


# ── global cap ────────────────────────────────────────────────────────────


def test_global_cap_folds_the_rest_into_one_notice(env: Env) -> None:
    sent = []
    for i in range(GLOBAL_CAP + 3):
        sent += env.policy.module_state(f"m{i}", ERROR, "x")
    assert len(sent) == GLOBAL_CAP
    assert env.policy.next_deadline() == 1000.0 + GLOBAL_WINDOW
    assert env.tick_at_deadline() == [Notice("+3 more notifications", "Open pyobs-gui for details.", False, None)]
    assert env.policy.next_deadline() is None


def test_global_cap_makes_room_as_time_passes(env: Env) -> None:
    for i in range(GLOBAL_CAP):
        env.policy.module_state(f"m{i}", ERROR, "x")
        env.clock.advance(1)
    assert env.policy.module_state("extra", ERROR, "x") == []
    env.clock.advance(GLOBAL_WINDOW)
    assert len(env.policy.module_state("again", ERROR, "x")) == 1 + 1  # the event and the "+1 more"


def test_startup_summary_counts_as_one_notification(env: Env) -> None:
    names = [f"m{i}" for i in range(20)]
    env.policy.start(names)
    notices = []
    for name in names:
        notices += env.policy.module_state(name, ERROR, "x")
    assert len(notices) == 1
    for i in range(GLOBAL_CAP - 1):
        assert len(env.policy.log(f"x{i}", "ERROR", "x")) == 1
    assert env.policy.log("one-too-many", "ERROR", "x") == []


# ── only when inactive ────────────────────────────────────────────────────


def test_nothing_while_the_application_is_active(env: Env) -> None:
    env.active = True
    assert env.policy.module_state("cam", ERROR, "x") == []
    assert env.policy.log("cam", "CRITICAL", "x") == []


def test_active_events_do_not_use_up_the_rate_limit_or_the_cap(env: Env) -> None:
    env.active = True
    for i in range(GLOBAL_CAP + 2):
        env.policy.log("cam", "ERROR", str(i))
    assert env.policy.next_deadline() is None
    env.active = False
    assert len(env.policy.log("cam", "ERROR", "now")) == 1


def test_inactive_filter_can_be_turned_off() -> None:
    env = Env(only_when_inactive=False)
    env.active = True
    assert len(env.policy.log("cam", "ERROR", "x")) == 1


def test_trailing_notice_is_dropped_if_the_user_is_looking_by_then(env: Env) -> None:
    env.policy.log("cam", "ERROR", "1")
    env.policy.log("cam", "ERROR", "2")
    env.active = True
    assert env.tick_at_deadline() == []


def test_startup_summary_respects_the_inactive_filter(env: Env) -> None:
    env.policy.start(["a", "b"])
    env.policy.module_state("a", ERROR, "x")
    env.active = True
    assert env.policy.module_state("b", ERROR, "y") == []


# ── enabled ───────────────────────────────────────────────────────────────


def test_disabled_sends_nothing() -> None:
    env = Env(enabled=False)
    assert env.policy.module_state("cam", ERROR, "x") == []
    assert env.policy.log("cam", "CRITICAL", "x") == []
    assert env.policy.tick() == []
    assert env.policy.next_deadline() is None


def test_disabling_drops_pending_notices_and_enabling_starts_clean(env: Env) -> None:
    env.policy.log("cam", "ERROR", "1")
    env.policy.log("cam", "ERROR", "2")
    assert env.policy.next_deadline() is not None
    env.settings.enabled = False
    assert env.policy.tick() == []
    assert env.policy.next_deadline() is None
    env.settings.enabled = True
    env.clock.advance(1)
    assert len(env.policy.log("cam", "ERROR", "3")) == 1


def test_state_seen_while_disabled_counts_as_the_previous_state() -> None:
    env = Env(enabled=False)
    env.policy.module_state("cam", ERROR, "x")
    env.settings.enabled = True
    # it already was in ERROR before notifications were switched on, no transition
    assert env.policy.module_state("cam", ERROR, "x") == []


def test_a_stale_window_does_not_swallow_the_startup_notice(env: Env) -> None:
    env.policy.log("a", "ERROR", "earlier")  # starts a window for "a"
    env.clock.advance(1)
    env.policy.start(["a", "b"])
    env.policy.module_state("a", ERROR, "x")
    env.clock.advance(20)  # the window is over, nothing called tick()
    assert env.policy.module_closed("b") == [Notice("a: ERROR", "x", True, "a")]
