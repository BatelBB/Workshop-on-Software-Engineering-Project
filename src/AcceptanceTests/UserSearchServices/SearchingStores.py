from Service.bridge.proxy import Proxy
import unittest


class SearchingStores(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_owner1 = ("usr11", "password")
        cls.store_owner2 = ("usr2", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_searching_for_a_store_happy(self):
        self.set_stores()
        r = self.app.get_store("bakery")
        self.assertTrue(r.success, "error: bakery store not found")
        store = r.result
        self.assertIn("pita", store, "error: pita not found")
        self.assertEqual("pita", store["pita"]["Name"], "error: pita name incorrect")
        self.assertEqual(5, store["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", store["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, store["pita"]["Rate"], "error: pita rate incorrect")
        self.assertEqual(20, store["pita"]["Quantity"], "error: pita quantity incorrect")
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

        r = self.app.get_store("market")
        self.assertTrue(r.success, "error: market store not found")
        store = r.result
        self.assertIn("pita", store, "error: pita not found")
        self.assertEqual(8, store["pita"]["Price"], "error: pita price incorrect")
        self.assertEqual("1", store["pita"]["Category"], "error: pita category incorrect")
        self.assertEqual(5, store["pita"]["Rate"], "error: pita rate incorrect")
        self.assertEqual(20, store["pita"]["Quantity"], "error: pita quantity incorrect")
        self.assertIn("tuna", store, "error: tuna not found")
        self.assertEqual(20, store["tuna"]["Price"], "error: tuna price incorrect")
        self.assertEqual("1", store["tuna"]["Category"], "error: tuna category incorrect")
        self.assertEqual(5, store["tuna"]["Rate"], "error: tuna rate incorrect")
        self.assertEqual(40, store["tuna"]["Quantity"], "error: tuna quantity incorrect")

    def test_searching_for_invalid_store(self):
        self.set_stores()
        r = self.app.get_store("xxx")
        self.assertFalse(r.success, "error: invalid store xxx found")

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
