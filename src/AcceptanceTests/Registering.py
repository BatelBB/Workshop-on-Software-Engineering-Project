from Service.bridge.proxy import Proxy
import unittest


class Registering(unittest.TestCase):
    app: Proxy
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Proxy()
        cls.happy_user1 = ("usr1", "password")
        cls.happy_user2 = ("usr2", "password")
        cls.empty_password = ("user3", "")
        cls.taken_username = ("usr1", "45sdfcgs#$%1")
        cls.admin_username = ("Kfir", "45sdfgs#$%1")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_registering_happy(self):
        r = self.app.register(*self.happy_user1)
        self.assertTrue(r.success and r.result, "error: registering failed")
        r = self.app.register(*self.happy_user2)
        self.assertTrue(r.success and r.result, "error: registering failed")

    def test_empty_password(self):
        r = self.app.register(*self.empty_password)
        self.assertFalse(r.success, "error: registering with an empty password succeeded")

    def test_taken_username(self):
        r = self.app.register(*self.happy_user1)
        self.assertTrue(r.success and r.result, "error: registering failed")
        r = self.app.register(*self.taken_username)
        self.assertFalse(r.success, "error: registering with a taken username succeeded")

    def test_registering_with_admin_username(self):
        r = self.app.register(*self.admin_username)
        self.assertFalse(r.success, "error: registering with the admin username succeeded")

