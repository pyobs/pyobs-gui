from typing import Any, Optional

import pytest

from pyobs.events import Event
from pyobs.interfaces import FitsHeaderEntry, IModule, Interface
from pyobs_gui import mainwindow as mw
from pyobs_gui.base import BaseWidget
from pyobs_gui.mainwindow import MainWidgetEntry, MainWindow, ModulePage
from pyobs_gui.modulegui import ModuleWindow

# -- fake "interfaces" (plain classes, not pyobs ABCs -- MAIN_WIDGETS matching is a plain
# isinstance() check, so a fake registry built from marker classes exercises exactly the same
# code path as the real one without needing to satisfy real interfaces' abstract methods) --------


class IMainA(Interface):
    """Stands in for a main widget with a declared entry-level sidebar fill (e.g. ICamera)."""


class IMainB(Interface):
    """Stands in for a second, independent main widget (e.g. IRoof)."""


class IPreferred1(Interface):
    """Stands in for a sidebar_preferred interface with its own standalone entry (e.g. IFilters)."""


class IPreferred2(Interface):
    """A second sidebar_preferred interface (e.g. ITemperatures)."""


class IFillGate(Interface):
    """Gates IMainA's declared sidebar fill (checked via comm.has_proxy)."""


class _FakeWidget(BaseWidget):
    """Minimal BaseWidget stand-in: records open()/discard(), can be made to fail its open()."""

    def __init__(self, label: Optional[str] = None, fail: bool = False, **kwargs: Any):
        super().__init__(**kwargs)
        self.label = label or type(self).__name__
        self.fail = fail
        self.opened = False
        self.discarded = False

    # pyrefly: ignore [bad-override]
    async def open(self, **kwargs: Any) -> None:
        if self.fail:
            raise RuntimeError(f"boom: {self.label}")
        self.opened = True

    async def discard(self) -> None:
        self.discarded = True
        await super().discard()

    def get_fits_headers(self, namespaces: Optional[list[str]] = None, **kwargs: Any) -> dict[str, FitsHeaderEntry]:
        hdr = super().get_fits_headers(namespaces, **kwargs)
        hdr[self.label] = FitsHeaderEntry(self.label, "")
        return hdr


class MainAWidget(_FakeWidget):
    pass


class MainBWidget(_FakeWidget):
    pass


class Preferred1Widget(_FakeWidget):
    pass


class Preferred2Widget(_FakeWidget):
    pass


class FillGateWidget(_FakeWidget):
    pass


class AlwaysWidget(_FakeWidget):
    pass


class ReplacementWidget(_FakeWidget):
    pass


class ExtraWidget(_FakeWidget):
    pass


class OverwriteWidget(_FakeWidget):
    pass


class CustomSidebarWidget(_FakeWidget):
    pass


FAKE_MAIN_WIDGETS = [
    MainWidgetEntry(IMainA, MainAWidget, "Main A", "fa5s.camera", sidebar=((IFillGate, FillGateWidget),)),
    MainWidgetEntry(IMainB, MainBWidget, "Main B", "ph.house"),
    MainWidgetEntry(IPreferred1, Preferred1Widget, "Preferred 1", "mdi.air-filter", sidebar_preferred=True),
    MainWidgetEntry(IPreferred2, Preferred2Widget, "Preferred 2", "mdi.thermometer", sidebar_preferred=True),
]
FAKE_ALWAYS_SIDEBAR_WIDGETS = (AlwaysWidget,)


# -- fake proxies (isinstance-matchable against the fake interfaces above) -----------------------


class ProxyMainAOnly(IMainA):
    pass


class ProxyMainAAndPreferred1(IMainA, IPreferred1):
    pass


class ProxyMainAAndMainB(IMainA, IMainB):
    pass


class ProxyPreferred1AndPreferred2(IPreferred1, IPreferred2):
    pass


class ProxyNoMatch:
    pass


class FakeModule(IMainA, IMainB):
    """Doubles as a Module for the ModuleWindow test -- just needs a `.name`."""

    def __init__(self, name: str = "modx"):
        self.name = name


# -- fake comm -------------------------------------------------------------------------------


class _ProxyCtx:
    def __init__(self, value: Any):
        self._value = value

    async def __aenter__(self) -> Any:
        return self._value

    async def __aexit__(self, *exc_info: Any) -> bool:
        return False


class _PermittedProxy:
    async def get_permitted_methods(self) -> list[str]:
        return ["anything"]


class _FakeComm:
    """Comm surface MainWindow._client_connected/_open_client/collect_main_widgets touch:
    a client list, a fixed "matchable" object returned by proxy(), has_proxy() gating declared
    sidebar fills, and no-op event (un)registration."""

    def __init__(self, matchable: Any = None, clients: Optional[list[str]] = None):
        self.matchable = matchable
        self.clients: list[str] = [] if clients is None else clients

    def proxy(self, client: str, interface: Any = None) -> _ProxyCtx:
        if interface is IModule:
            return _ProxyCtx(_PermittedProxy())
        return _ProxyCtx(self.matchable)

    async def has_proxy(self, client: str, interface: Any) -> bool:
        return isinstance(self.matchable, interface)

    async def clients_with_interface(self, interface: Any) -> list[str]:
        return []

    async def register_event(self, event_class: Any, handler: Any) -> None:
        pass

    async def unregister_event(self, event_class: Any, handler: Any) -> None:
        pass


def _make_window(
    monkeypatch: pytest.MonkeyPatch,
    matchable: Any = None,
    widgets: Optional[list[dict[str, Any]]] = None,
    sidebar: Optional[list[dict[str, Any]]] = None,
) -> MainWindow:
    monkeypatch.setattr(mw, "MAIN_WIDGETS", FAKE_MAIN_WIDGETS)
    monkeypatch.setattr(mw, "ALWAYS_SIDEBAR_WIDGETS", FAKE_ALWAYS_SIDEBAR_WIDGETS)
    window = MainWindow(show_shell=False, show_events=False, show_status=False, widgets=widgets, sidebar=sidebar)
    window._comm = _FakeComm(matchable=matchable)  # pyrefly: ignore [bad-assignment]
    return window


async def _connect_and_wait(window: MainWindow, client: str) -> bool:
    connected = await window._client_connected(Event(), client)
    if client in window._pending_opens:
        await window._pending_opens[client]
    return connected


def _get_page(window: MainWindow, client: str) -> ModulePage:
    page = window._widgets[client]
    assert isinstance(page, ModulePage)
    return page


@pytest.mark.asyncio
async def test_promotion_rule_demotes_sidebar_preferred_when_main_nonempty(qapp, monkeypatch) -> None:
    """Camera-like + Filter-like (sidebar_preferred): one tab (no tab bar), the sidebar_preferred
    match lands in the sidebar instead of getting its own tab -- regression test for the
    double-display bug the 2026-09-01 promotion rule fixed."""
    window = _make_window(monkeypatch, matchable=ProxyMainAAndPreferred1())
    try:
        assert await _connect_and_wait(window, "mod")

        page = _get_page(window, "mod")
        assert page.tab_widget is None  # single main widget -> no tab chrome
        assert [type(w) for w in page.widgets] == [MainAWidget]

        assert any(isinstance(w, Preferred1Widget) for w in page.sidebar_widgets)
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_promotion_rule_promotes_when_main_empty(qapp, monkeypatch) -> None:
    """Two sidebar_preferred-only matches (no plain main match) -- both promoted into tabs."""
    window = _make_window(monkeypatch, matchable=ProxyPreferred1AndPreferred2())
    try:
        assert await _connect_and_wait(window, "mod")

        page = _get_page(window, "mod")
        assert page.tab_widget is not None
        assert page.tab_widget.count() == 2
        assert {type(w) for w in page.widgets} == {Preferred1Widget, Preferred2Widget}
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_single_match_has_no_tab_chrome(qapp, monkeypatch) -> None:
    """A bare single-interface match still gets a ModulePage, just with no visible QTabWidget --
    the point of making ModulePage the universal host (D2), not conditional on >= 2 matches."""
    window = _make_window(monkeypatch, matchable=ProxyMainAOnly())
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")
        assert page.tab_widget is None
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_no_matching_interface_adds_no_page(qapp, monkeypatch) -> None:
    window = _make_window(monkeypatch, matchable=ProxyNoMatch())
    try:
        assert await _connect_and_wait(window, "mod") is False
        assert "mod" not in window._widgets
        assert window.listPages.count() == 0
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_custom_sidebar_visible_on_bare_module(qapp, monkeypatch) -> None:
    """A custom sidebar: entry for a single-match module is actually visible -- regression test
    for the "known wrinkle" the 2026-08-28 version deferred and the 2026-09-01 revision fixed."""
    window = _make_window(
        monkeypatch,
        matchable=ProxyMainAOnly(),
        sidebar=[{"module": "mod", "widget": CustomSidebarWidget}],
    )
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")
        assert any(isinstance(w, CustomSidebarWidget) for w in page.sidebar_widgets)
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_always_sidebar_widgets_present_regardless_of_promotion(qapp, monkeypatch) -> None:
    """Every module's sidebar contains ALWAYS_SIDEBAR_WIDGETS, including a module whose only
    matches were promoted into tabs (no "plain main" entry at all)."""
    window = _make_window(monkeypatch, matchable=ProxyPreferred1AndPreferred2())
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")
        assert any(isinstance(w, AlwaysWidget) for w in page.sidebar_widgets)
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_declared_sidebar_fill_gated_by_has_proxy(qapp, monkeypatch) -> None:
    """IMainA's declared `sidebar` tuple only fills in when comm.has_proxy() confirms the gate
    interface -- IFillGate here."""
    window = _make_window(monkeypatch, matchable=ProxyMainAAndMainB())  # no IFillGate
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")
        assert not any(isinstance(w, FillGateWidget) for w in page.sidebar_widgets)
    finally:
        window.deleteLater()

    class ProxyMainAWithGate(IMainA, IFillGate):
        pass

    window2 = _make_window(monkeypatch, matchable=ProxyMainAWithGate())
    try:
        assert await _connect_and_wait(window2, "mod")
        page2 = window2._widgets["mod"]
        assert any(isinstance(w, FillGateWidget) for w in page2.sidebar_widgets)
    finally:
        window2.deleteLater()


@pytest.mark.asyncio
async def test_custom_widget_extra_tab(qapp, monkeypatch) -> None:
    """No interface, no overwrite -- a custom widgets: entry is appended as an extra tab."""
    window = _make_window(
        monkeypatch,
        matchable=ProxyMainAOnly(),
        widgets=[{"module": "mod", "widget": ExtraWidget, "label": "Extra"}],
    )
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")
        assert page.tab_widget is not None
        assert page.tab_widget.count() == 2
        assert {type(w) for w in page.widgets} == {MainAWidget, ExtraWidget}
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_custom_widget_interface_replaces_slot(qapp, monkeypatch) -> None:
    """interface: IMainA replaces the same-interface slot in place, keeping tab order."""
    window = _make_window(
        monkeypatch,
        matchable=ProxyMainAAndMainB(),
        widgets=[{"module": "mod", "widget": ReplacementWidget, "interface": "IMainA"}],
    )
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")
        assert page.tab_widget is not None
        types = [type(w) for w in page.widgets]
        assert types == [ReplacementWidget, MainBWidget]  # slot 0 replaced, order kept
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_custom_widget_overwrite_replaces_whole_page(qapp, monkeypatch) -> None:
    """overwrite: true -- the page becomes exactly the custom entries."""
    window = _make_window(
        monkeypatch,
        matchable=ProxyMainAAndMainB(),
        widgets=[{"module": "mod", "widget": OverwriteWidget, "overwrite": True}],
    )
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")
        assert page.tab_widget is None
        assert [type(w) for w in page.widgets] == [OverwriteWidget]
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_disconnect_discards_every_tab_and_sidebar_widget(qapp, monkeypatch) -> None:
    window = _make_window(monkeypatch, matchable=ProxyMainAAndPreferred1())
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")
        tab_widgets = [w for w in page.widgets if isinstance(w, _FakeWidget)]
        sidebar_widgets = [w for w in page.sidebar_widgets if isinstance(w, _FakeWidget)]
        assert tab_widgets and sidebar_widgets
        assert len(tab_widgets) == len(page.widgets)
        assert len(sidebar_widgets) == len(page.sidebar_widgets)

        assert await window._client_disconnected(Event(), "mod")

        assert all(w.discarded for w in tab_widgets)
        assert all(w.discarded for w in sidebar_widgets)
        assert "mod" not in window._widgets
        assert "mod" not in window._pages
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_get_fits_headers_aggregates_tabs_and_sidebar(qapp, monkeypatch) -> None:
    window = _make_window(monkeypatch, matchable=ProxyPreferred1AndPreferred2())
    try:
        assert await _connect_and_wait(window, "mod")
        page = _get_page(window, "mod")

        hdr = page.get_fits_headers()
        assert "Preferred1Widget" in hdr
        assert "Preferred2Widget" in hdr
        assert "AlwaysWidget" in hdr
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_partial_open_failure_keeps_page_with_remaining_tab(qapp, monkeypatch) -> None:
    """One of two main widgets fails to open -> its tab is removed and discarded, the page
    (and the surviving tab) stays up."""
    window = _make_window(monkeypatch, matchable=ProxyMainAAndMainB())
    monkeypatch.setattr(MainBWidget, "__init__", lambda self, **kw: _FakeWidget.__init__(self, fail=True, **kw))
    try:
        assert await _connect_and_wait(window, "mod")

        assert "mod" in window._widgets
        page = _get_page(window, "mod")
        assert [type(w) for w in page.widgets] == [MainAWidget]
        assert page.tab_widget is not None
        assert page.tab_widget.count() == 1
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_all_widgets_failing_tears_down_client(qapp, monkeypatch) -> None:
    window = _make_window(monkeypatch, matchable=ProxyMainAOnly())
    monkeypatch.setattr(MainAWidget, "__init__", lambda self, **kw: _FakeWidget.__init__(self, fail=True, **kw))
    try:
        assert await _connect_and_wait(window, "mod")  # _client_connected itself still returns True
        assert "mod" not in window._widgets  # but _fail_open tore it down once the open failed
        assert "mod" not in window._pages
        assert not any(window.listPages.item(i).text() == "mod" for i in range(window.listPages.count()))
    finally:
        window.deleteLater()


@pytest.mark.asyncio
async def test_module_window_multi_interface_gets_tabbed_module_page(qapp, monkeypatch) -> None:
    monkeypatch.setattr(mw, "MAIN_WIDGETS", FAKE_MAIN_WIDGETS)
    monkeypatch.setattr(mw, "ALWAYS_SIDEBAR_WIDGETS", FAKE_ALWAYS_SIDEBAR_WIDGETS)

    class _StubGuiModule:
        def quit(self) -> None:
            pass

    window = ModuleWindow(_StubGuiModule())  # pyrefly: ignore [bad-argument-type]
    try:
        await window.open(
            module=FakeModule("mod"),  # pyrefly: ignore [bad-argument-type]
            comm=_FakeComm(matchable=FakeModule("mod")),
            vfs=None,
            observer=None,
        )
        page = window.centralWidget()
        assert isinstance(page, ModulePage)
        assert page.tab_widget is not None
        assert page.tab_widget.count() == 2
    finally:
        window.deleteLater()
