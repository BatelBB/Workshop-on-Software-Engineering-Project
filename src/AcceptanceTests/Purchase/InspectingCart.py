from Service.bridge.proxy import Proxy
import unittest


class InspectingCart(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_owner1 = ("usr1", "password")
        cls.store_owner2 = ("usr444", "password")
        cls.registered_buyer = ("usr2", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.registered_buyer)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_member_inspecting_empty_cart(self):
        self.set_stores()
        self.app.login(*self.registered_buyer)
        cart = self.app.show_cart().result
        self.assertDictEqual({}, cart, "error: cart not empty")
        self.app.logout()

    def test_member_inspecting_not_empty_cart_for(self):
        self.set_stores()
        self.app.login(*self.registered_buyer)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("market", "pita", 10)
        cart = self.app.show_cart().result
        self.assertIn("bakery", cart, "error: bakery store not in cart")
        self.assertIn("bread", cart["bakery"], "error: bread not in cart")
        self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
        self.assertEqual(10, cart["bakery"]["bread"]["Price"], "error: bread price doesn't match")
        self.assertIn("market", cart, "error: market store not in cart")
        self.assertIn("pita", cart["market"], "error: pita not in cart")
        self.assertEqual(10, cart["market"]["pita"]["Quantity"], "error: pita quantity doesn't match")
        self.assertEqual(8, cart["market"]["pita"]["Price"], "error: bread price doesn't match")
        self.app.logout()

    def test_guest_inspecting_empty_cart(self):
        self.set_stores()
        cart = self.app.show_cart().result
        self.assertDictEqual({}, cart, "error: cart not empty")

    def test_guest_inspecting_not_empty_cart_for(self):
        self.set_stores()
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("market", "pita", 10)
        cart = self.app.show_cart().result
        self.assertIn("bakery", cart, "error: bakery store not in cart")
        self.assertIn("bread", cart["bakery"], "error: bread not in cart")
        self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
        self.assertEqual(10, cart["bakery"]["bread"]["Price"], "error: bread price doesn't match")
        self.assertIn("market", cart, "error: market store not in cart")
        self.assertIn("pita", cart["market"], "error: pita not in cart")
        self.assertEqual(10, cart["market"]["pita"]["Quantity"], "error: pita quantity doesn't match")
        self.assertEqual(8, cart["market"]["pita"]["Price"], "error: bread price doesn't match")

    def test_guest_losing_cart_after_leaving(self):
        self.set_stores()
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("market", "pita", 10)
        self.app.exit_market()
        self.app.enter_market()
        cart = self.app.show_cart().result
        self.assertNotIn("bakery", cart, "error: bakery store in cart after the guest left and reentered")
        self.assertNotIn("market", cart, "error: market store in cart after the guest left and reentered")

    def test_inspecting_cart_after_product_name_changed(self):

    def test_inspecting_cart_after_product_price_changed(self):


    def set_stores(self):
        self.app.login(*self.store_owner1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        self.app.login(*self.store_owner2)
        self.app.open_store("market")
        self.app.add_product("market", "tuna", "1", 20, 40, ["basic", "z"])
        self.app.add_product("market", "pita", "1", 8, 20, ["basic", "y"])
        self.app.logout()
