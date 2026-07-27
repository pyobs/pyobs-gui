from PySide6 import QtCore

from pyobs_gui.accounts import SavedAccountsModel


def make_model(tmp_path) -> SavedAccountsModel:
    """An ini-backed, per-test-isolated QSettings -- never touches the real user's settings."""
    settings = QtCore.QSettings(str(tmp_path / "test_accounts.ini"), QtCore.QSettings.Format.IniFormat)
    return SavedAccountsModel(settings)


def test_list_accounts_empty_initially(tmp_path) -> None:
    model = make_model(tmp_path)
    assert model.list_accounts() == []


def test_add_account_persists_fields(tmp_path) -> None:
    model = make_model(tmp_path)

    account_id = model.add_account("user@example.com", label="My Telescope", host="1.2.3.4", port=5222)

    accounts = model.list_accounts()
    assert len(accounts) == 1
    assert accounts[0].id == account_id
    assert accounts[0].jid == "user@example.com"
    assert accounts[0].label == "My Telescope"
    assert accounts[0].host == "1.2.3.4"
    assert accounts[0].port == 5222


def test_account_by_id_returns_none_for_unknown_id(tmp_path) -> None:
    model = make_model(tmp_path)
    assert model.account_by_id("does-not-exist") is None


def test_update_account_keeps_id_stable(tmp_path) -> None:
    """The whole point of a stable id: renaming jid/label must not change it, since it's what a
    stored password is keyed on."""
    model = make_model(tmp_path)
    account_id = model.add_account("old@example.com", label="Old Label")

    model.update_account(account_id, "new@example.com", label="New Label")

    account = model.account_by_id(account_id)
    assert account is not None
    assert account.id == account_id
    assert account.jid == "new@example.com"
    assert account.label == "New Label"


def test_remove_account(tmp_path) -> None:
    model = make_model(tmp_path)
    keep_id = model.add_account("keep@example.com")
    remove_id = model.add_account("remove@example.com")

    model.remove_account(remove_id)

    accounts = model.list_accounts()
    assert [a.id for a in accounts] == [keep_id]


def test_multiple_accounts_independent(tmp_path) -> None:
    model = make_model(tmp_path)
    id1 = model.add_account("one@example.com", label="One")
    id2 = model.add_account("two@example.com", label="Two")

    model.update_account(id1, "one@example.com", label="One Updated")

    accounts = {a.id: a for a in model.list_accounts()}
    assert accounts[id1].label == "One Updated"
    assert accounts[id2].label == "Two"


def test_last_selected_account_id_roundtrips(tmp_path) -> None:
    model = make_model(tmp_path)
    assert model.last_selected_account_id == ""

    model.last_selected_account_id = "some-id"
    assert model.last_selected_account_id == "some-id"


def test_display_name_falls_back_to_jid(tmp_path) -> None:
    model = make_model(tmp_path)
    account_id = model.add_account("user@example.com")
    account = model.account_by_id(account_id)
    assert account is not None
    assert account.display_name == "user@example.com"

    model.update_account(account_id, "user@example.com", label="Friendly Name")
    account = model.account_by_id(account_id)
    assert account is not None
    assert account.display_name == "Friendly Name"
