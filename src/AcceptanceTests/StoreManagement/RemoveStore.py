from Service.bridge.proxy import Proxy
import unittest


class RemoveStore(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.store_founder2 = ("usr2", "password")
        cls.registered_user = ("user33", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_founder2)
        self.app.register(*self.registered_user)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_remove_store_happy(self):
        self.set_stores()
        self.app.login(*self.store_founder1)
        r = self.app.remove_store("bakery")
        self.assertTrue(r.success, "error: remove store action failed")
        r = self.app.add_to_cart("bakery", "bread", 10)
        self.assertFalse(r.success, "error: add to cart action succeeded")
        cart = self.app.show_cart().result
        self.assertDictEqual({}, cart, "error: product of removed store added to cart!")
        self.app.logout()

    def test_remove_store_products_not_found_in_search(self):
        self.set_stores()
        self.app.login(*self.store_founder1)
        r = self.app.remove_store("bakery")
        self.assertTrue(r.success, "error: remove store action failed")
        self.app.logout()
        self.app.login(*self.store_founder2)
        r = self.app.reopen_store("market")
        self.assertTrue(r.success, "error: remove store action failed")
        self.app.logout()
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery product found after the store removed")
        products = self.app.get_products_by_name("pita").result
        self.assertEqual(0, len(products), "error: bakery and market products found after the stores removed")
        products = self.app.get_products_by_name("tuna").result
        self.assertEqual(0, len(products), "error: market product found after the store removed")
        self.app.logout()

    def test_remove_store_already_removed(self):
        self.set_stores()
        self.app.login(*self.store_founder1)
        r = self.app.remove_store("bakery")
        self.assertTrue(r.success, "error: remove store action failed")
        r = self.app.remove_store("bakery")
        self.assertFalse(r.success, "error: remove store action succeeded after store already removed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery product found after the store removed twice")
        self.app.logout()

    def test_remove_store_closed_store(self):
        self.set_stores()
        self.app.login(*self.store_founder1)
        self.app.close_store("bakery")
        r = self.app.remove_store("bakery")
        self.assertTrue(r.success, "error: remove store action failed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery product found after the store closed and removed")
        self.app.logout()

    def test_remove_store_no_permission_member(self):
        self.set_stores()
        self.app.login(*self.registered_user)
        r = self.app.remove_store("bakery")
        self.assertFalse(r.success, "error: remove store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: bakery products not found after the store removed by a member "
                                           "without permissions")
        self.app.logout()

    def test_remove_store_by_another_owner(self):
        self.set_stores()
        self.app.login(*self.store_founder2)
        r = self.app.remove_store("bakery")
        self.assertFalse(r.success, "error: remove store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: bakery products not found after the store removed by another owner")
        self.app.logout()

    def test_remove_store_no_permission_guest(self):
        self.set_stores()
        r = self.app.remove_store("bakery")
        self.assertFalse(r.success, "error: remove store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: bakery products not found after the store removed by a guest")

    def set_stores(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        self.app.login(*self.store_founder2)
        self.app.open_store("market")
        self.app.add_product("market", "tuna", "2", 20, 40, ["fish", "z"])
        self.app.add_product("market", "pita", "1", 8, 20, ["basic", "y"])
        self.app.logout()
