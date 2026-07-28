"""Login window shown before any Module/XmppComm exists -- see specs/plans/gui-login-window.md.

Modeled on pyobs-polaris's LoginWindow.qml: list-left/detail-right, Connect always uses whatever's
currently in the fields (never implicitly saves), saving an account and storing its password are
two separate, explicit actions.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass

from PySide6 import QtCore, QtGui, QtWidgets

from .accounts import SavedAccountsModel

log = logging.getLogger(__name__)

_KEYRING_SERVICE = "pyobs-gui"


@dataclass
class ConnectionRequest:
    """Everything needed to build an XmppComm, built fresh from the visible fields on Connect."""

    jid: str
    password: str
    server: str | None
    use_tls: bool
    insecure_skip_tls: bool


def build_connection_request(
    jid: str,
    password: str,
    override_server: bool,
    host: str,
    port: str,
    use_tls: bool,
    insecure_skip_tls: bool,
) -> ConnectionRequest | None:
    """Builds a ConnectionRequest from raw field values, or None if the required fields (jid,
    password) aren't filled in. Pulled out of LoginWindow as a plain function so it's testable
    without constructing any Qt widgets.

    Args:
        jid: JID field text.
        password: Password field text.
        override_server: Whether the "override server address" checkbox is checked.
        host: Host field text (only used if override_server).
        port: Port field text (only used if override_server and non-empty).
        use_tls: Whether the "Use SSL/TLS" checkbox is checked. Defaults to True in the UI --
            XmppComm itself defaults to False (more appropriate for trusted local networks), but
            a remote/non-technical-facing login window should default to the secure option.
        insecure_skip_tls: Whether the "skip TLS certificate verification" checkbox is checked.
            Only meaningful when use_tls is also True.
    """
    jid = jid.strip()
    if not jid or not password:
        return None

    server = None
    if override_server:
        host = host.strip()
        port = port.strip()
        if host:
            server = f"{host}:{port}" if port else host

    return ConnectionRequest(
        jid=jid, password=password, server=server, use_tls=use_tls, insecure_skip_tls=insecure_skip_tls
    )


class LoginWindow(QtWidgets.QDialog):
    def __init__(self, accounts: SavedAccountsModel | None = None, parent: QtWidgets.QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("pyobs - Sign in")
        self.resize(640, 480)

        self._accounts = accounts if accounts is not None else SavedAccountsModel()
        self._selected_account_id = ""
        self._keychain_notice = ""

        loop = asyncio.get_event_loop()
        self._connect_future: asyncio.Future[ConnectionRequest] = loop.create_future()

        self._build_ui()
        self._reload_account_list()

        last_id = self._accounts.last_selected_account_id
        if last_id and self._accounts.account_by_id(last_id) is not None:
            self._select_account(last_id)
        else:
            self._select_account("")

    async def wait_for_connect(self) -> ConnectionRequest:
        """Waits for the user to click Connect, and returns the resulting request. Cancelled if
        the window is closed first (see closeEvent)."""
        return await self._connect_future

    # ── UI construction ──────────────────────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QtWidgets.QHBoxLayout(self)

        # left: saved accounts list
        left = QtWidgets.QVBoxLayout()
        left_label = QtWidgets.QLabel("Accounts")
        left_label.setStyleSheet("font-weight: bold;")
        left.addWidget(left_label)
        self._account_list = QtWidgets.QListWidget()
        self._account_list.currentItemChanged.connect(self._on_account_list_selection_changed)
        left.addWidget(self._account_list)
        self._new_connection_button = QtWidgets.QPushButton("+ New connection")
        self._new_connection_button.clicked.connect(lambda: self._select_account(""))
        left.addWidget(self._new_connection_button)
        left_widget = QtWidgets.QWidget()
        left_widget.setLayout(left)
        left_widget.setFixedWidth(220)
        layout.addWidget(left_widget)

        # right: detail form
        right = QtWidgets.QVBoxLayout()

        title = QtWidgets.QLabel("pyobs")
        title.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        title.setStyleSheet("font-weight: bold; font-size: 16pt;")
        right.addWidget(title)

        self._status_label = QtWidgets.QLabel("")
        self._status_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignHCenter)
        right.addWidget(self._status_label)

        self._keychain_notice_label = QtWidgets.QLabel("")
        self._keychain_notice_label.setStyleSheet("color: orange;")
        self._keychain_notice_label.setWordWrap(True)
        self._keychain_notice_label.setVisible(False)
        right.addWidget(self._keychain_notice_label)

        self._jid_field = QtWidgets.QLineEdit()
        self._jid_field.setPlaceholderText("JID (e.g. user@example.com)")
        right.addWidget(self._jid_field)

        self._label_field = QtWidgets.QLineEdit()
        self._label_field.setPlaceholderText("Label (optional, shown in the list)")
        right.addWidget(self._label_field)

        self._password_field = QtWidgets.QLineEdit()
        self._password_field.setPlaceholderText("Password")
        self._password_field.setEchoMode(QtWidgets.QLineEdit.EchoMode.Password)
        self._password_field.returnPressed.connect(self._on_connect_clicked)
        right.addWidget(self._password_field)

        self._use_tls_checkbox = QtWidgets.QCheckBox("Use SSL/TLS")
        self._use_tls_checkbox.setChecked(True)
        self._use_tls_checkbox.toggled.connect(self._on_use_tls_toggled)
        right.addWidget(self._use_tls_checkbox)

        self._skip_tls_checkbox = QtWidgets.QCheckBox("Skip TLS certificate verification (insecure, dev only)")
        right.addWidget(self._skip_tls_checkbox)

        self._store_password_checkbox = QtWidgets.QCheckBox("Store password in system keychain")
        right.addWidget(self._store_password_checkbox)

        self._override_server_checkbox = QtWidgets.QCheckBox("Override server address (skip DNS SRV lookup)")
        self._override_server_checkbox.toggled.connect(self._on_override_server_toggled)
        right.addWidget(self._override_server_checkbox)

        server_row = QtWidgets.QHBoxLayout()
        self._host_field = QtWidgets.QLineEdit()
        self._host_field.setPlaceholderText("Host (e.g. example.com)")
        server_row.addWidget(self._host_field)
        self._port_field = QtWidgets.QLineEdit()
        self._port_field.setPlaceholderText("5222")
        self._port_field.setValidator(QtGui.QIntValidator(1, 65535))
        self._port_field.setFixedWidth(80)
        server_row.addWidget(self._port_field)
        self._server_row_widget = QtWidgets.QWidget()
        self._server_row_widget.setLayout(server_row)
        self._server_row_widget.setVisible(False)
        right.addWidget(self._server_row_widget)

        button_row = QtWidgets.QHBoxLayout()
        self._save_button = QtWidgets.QPushButton("Save as new account")
        self._save_button.clicked.connect(self._on_save_clicked)
        button_row.addWidget(self._save_button)
        self._delete_button = QtWidgets.QPushButton("Delete")
        self._delete_button.setVisible(False)
        self._delete_button.clicked.connect(self._on_delete_clicked)
        button_row.addWidget(self._delete_button)
        right.addLayout(button_row)

        right.addStretch()

        self._connect_button = QtWidgets.QPushButton("Connect")
        self._connect_button.clicked.connect(self._on_connect_clicked)
        right.addWidget(self._connect_button)

        layout.addLayout(right)

    # ── account list / selection ─────────────────────────────────────────────

    def _reload_account_list(self) -> None:
        self._account_list.blockSignals(True)
        self._account_list.clear()
        for account in self._accounts.list_accounts():
            item = QtWidgets.QListWidgetItem(account.display_name)
            item.setData(QtCore.Qt.ItemDataRole.UserRole, account.id)
            self._account_list.addItem(item)
        self._account_list.blockSignals(False)

    def _on_account_list_selection_changed(
        self, current: QtWidgets.QListWidgetItem | None, previous: QtWidgets.QListWidgetItem | None
    ) -> None:
        account_id = current.data(QtCore.Qt.ItemDataRole.UserRole) if current is not None else ""
        self._select_account(account_id or "")

    def _select_account(self, account_id: str) -> None:
        self._selected_account_id = account_id
        self._password_field.setText("")

        if not account_id:
            self._jid_field.setText("")
            self._label_field.setText("")
            self._store_password_checkbox.setChecked(False)
            self._override_server_checkbox.setChecked(False)
            self._host_field.setText("")
            self._port_field.setText("")
            self._use_tls_checkbox.setChecked(True)
            self._skip_tls_checkbox.setChecked(False)
            self._delete_button.setVisible(False)
            self._save_button.setText("Save as new account")
            return

        account = self._accounts.account_by_id(account_id)
        if account is None:
            return

        self._jid_field.setText(account.jid)
        self._label_field.setText(account.label)
        self._override_server_checkbox.setChecked(bool(account.host))
        self._host_field.setText(account.host)
        self._port_field.setText(str(account.port) if account.port else "")
        self._use_tls_checkbox.setChecked(account.use_tls)
        self._skip_tls_checkbox.setChecked(account.insecure_skip_tls)
        self._delete_button.setVisible(True)
        self._save_button.setText("Save changes")

        import keyring

        try:
            password = keyring.get_password(_KEYRING_SERVICE, account_id)
        except Exception:
            log.exception("Could not read password from system keychain.")
            password = None
        self._store_password_checkbox.setChecked(password is not None)
        if password is not None:
            self._password_field.setText(password)

    def _on_override_server_toggled(self, checked: bool) -> None:
        self._server_row_widget.setVisible(checked)

    def _on_use_tls_toggled(self, checked: bool) -> None:
        # skipping cert verification is meaningless with TLS off
        self._skip_tls_checkbox.setEnabled(checked)
        if not checked:
            self._skip_tls_checkbox.setChecked(False)

    # ── save / delete ─────────────────────────────────────────────────────────

    def _on_save_clicked(self) -> None:
        jid = self._jid_field.text().strip()
        if not jid:
            return
        label = self._label_field.text().strip()
        host = self._host_field.text().strip() if self._override_server_checkbox.isChecked() else ""
        port_text = self._port_field.text().strip() if self._override_server_checkbox.isChecked() else ""
        port = int(port_text) if port_text else 0
        use_tls = self._use_tls_checkbox.isChecked()
        insecure_skip_tls = self._skip_tls_checkbox.isChecked()

        if self._selected_account_id:
            account_id = self._selected_account_id
            self._accounts.update_account(
                account_id,
                jid,
                label=label,
                host=host,
                port=port,
                use_tls=use_tls,
                insecure_skip_tls=insecure_skip_tls,
            )
        else:
            account_id = self._accounts.add_account(
                jid, label=label, host=host, port=port, use_tls=use_tls, insecure_skip_tls=insecure_skip_tls
            )
            self._selected_account_id = account_id

        self._set_stored_password(account_id, self._store_password_checkbox.isChecked())
        self._reload_account_list()
        self._select_list_item_by_account_id(account_id)

    def _on_delete_clicked(self) -> None:
        if not self._selected_account_id:
            return
        self._set_stored_password(self._selected_account_id, False)
        self._accounts.remove_account(self._selected_account_id)
        self._reload_account_list()
        self._select_account("")

    def _set_stored_password(self, account_id: str, store: bool) -> None:
        import keyring

        self._keychain_notice = ""
        self._keychain_notice_label.setVisible(False)
        try:
            if store and self._password_field.text():
                keyring.set_password(_KEYRING_SERVICE, account_id, self._password_field.text())
            elif not store:
                try:
                    keyring.delete_password(_KEYRING_SERVICE, account_id)
                except keyring.errors.PasswordDeleteError:
                    pass  # nothing stored to delete -- not an error
        except Exception:
            log.exception("Could not update password in system keychain.")
            action = "save" if store else "remove"
            self._keychain_notice = f"Could not {action} the password in the system keychain."
            self._keychain_notice_label.setText(self._keychain_notice)
            self._keychain_notice_label.setVisible(True)

    def _select_list_item_by_account_id(self, account_id: str) -> None:
        for i in range(self._account_list.count()):
            item = self._account_list.item(i)
            if item.data(QtCore.Qt.ItemDataRole.UserRole) == account_id:
                self._account_list.setCurrentItem(item)
                return

    # ── connect ───────────────────────────────────────────────────────────────

    def _on_connect_clicked(self) -> None:
        request = build_connection_request(
            jid=self._jid_field.text(),
            password=self._password_field.text(),
            override_server=self._override_server_checkbox.isChecked(),
            host=self._host_field.text(),
            port=self._port_field.text(),
            use_tls=self._use_tls_checkbox.isChecked(),
            insecure_skip_tls=self._skip_tls_checkbox.isChecked(),
        )
        if request is None:
            return

        if self._selected_account_id:
            self._accounts.last_selected_account_id = self._selected_account_id

        self._status_label.setText("Connecting...")
        self._connect_button.setEnabled(False)
        if not self._connect_future.done():
            self._connect_future.set_result(request)

    def closeEvent(self, event: object) -> None:  # noqa: N802  (Qt override, not our naming convention)
        if not self._connect_future.done():
            self._connect_future.cancel()
        super().closeEvent(event)  # type: ignore[arg-type]


__all__ = ["ConnectionRequest", "LoginWindow", "build_connection_request"]
