from Service.bridge.proxy import Proxy
import unittest


class SearchingProducts(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_owner1 = ("usr1", "password")
        cls.store_owner2 = ("usr2", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_get_store_products_happy(self):
        self.set_stores()
        r = self.app.get_store("bakery")
        self.assertTrue(r.success, "error: get store product failed")
        products = r.result
        self.assertIn("pita", products, "error: pita not found")
        self.assertEqual(5, products["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", products["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, products["pita"]["Rate"], "error: pita rate incorrect")
        self.assertIn("bread", products, "error: bread not found")
        self.assertEqual(10, products["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", products["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, products["bread"]["Rate"], "error: bread rate incorrect")

    def test_get_store_products_invalid_store(self):
        self.set_stores()
        r = self.app.get_store("xxx")
        self.assertFalse(r.success, "error: get store product succeeded")

    def test_get_products_by_name_unique_name(self):
        self.set_stores()
        r = self.app.get_products_by_name("tuna")
        self.assertTrue(r.success, "error: get product by name failed")
        products = r.result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        product = products[0]
        self.assertIn("tuna", product, "error: tuna not found")
        self.assertEqual("tuna", product["tuna"]["Name"], "error: tuna name incorrect")
        self.assertEqual(20, product["tuna"]["Price"], "error: tuna price incorrect")
        self.assertEqual("2", product["tuna"]["Category"], "error: tuna category incorrect")
        self.assertEqual(5, product["tuna"]["Rate"], "error: tuna rate incorrect")

    def test_get_products_by_name_common_name(self):
        self.set_stores()
        r = self.app.get_products_by_name("pita")
        self.assertTrue(r.success, "error: get product by name failed")
        products = r.result
        self.assertEqual(2, len(products), "error: didn't get 2 stores that has the products while the market has 2")
        bakery = products[0]
        market = products[1]
        self.assertIn("pita", bakery, "error: pita not found")
        self.assertEqual("pita", bakery["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(5, bakery["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", bakery["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, bakery["pita"]["Rate"], "error: pita rate incorrect")
        self.assertIn("pita", market, "error: pita not found")
        self.assertEqual("pita", market["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(8, market["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", market["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, market["pita"]["Rate"], "error: pita rate incorrect")

    def test_get_products_by_name_no_match(self):
        self.set_stores()
        r = self.app.get_products_by_name("xxx")
        self.assertTrue(r.success, "error: get product by name failed")
        self.assertEqual(0, len(r.result), "error: found product xxx")

    def test_get_products_by_category_unique_category(self):
        self.set_stores()
        r = self.app.get_products_by_category("2")
        self.assertTrue(r.success, "error: get product by category failed")
        products = r.result
        self.assertEqual(1, len(products), "error: didn't get 1 store that has the products while the market has 1")
        product = products[0]
        self.assertIn("tuna", product, "error: tuna not found")
        self.assertEqual("tuna", product["tuna"]["Name"], "error: tuna name incorrect")
        self.assertEqual(20, product["tuna"]["Price"], "error: tuna price incorrect")
        self.assertEqual("2", product["tuna"]["Category"], "error: tuna category incorrect")
        self.assertEqual(5, product["tuna"]["Rate"], "error: tuna rate incorrect")

    def test_get_products_by_name_common_category(self):
        self.set_stores()
        r = self.app.get_products_by_category("1")
        self.assertTrue(r.success, "error: get product by category failed")
        products = r.result
        self.assertEqual(2, len(products), "error: didn't get 2 stores that has the products while the market has 2")
        bakery = products[0]
        market = products[1]
        self.assertIn("pita", bakery, "error: pita not found")
        self.assertEqual("pita", bakery["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(5, bakery["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", bakery["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, bakery["pita"]["Rate"], "error: pita rate incorrect")
        self.assertIn("bread", bakery, "error: bread not found")
        self.assertEqual("bread", bakery["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, bakery["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", bakery["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, bakery["bread"]["Rate"], "error: bread rate incorrect")
        self.assertIn("pita", market, "error: pita not found")
        self.assertEqual("pita", market["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(8, market["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", market["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, market["pita"]["Rate"], "error: pita rate incorrect")

    def test_get_products_by_category_no_match(self):
        self.set_stores()
        r = self.app.get_products_by_category("xxx")
        self.assertTrue(r.success, "error: get product by category failed")
        self.assertEqual(0, len(r.result), "error: found category xxx")

    def test_get_products_by_keywords_unique_keyword(self):
        self.set_stores()
        r = self.app.get_products_by_keywords(["fish"])
        self.assertTrue(r.success, "error: get product by keyword failed")
        products = r.result
        self.assertEqual(1, len(products), "error: didn't get 1 store that has the products while the market has 1")
        product = products[0]
        self.assertIn("tuna", product, "error: tuna not found")
        self.assertEqual("tuna", product["tuna"]["Name"], "error: tuna name incorrect")
        self.assertEqual(20, product["tuna"]["Price"], "error: tuna price incorrect")
        self.assertEqual("2", product["tuna"]["Category"], "error: tuna category incorrect")
        self.assertEqual(5, product["tuna"]["Rate"], "error: tuna rate incorrect")

        product2 = self.app.get_products_by_keywords(["z"]).result[0]
        self.assertEqual(product2, product, "error: keywords 'z' and 'fish' should yield the same result")

    def test_get_products_by_keywords_common_keyword(self):
        self.set_stores()
        r = self.app.get_products_by_keywords(["basic", "y"])
        self.assertTrue(r.success, "error: get product by keywords failed")
        products = r.result
        self.assertEqual(2, len(products), "error: didn't get 2 stores that has the products while the market has 2")
        bakery = products[0]
        market = products[1]
        self.assertIn("pita", bakery, "error: pita not found")
        self.assertEqual("pita", bakery["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(5, bakery["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", bakery["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, bakery["pita"]["Rate"], "error: pita rate incorrect")
        self.assertIn("bread", bakery, "error: bread not found")
        self.assertEqual("bread", bakery["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, bakery["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", bakery["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, bakery["bread"]["Rate"], "error: bread rate incorrect")
        self.assertIn("pita", market, "error: pita not found")
        self.assertEqual("pita", market["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(8, market["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", market["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, market["pita"]["Rate"], "error: pita rate incorrect")

    def test_get_products_by_keywords_no_match(self):
        self.set_stores()
        r = self.app.get_products_by_keywords(["xxx"])
        self.assertTrue(r.success, "error: get product by keyword failed")
        self.assertEqual(0, len(r.result), "error: found keyword xxx")

    def test_get_products_in_price_range_unique_range(self):
        self.set_stores()
        r = self.app.get_products_in_price_range(15, 20)
        self.assertTrue(r.success, "error: get product by price range failed")
        products = r.result
        self.assertEqual(1, len(products), "error: didn't get 1 store that has the products while the market has 1")
        product = products[0]
        self.assertIn("tuna", product, "error: tuna not found")
        self.assertEqual("tuna", product["tuna"]["Name"], "error: tuna name incorrect")
        self.assertEqual(20, product["tuna"]["Price"], "error: tuna price incorrect")
        self.assertEqual("2", product["tuna"]["Category"], "error: tuna category incorrect")
        self.assertEqual(5, product["tuna"]["Rate"], "error: tuna rate incorrect")

    def test_get_products_in_price_range_common_range(self):
        self.set_stores()
        r = self.app.get_products_in_price_range(5, 15)
        self.assertTrue(r.success, "error: get product by price range failed")
        products = r.result
        self.assertEqual(2, len(products), "error: didn't get 2 stores that has the products while the market has 2")
        bakery = products[0]
        market = products[1]
        self.assertIn("pita", bakery, "error: pita not found")
        self.assertEqual("pita", bakery["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(5, bakery["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", bakery["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, bakery["pita"]["Rate"], "error: pita rate incorrect")
        self.assertIn("bread", bakery, "error: bread not found")
        self.assertEqual("bread", bakery["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, bakery["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", bakery["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, bakery["bread"]["Rate"], "error: bread rate incorrect")
        self.assertIn("pita", market, "error: pita not found")
        self.assertEqual("pita", market["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(8, market["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", market["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, market["pita"]["Rate"], "error: pita rate incorrect")

    def test_get_products_in_price_range_no_match(self):
        self.set_stores()
        r = self.app.get_products_in_price_range(0, 4)
        self.assertTrue(r.success, "error: get product by price range failed")
        self.assertEqual(0, len(r.result), "error: found product in price range")

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
