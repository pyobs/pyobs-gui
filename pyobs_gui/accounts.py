"""Saved XMPP login accounts, persisted via QSettings -- see specs/plans/gui-login-window.md.

Each account has a stable internal id (a uuid4 hex string, generated in add_account()) distinct
from its jid/label -- both are freely editable via update_account(), and the id (not jid/label) is
what a stored password gets keyed on in the system keychain, so renaming an account never orphans
its password. Mirrors pyobs-polaris's SavedAccountsModel, which follows the same rule for the same
reason.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass

from PySide6 import QtCore

_ORGANIZATION = "pyobs"
_APPLICATION = "pyobs-gui"


@dataclass
class Account:
    id: str
    jid: str
    label: str = ""
    host: str = ""
    port: int = 0
    use_tls: bool = True
    insecure_skip_tls: bool = False

    @property
    def display_name(self) -> str:
        return self.label if self.label else self.jid


class SavedAccountsModel:
    """Saved account list, persisted via QSettings. Password storage is a separate concern --
    see login.py's use of the `keyring` package, keyed by Account.id."""

    def __init__(self, settings: QtCore.QSettings | None = None) -> None:
        self._settings = settings if settings is not None else QtCore.QSettings(_ORGANIZATION, _APPLICATION)

    def list_accounts(self) -> list[Account]:
        accounts = []
        size = self._settings.beginReadArray("accounts")
        try:
            for i in range(size):
                self._settings.setArrayIndex(i)
                accounts.append(
                    Account(
                        id=str(self._settings.value("id", "")),
                        jid=str(self._settings.value("jid", "")),
                        label=str(self._settings.value("label", "")),
                        host=str(self._settings.value("host", "")),
                        port=int(self._settings.value("port", 0, type=int)),  # pyrefly: ignore [bad-argument-type]
                        use_tls=bool(self._settings.value("use_tls", True, type=bool)),
                        insecure_skip_tls=bool(self._settings.value("insecure_skip_tls", False, type=bool)),
                    )
                )
        finally:
            self._settings.endArray()
        return accounts

    def account_by_id(self, account_id: str) -> Account | None:
        for account in self.list_accounts():
            if account.id == account_id:
                return account
        return None

    def add_account(
        self,
        jid: str,
        label: str = "",
        host: str = "",
        port: int = 0,
        use_tls: bool = True,
        insecure_skip_tls: bool = False,
    ) -> str:
        """Adds a new account and returns its newly generated id."""
        account = Account(
            id=uuid.uuid4().hex,
            jid=jid,
            label=label,
            host=host,
            port=port,
            use_tls=use_tls,
            insecure_skip_tls=insecure_skip_tls,
        )
        accounts = self.list_accounts()
        accounts.append(account)
        self._write_all(accounts)
        return account.id

    def update_account(
        self,
        account_id: str,
        jid: str,
        label: str = "",
        host: str = "",
        port: int = 0,
        use_tls: bool = True,
        insecure_skip_tls: bool = False,
    ) -> None:
        """Updates an existing account's fields in place -- the id itself never changes."""
        accounts = self.list_accounts()
        for i, account in enumerate(accounts):
            if account.id == account_id:
                accounts[i] = Account(
                    id=account_id,
                    jid=jid,
                    label=label,
                    host=host,
                    port=port,
                    use_tls=use_tls,
                    insecure_skip_tls=insecure_skip_tls,
                )
                break
        self._write_all(accounts)

    def remove_account(self, account_id: str) -> None:
        accounts = [a for a in self.list_accounts() if a.id != account_id]
        self._write_all(accounts)

    def _write_all(self, accounts: list[Account]) -> None:
        self._settings.beginWriteArray("accounts")
        try:
            for i, account in enumerate(accounts):
                self._settings.setArrayIndex(i)
                self._settings.setValue("id", account.id)
                self._settings.setValue("jid", account.jid)
                self._settings.setValue("label", account.label)
                self._settings.setValue("host", account.host)
                self._settings.setValue("port", account.port)
                self._settings.setValue("use_tls", account.use_tls)
                self._settings.setValue("insecure_skip_tls", account.insecure_skip_tls)
        finally:
            self._settings.endArray()

    @property
    def last_selected_account_id(self) -> str:
        """Only remembers which account was last used (to preselect it next launch) -- never
        implies anything was saved/connected automatically."""
        return str(self._settings.value("last_selected_account_id", ""))

    @last_selected_account_id.setter
    def last_selected_account_id(self, value: str) -> None:
        self._settings.setValue("last_selected_account_id", value)


__all__ = ["Account", "SavedAccountsModel"]
