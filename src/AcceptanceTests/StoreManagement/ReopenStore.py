from Service.bridge.proxy import Proxy
import unittest


class ReopenStore(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_owner1 = ("usr1", "password")
        cls.store_owner2 = ("usr2", "password")
        cls.registered_user = ("user33", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.registered_user)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_reopen_store_happy(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.reopen_store("bakery")
        self.assertTrue(r.success, "error: reopen store action failed")
        r = self.app.add_to_cart("bakery", "bread", 10)
        self.assertTrue(r.success, "error: add to cart action failed")
        cart = self.app.show_cart().result
        self.assertIn("bread", cart["bakery"], "error: bread not in cart after store reopened")
        self.assertEqual(10, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match after store "
                                                                  "reopened")
        self.app.logout()

    def test_reopened_store_products_found_in_search(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.reopen_store("bakery")
        self.assertTrue(r.success, "error: reopen store action failed")
        self.app.logout()
        self.app.login(*self.store_owner2)
        r = self.app.reopen_store("market")
        self.assertTrue(r.success, "error: reopen store action failed")
        self.app.logout()
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: bakery product not found after the store reopened")
        products = self.app.get_products_by_name("pita").result
        self.assertEqual(2, len(products), "error: bakery and market products not found after the stores reopened")
        products = self.app.get_products_by_name("tuna").result
        self.assertEqual(1, len(products), "error: market product not found after the store reopened")
        self.app.logout()

    def test_reopen_store_already_open(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.reopen_store("bakery")
        self.assertTrue(r.success, "error: reopen store action failed")
        r = self.app.reopen_store("bakery")
        self.assertFalse(r.success, "error: close reopened action succeeded after store already opened")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: bakery product not found after the store reopened twice")
        self.app.logout()

    def test_reopen_store_no_permission_member(self):
        self.set_stores()
        self.app.login(*self.registered_user)
        r = self.app.reopen_store("bakery")
        self.assertFalse(r.success, "error: reopen store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery products found after the store opened by a member "
                                           "without permissions")
        self.app.logout()

    def test_reopen_store_by_another_owner(self):
        self.set_stores()
        self.app.login(*self.store_owner2)
        r = self.app.reopen_store("bakery")
        self.assertFalse(r.success, "error: reopen store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery products found after the store reopened by another owner")
        self.app.logout()

    def test_reopen_store_no_permission_guest(self):
        self.set_stores()
        r = self.app.reopen_store("bakery")
        self.assertFalse(r.success, "error: reopened store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery products found after the store reopened by a guest")

    def set_stores(self):
        self.app.login(*self.store_owner1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.close_store("bakery")
        self.app.logout()
        self.app.login(*self.store_owner2)
        self.app.open_store("market")
        self.app.add_product("market", "tuna", "2", 20, 40, ["fish", "z"])
        self.app.add_product("market", "pita", "1", 8, 20, ["basic", "y"])
        self.app.close_store("market")
        self.app.logout()
