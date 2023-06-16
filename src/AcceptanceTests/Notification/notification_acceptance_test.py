from typing import Optional, Tuple, Dict

from Service.bridge.proxy import Proxy
import unittest

from domain.main.Market.Permissions import Permission
from domain.main.Notifications.notification import Notification


def _count_optional(li: Optional[list]):
    return 0 if li is None else len(li)


class _UserNotificationTestHelper:
    def __init__(self, username: str, password: str, app: Proxy):
        self.username = username
        self.password = password
        self.app = app
        self.last_inbox: Optional[list[Notification]] = None
        self.current_inbox: Optional[list[Notification]] = None

    def login(self):
        return self.app.login(self.username, self.password)

    def logout(self):
        return self.app.logout()

    def update_inbox(self):
        self.last_inbox = self.current_inbox
        self.current_inbox = self.app.get_inbox().result

    @property
    def count_inbox_new(self):
        return _count_optional(self.current_inbox) - _count_optional(self.last_inbox)


class _NotificationAcceptanceTestsHelper:
    def __init__(self, app: Proxy, *args: Tuple[str, str]):
        self._app = app
        self._users: Dict[str, _UserNotificationTestHelper] = {
            username: _UserNotificationTestHelper(username, password, app)
            for (username, password) in args
        }
        self._current_user: Optional[_UserNotificationTestHelper] = None

    def register_everyone(self, with_initial_login: bool = True):
        for u in self._users.values():
            self._app.register(u.username, u.password)
            if with_initial_login:
                self.switch_user(u.username)
                self.update_inbox()
                self.logout()

    def login(self, username: str):
        if self._current_user is not None:
            raise Exception("should be logged out")
        user = self._users[username]
        user.login()
        self._current_user = user

    def logout(self):
        if self._current_user is None:
            raise Exception("should be logged in")
        self._current_user.logout()
        self._current_user = None

    def switch_user(self, username: str):
        if self._current_user is not None and self._current_user.username == username:
            return
        if self._current_user is not None:
            self.logout()
        self.login(username)

    def update_inbox(self):
        self._current_user.update_inbox()

    @property
    def count_inbox_new(self):
        return self._current_user.count_inbox_new


class NotificationAcceptanceTests(unittest.TestCase):
    app: Proxy
    admin: Tuple[str, str]
    helper: _NotificationAcceptanceTestsHelper

    @classmethod
    def setUpClass(cls) -> None:
        cls.admin = 'Kfir', 'Kfir'

    def setUp(self) -> None:
        self.app = Proxy()
        self.app.enter_market()
        self.helper = _NotificationAcceptanceTestsHelper(
            self.app,
            ('yuval', '123456'),
            ('batel', '123456'),
            ('hagai', '123456'),
            ('mendi', '123456')
        )
        self.helper.register_everyone(with_initial_login=True)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()
        self.app.enter_market()
        self.app.login(*NotificationAcceptanceTests.admin)
        self.app.shutdown()

    def test_appointment(self):
        self.helper.switch_user('yuval')
        self.app.open_store('snacks')
        self.app.add_permission('snacks', 'batel', Permission.InteractWithCustomer)
        self.helper.switch_user('batel')
        self.helper.update_inbox()
        self.assert_new_messages()

    def assert_new_messages(self, msg: str = None):
        self.assertGreater(self.helper.count_inbox_new, 0,
                           msg or f"user {self.helper._current_user.username} should have had new messages")
