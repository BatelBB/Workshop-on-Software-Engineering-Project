from Service.bridge.proxy import Proxy
import unittest


class Login(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.happy_user1 = ("usr1", "password")
        cls.happy_user2 = ("usr22", "password")
        cls.happy_user3 = ("usr3", "45sdfgs#$%1")
        cls.not_registered_user = ("usr4", "45sdfgs#$%1")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.happy_user1)
        self.app.register(*self.happy_user2)
        self.app.register(*self.happy_user3)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_login_happy(self):
        r = self.app.login(*self.happy_user1)
        self.assertTrue(r.success and r.result, "error: login failed")
        self.app.logout()
        r = self.app.login(*self.happy_user2)
        self.assertTrue(r.success and r.result, "error: login failed")
        self.app.logout()

    def test_login_without_registering(self):
        r = self.app.login(*self.not_registered_user)
        self.assertFalse(r.success, "error: successfully login with unregistered username")

    def test_2_logins_without_logout(self):
        r = self.app.login(*self.happy_user1)
        self.assertTrue(r.success and r.result, "error: login failed")
        r = self.app.login(*self.happy_user2)
        self.assertTrue(r.success and r.result, "error: login failed "
                                                "while another user is logged in in the same session")
        self.app.logout()

    def test_wrong_password(self):
        r = self.app.login(self.happy_user1[0], "wrongPass")
        self.assertFalse(r.success, "error: successfully login with wrong password")
