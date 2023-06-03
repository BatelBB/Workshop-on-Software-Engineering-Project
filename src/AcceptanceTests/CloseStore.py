from Service.bridge.proxy import Proxy
import unittest


class CloseStore(unittest.TestCase):
    app: Proxy
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Proxy()
        cls.store_owner1 = ("usr1", "password")
        cls.store_owner2 = ("usr2", "password")
        cls.registered_user = ("user3", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.registered_user)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_close_store_happy(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.close_store("bakery")
        self.assertTrue(r.success, "error: close store action failed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery product found after the store closed")
        self.app.logout()

    def test_close_store_products_not_found_in_search(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.close_store("bakery")
        self.assertTrue(r.success, "error: close store action failed")
        self.app.logout()
        self.app.login(*self.store_owner2)
        r = self.app.close_store("market")
        self.assertTrue(r.success, "error: close store action failed")
        self.app.logout()
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery product found after the store closed")
        products = self.app.get_products_by_name("pita").result
        self.assertEqual(0, len(products), "error: bakery and market products found after the stores closed")
        products = self.app.get_products_by_name("tuna").result
        self.assertEqual(0, len(products), "error: market product found after the store closed")
        self.app.logout()

    def test_close_store_already_closed(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.close_store("bakery")
        self.assertTrue(r.success, "error: close store action failed")
        r = self.app.close_store("bakery")
        self.assertFalse(r.success, "error: close store action succeeded after store already closed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: bakery product found after the store closed twice")
        self.app.logout()

    def test_close_store_no_permission_member(self):
        self.set_stores()
        self.app.login(*self.registered_user)
        r = self.app.close_store("bakery")
        self.assertFalse(r.success, "error: closed store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: bakery products not found after the store closed by a member "
                                           "without permissions")
        self.app.logout()

    def test_close_store_by_another_owner(self):
        self.set_stores()
        self.app.login(*self.store_owner2)
        r = self.app.close_store("bakery")
        self.assertFalse(r.success, "error: closed store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: bakery products not found after the store closed by another owner")
        self.app.logout()

    def test_close_store_no_permission_guest(self):
        self.set_stores()
        r = self.app.close_store("bakery")
        self.assertFalse(r.success, "error: closed store action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: bakery products not found after the store closed by a guest")

    def set_stores(self):
        self.app.login(*self.store_owner1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        self.app.login(*self.store_owner2)
        self.app.open_store("market")
        self.app.add_product("market", "tuna", "2", 20, 40, ["fish", "z"])
        self.app.add_product("market", "pita", "1", 8, 20, ["basic", "y"])
        self.app.logout()
