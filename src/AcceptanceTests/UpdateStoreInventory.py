from Service.bridge.proxy import Proxy
import unittest


class UpdateStoreInventory(unittest.TestCase):
    app: Proxy
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Proxy()
        cls.store_owner1 = ("usr1", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_owner1)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    # def test_owner_change_product_name_and_cart_using_old_name_can_purchase(self):

    def test_owner_add_products_to_store_happy(self):
        self.app.login(*self.store_owner1)
        self.app.open_store("bakery")
        r = self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.assertTrue(r.success, "error: add product action failed")
        r = self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.assertTrue(r.success, "error: add product action failed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        products = self.app.get_products_by_name("pita").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        self.app.logout()

    def test_owner_add_products_that_already_existed(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.add_product("bakery", "bread", "5", 8, 2, ["yy", "zz"])
        self.assertFalse(r.success, "error: add product action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        bakery = products[0]
        self.assertIn("bread", bakery, "error: bread not found")
        self.assertEqual("bread", bakery["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, bakery["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", bakery["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(None, bakery["bread"]["Rate"], "error: bread rate incorrect")
        self.app.logout()

    def test_owner_add_product_with_non_positive_price(self):
        self.app.login(*self.store_owner1)
        self.app.open_store("bakery")
        r = self.app.add_product("bakery", "bread", "1", -5, 2, ["yy", "zz"])
        self.assertFalse(r.success, "error: add product action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: product with negative price added")

        r = self.app.add_product("bakery", "bread", "1", 0, 2, ["yy", "zz"])
        self.assertFalse(r.success, "error: add product action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: product with zero price added")
        self.app.logout()

    def test_owner_add_product_with_negative_quantity(self):
        self.app.login(*self.store_owner1)
        self.app.open_store("bakery")
        r = self.app.add_product("bakery", "bread", "1", 5, -8, ["yy", "zz"])
        self.assertFalse(r.success, "error: add product action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: product with negative quantity added")
        self.app.logout()

    def test_owner_remove_product(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.remove_product("bakery", "bread")
        self.assertTrue(r.success, "error: remove product action failed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: product found after removed from store")
        self.app.logout()

    def test_owner_remove_product_not_existed(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.remove_product("bakery", "xxx")
        self.assertFalse(r.success, "error: remove product action succeeded")
        self.app.logout()

    def test_owner_update_product_quantity_happy(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.update_product_quantity("bakery", "bread", 100)
        self.assertTrue(r.success, "error: update product quantity action failed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        bakery = products[0]
        self.assertIn("bread", bakery, "error: bread not found")
        self.assertEqual("bread", bakery["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, bakery["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", bakery["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(None, bakery["bread"]["Rate"], "error: bread rate incorrect")
        # todo add quantity check
        self.app.logout()

    def test_owner_update_product_quantity_illegal_quantity(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.update_product_quantity("bakery", "bread", -5)
        self.assertFalse(r.success, "error: update product quantity action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        bakery = products[0]
        self.assertIn("bread", bakery, "error: bread not found")
        self.assertEqual("bread", bakery["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, bakery["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", bakery["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(None, bakery["bread"]["Rate"], "error: bread rate incorrect")
        # todo add quantity check
        self.app.logout()

    def test_owner_change_product_name(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.change_product_name("bakery", "bread", "new_bread")
        self.assertTrue(r.success, "error: change product name action failed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: got a store that has the products with the old name "
                                           "after its name changed")
        products = self.app.get_products_by_name("new_bread").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        bakery = products[0]
        self.assertIn("new_bread", bakery, "error: new_bread not found")
        self.assertEqual("new_bread", bakery["new_bread"]["Name"], "error: new_bread name incorrect")
        self.assertEqual(10, bakery["new_bread"]["Price"], "error: new_bread price incorrect")
        self.assertEqual("1", bakery["new_bread"]["Category"], "error: new_bread category incorrect")
        self.app.logout()

    def test_owner_change_product_price(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.change_product_price("bakery", 10, 20)
        self.assertTrue(r.success, "error: change product price action failed")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        bakery = products[0]
        self.assertIn("bread", bakery, "error: bread not found")
        self.assertEqual("bread", bakery["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(20, bakery["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", bakery["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(None, bakery["bread"]["Rate"], "error: bread rate incorrect")
        self.app.logout()

    def test_owner_change_product_price_to_non_positive_price(self):
        self.set_stores()
        self.app.login(*self.store_owner1)
        r = self.app.change_product_price("bakery", 10, -5)
        self.assertFalse(r.success, "error: change product price action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        bakery = products[0]
        self.assertIn("bread", bakery, "error: bread not found")
        self.assertEqual("bread", bakery["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, bakery["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", bakery["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(None, bakery["bread"]["Rate"], "error: bread rate incorrect")
        self.app.logout()

    def set_stores(self):
        self.app.login(*self.store_owner1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()