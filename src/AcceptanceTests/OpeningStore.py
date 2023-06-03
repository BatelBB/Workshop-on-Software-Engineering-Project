from Service.bridge.proxy import Proxy
import unittest


class OpeningStore(unittest.TestCase):
    app: Proxy
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Proxy()
        cls.registered_user1 = ("usr44", "45sdfgs#$%1")
        cls.registered_user2 = ("usr5", "45sdfgs#$%1")
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

    def test_member_opening_a_store(self):
        self.app.login(*self.registered_user1)
        r = self.app.open_store("market")
        self.assertTrue(r.success, "error: open store action failed")
        self.app.add_product("market", "tuna", "2", 20, 40, ["fish", "z"])
        products = self.app.get_products_by_name("tuna").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")
        product = products[0]
        self.assertIn("tuna", product, "error: tuna not found")
        self.assertEqual("tuna", product["tuna"]["Name"], "error: tuna name incorrect")
        self.assertEqual(20, product["tuna"]["Price"], "error: tuna price incorrect")
        self.assertEqual("2", product["tuna"]["Category"], "error: tuna category incorrect")
        self.assertEqual(None, product["tuna"]["Rate"], "error: tuna rate incorrect")
        self.app.logout()
        
    def test_guest_opening_a_store(self):
        r = self.app.open_store("market")
        self.assertFalse(r.success, "error: open store action succeeded")
        
    def test_opening_a_store_taken_name(self):
        self.app.login(*self.registered_user1)
        r = self.app.open_store("bakery")
        self.assertTrue(r.success, "error: open store action failed")
        self.app.logout()
        self.app.login(*self.registered_user2)
        r = self.app.open_store("bakery")
        self.assertFalse(r.success, "error: open store action succeeded")
        self.app.logout()
