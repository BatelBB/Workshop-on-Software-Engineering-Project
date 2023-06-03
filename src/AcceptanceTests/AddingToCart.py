from Service.bridge.proxy import Proxy
import unittest


class AddingToCart(unittest.TestCase):
    app: Proxy
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Proxy()
        cls.store_owner1 = ("usr11", "password")
        cls.store_owner2 = ("usr5", "password")
        cls.registered_buyer1 = ("usr2", "password")
        cls.registered_buyer2 = ("usr3", "45sdfgs#$%1")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.registered_buyer1)
        self.app.register(*self.registered_buyer2)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_member_adding_to_cart(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        r = self.app.add_to_cart("bakery", "bread", 5)
        self.assertTrue(r.success and r.result, "error: add to cart failed")
        r = self.app.add_to_cart("bakery", "pita", 10)
        self.assertTrue(r.success and r.result, "error: add to cart failed")
        r = self.app.add_to_cart("market", "pita", 10)
        self.assertTrue(r.success and r.result, "error: add to cart failed")
        r = self.app.add_to_cart("market", "tuna", 20)
        self.assertTrue(r.success and r.result, "error: add to cart failed")
        cart = self.app.show_cart().result
        self.assertIn("bread", cart["bakery"], "error: bread not in cart")
        self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
        self.assertIn("pita", cart["bakery"], "error: pita not in cart")
        self.assertEqual(10, cart["bakery"]["pita"]["Quantity"], "error: pita quantity doesn't match")
        self.assertIn("pita", cart["market"], "error: pita not in cart")
        self.assertEqual(10, cart["market"]["pita"]["Quantity"], "error: pita quantity doesn't match")
        self.assertIn("tuna", cart["market"], "error: pita not in cart")
        self.assertEqual(20, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
        self.app.logout()

    def test_guest_adding_to_cart(self):
        self.set_stores()
        r = self.app.add_to_cart("bakery", "bread", 5)
        self.assertTrue(r.success and r.result, "error: add to cart failed")
        r = self.app.add_to_cart("market", "tuna", 10)
        self.assertTrue(r.success and r.result, "error: add to cart failed")
        cart = self.app.show_cart().result
        self.assertIn("bread", cart["bakery"], "error: bread not in cart")
        self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
        self.assertIn("tuna", cart["market"], "error: tuna not in cart")
        self.assertEqual(10, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")

    def test_removing_from_cart(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("market", "pita", 10)
        r = self.app.remove_from_cart("bakery", "bread")
        self.assertTrue(r.success and r.result, "error: remove product from cart action failed!")
        cart = self.app.show_cart().result
        self.assertNotIn("bread", cart["bakery"], "error: bread in cart after removed")
        self.assertIn("pita", cart["market"], "error: pita not in cart after another product removed")
        self.app.logout()

    def test_update_product_quantity_in_cart(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("market", "pita", 10)
        r = self.app.update_cart_product_quantity("bakery", "bread", 10)
        self.assertTrue(r.success and r.result, "error: update product quantity action failed!")
        cart = self.app.show_cart().result
        self.assertIn("bread", cart["bakery"], "error: bread not in cart")
        self.assertEqual(10, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match after updated")
        self.assertIn("pita", cart["market"], "error: tuna not in cart")
        self.assertEqual(10, cart["market"]["pita"]["Quantity"], "error: pita quantity doesn't match")
        self.app.logout()

    def test_adding_exceeding_product_quantity(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("bakery", "pita", 10)
        r = self.app.add_to_cart("bakery", "bread", 100)
        self.assertFalse(r.success, "error: update product quantity action not failed!")
        cart = self.app.show_cart().result
        self.assertNotIn("bread", cart["bakery"], "error: bread in cart after add to cart action with exceeding amount")
        self.assertIn("pita", cart["bakery"], "error: pita not in cart")
        self.assertEqual(10, cart["bakery"]["pita"]["Quantity"], "error: pita quantity doesn't match")
        self.app.logout()

    def test_update_product_quantity_with_exceeding_quantity(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("market", "pita", 10)
        r = self.app.update_cart_product_quantity("bakery", "bread", 100)
        self.assertFalse(r.success, "error: update product quantity action not failed!")
        cart = self.app.show_cart().result
        self.assertIn("bread", cart["bakery"], "error: bread not in cart")
        self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match after updated")
        self.assertIn("tuna", cart["market"], "error: tuna not in cart")
        self.assertEqual(10, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
        self.app.logout()

    def test_adding_to_cart_with_non_positive_quantity(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        r = self.app.add_to_cart("market", "tuna", 0)
        self.assertFalse(r.success, "error: add to cart action not failed!")
        r = self.app.add_to_cart("bakery", "bread", -5)
        self.assertFalse(r.success, "error: add to cart action not failed!")
        cart = self.app.show_cart().result
        print(cart)
        self.assertNotIn("market", cart, "error: bread in cart after add to cart action with 0 amount")
        self.assertNotIn("bakery", cart, "error: tuna in cart after add to cart action with negative amount")
        self.app.logout()

    def test_adding_invalid_product(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("market", "tuna", 10)
        self.app.add_to_cart("market", "xxx", 100)
        cart = self.app.show_cart().result
        self.assertNotIn("xxx", cart["market"], "error: xxx in cart and it's not a product in the bakery store")
        self.assertIn("tuna", cart["market"], "error: tuna not in cart")
        self.assertEqual(10, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
        self.app.logout()

    def test_adding_invalid_with_invalid_store(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("market", "tuna", 10)
        self.app.add_to_cart("xxx", "bread", 100)
        cart = self.app.show_cart().result
        self.assertNotIn("xxx", cart, "error: store 'xxx' in cart after add to cart action with invalid store")
        self.assertIn("tuna", cart["market"], "error: tuna not in cart")
        self.assertEqual(10, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
        self.app.logout()

    def test_removing_invalid_product(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("market", "tuna", 10)
        r = self.app.remove_from_cart("bakery", "xxx")
        self.assertFalse(r.success, "error: remove product from cart action not failed!")
        cart = self.app.show_cart().result
        self.assertIn("bread", cart["bakery"], "error: bread not in cart")
        self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
        self.assertIn("tuna", cart["market"], "error: tuna not in cart")
        self.assertEqual(10, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
        self.app.logout()

    def test_removing_invalid_store(self):
        self.set_stores()
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("market", "tuna", 10)
        r = self.app.remove_from_cart("xxx", "bread")
        self.assertFalse(r.success, "error: remove product from cart action not failed!")
        cart = self.app.show_cart().result
        self.assertIn("bread", cart["bakery"], "error: bread not in cart")
        self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
        self.assertIn("tuna", cart["market"], "error: tuna not in cart")
        self.assertEqual(10, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
        self.app.logout()

    def set_stores(self):
        self.app.login(*self.store_owner1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        self.app.login(*self.store_owner2)
        self.app.open_store("market")
        self.app.add_product("market", "tuna", "1", 20, 40, ["basic", "z"])
        self.app.add_product("market", "pita", "1", 10, 20, ["basic", "y"])
        self.app.logout()
