import asyncio

import pytest
from PySide6 import QtCore

from pyobs_gui.accounts import SavedAccountsModel
from pyobs_gui.loginwindow import ConnectionRequest, LoginWindow, build_connection_request


def make_model(tmp_path) -> SavedAccountsModel:
    settings = QtCore.QSettings(str(tmp_path / "test_accounts.ini"), QtCore.QSettings.Format.IniFormat)
    return SavedAccountsModel(settings)


# ── build_connection_request (pure logic, no Qt widgets needed) ───────────────


def test_build_connection_request_requires_jid_and_password() -> None:
    assert build_connection_request("", "pw", False, "", "", False) is None
    assert build_connection_request("user@example.com", "", False, "", "", False) is None


def test_build_connection_request_without_server_override() -> None:
    request = build_connection_request("user@example.com", "secret", False, "ignored-host", "1234", False)
    assert request == ConnectionRequest(jid="user@example.com", password="secret", server=None, insecure_skip_tls=False)


def test_build_connection_request_with_server_override_host_and_port() -> None:
    request = build_connection_request("user@example.com", "secret", True, "example.com", "5223", False)
    assert request is not None
    assert request.server == "example.com:5223"


def test_build_connection_request_with_server_override_host_only() -> None:
    request = build_connection_request("user@example.com", "secret", True, "example.com", "", False)
    assert request is not None
    assert request.server == "example.com"


def test_build_connection_request_override_checked_but_host_blank_gives_no_server() -> None:
    """Matches XmppComm's own default (None -> normal DNS SRV lookup) -- an override checkbox
    with nothing typed in yet must not produce a bogus ":5223" server string."""
    request = build_connection_request("user@example.com", "secret", True, "", "5223", False)
    assert request is not None
    assert request.server is None


def test_build_connection_request_strips_whitespace_from_jid() -> None:
    request = build_connection_request("  user@example.com  ", "secret", False, "", "", False)
    assert request is not None
    assert request.jid == "user@example.com"


def test_build_connection_request_carries_insecure_skip_tls() -> None:
    request = build_connection_request("user@example.com", "secret", False, "", "", True)
    assert request is not None
    assert request.insecure_skip_tls is True


# ── LoginWindow ────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_login_window_starts_on_new_connection_form(tmp_path) -> None:
    window = LoginWindow(accounts=make_model(tmp_path))
    assert window._jid_field.text() == ""
    assert window._selected_account_id == ""
    window.close()


@pytest.mark.asyncio
async def test_login_window_lists_saved_accounts(tmp_path) -> None:
    model = make_model(tmp_path)
    model.add_account("user@example.com", label="My Telescope")

    window = LoginWindow(accounts=model)
    assert window._account_list.count() == 1
    assert window._account_list.item(0).text() == "My Telescope"
    window.close()


@pytest.mark.asyncio
async def test_login_window_selecting_account_prefills_fields(tmp_path) -> None:
    model = make_model(tmp_path)
    account_id = model.add_account("user@example.com", label="My Telescope", host="example.com", port=5223)

    window = LoginWindow(accounts=model)
    window._select_account(account_id)

    assert window._jid_field.text() == "user@example.com"
    assert window._label_field.text() == "My Telescope"
    assert window._override_server_checkbox.isChecked() is True
    assert window._host_field.text() == "example.com"
    assert window._port_field.text() == "5223"
    window.close()


@pytest.mark.asyncio
async def test_login_window_connect_resolves_wait_for_connect(tmp_path) -> None:
    window = LoginWindow(accounts=make_model(tmp_path))
    window._jid_field.setText("user@example.com")
    window._password_field.setText("secret")

    window._on_connect_clicked()
    request = await asyncio.wait_for(window.wait_for_connect(), timeout=1.0)

    assert request == ConnectionRequest(jid="user@example.com", password="secret", server=None, insecure_skip_tls=False)
    window.close()


@pytest.mark.asyncio
async def test_login_window_connect_with_empty_fields_does_not_resolve(tmp_path) -> None:
    window = LoginWindow(accounts=make_model(tmp_path))
    window._on_connect_clicked()  # jid/password both empty

    assert not window._connect_future.done()
    window.close()


@pytest.mark.asyncio
async def test_login_window_close_without_connecting_cancels_wait_for_connect(tmp_path) -> None:
    window = LoginWindow(accounts=make_model(tmp_path))
    window.close()

    with pytest.raises(asyncio.CancelledError):
        await asyncio.wait_for(window.wait_for_connect(), timeout=1.0)


@pytest.mark.asyncio
async def test_login_window_save_then_select_persists_account(tmp_path) -> None:
    model = make_model(tmp_path)
    window = LoginWindow(accounts=model)
    window._jid_field.setText("user@example.com")
    window._label_field.setText("My Telescope")

    window._on_save_clicked()

    accounts = model.list_accounts()
    assert len(accounts) == 1
    assert accounts[0].jid == "user@example.com"
    assert accounts[0].label == "My Telescope"
    assert window._selected_account_id == accounts[0].id
    window.close()


@pytest.mark.asyncio
async def test_login_window_delete_removes_account(tmp_path) -> None:
    model = make_model(tmp_path)
    account_id = model.add_account("user@example.com")

    window = LoginWindow(accounts=model)
    window._select_account(account_id)
    window._on_delete_clicked()

    assert model.list_accounts() == []
    assert window._selected_account_id == ""
    window.close()
