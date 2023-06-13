from Service.bridge.proxy import Proxy
import unittest


class Logout(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.registered_user1 = ("usr1", "password")
        cls.registered_user2 = ("usr222", "password")
        cls.not_registered_user = ("usr3", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.registered_user1)
        self.app.register(*self.registered_user2)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_member_logout(self):
        self.app.login(*self.registered_user1)
        r = self.app.logout()
        self.assertTrue(r.success and r.result, "error: failed to logout")
        self.app.login(*self.registered_user2)
        r = self.app.logout()
        self.assertTrue(r.success and r.result, "error: failed to logout")

    def test_guest_logout(self):
        r = self.app.logout()
        self.assertFalse(r.success, "error: a guest succeeded to logout")

    def test_Logout_with_empty_cart(self):
        self.app.login(*self.registered_user1)
        cart_before = self.app.show_cart().result
        self.app.logout()
        self.app.exit_market()
        self.app.enter_market()
        self.app.login(*self.registered_user1)
        cart_after = self.app.show_cart().result
        self.assertDictEqual(cart_before, cart_after)

    def test_logout_without_empty_cart(self):
        self.set_a_store()
        self.app.login(*self.registered_user1)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("bakery", "pita", 10)
        cart_before = self.app.show_cart().result
        self.app.logout()
        self.app.exit_market()
        self.app.enter_market()
        self.app.login(*self.registered_user1)
        cart_after = self.app.show_cart().result
        self.assertDictEqual(cart_before, cart_after)

    def set_a_store(self):
        self.app.login(*self.registered_user2)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
