from Service.bridge.proxy import Proxy
import unittest
from domain.main.Market.Permissions import Permission


class SystemAdmin(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.store_owner1 = ("usr3", "password")
        cls.store_manager1 = ("usr4", "password")
        cls.registered_user = ("user5", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_manager1)
        self.app.register(*self.registered_user)
        self.set_stores()
        self.app.login(*self.service_admin)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_cancel_membership_of_a_member(self):
        r = self.app.cancel_membership_of(self.registered_user[0])
        self.assertTrue(r.success, "error: cancel membership action failed")
        self.app.logout()
        r = self.app.login(*self.registered_user)
        self.assertFalse(r.success, "error: canceled membership user succeeded with login")
        r = self.app.open_store("market")
        self.assertFalse(r.success, "error: open store action succeeded")
        r = self.app.get_store("market")
        self.assertFalse(r.success, "error: canceled membership user succeeded to open a store")

    def test_cancel_membership_of_store_founder(self):
        r = self.app.cancel_membership_of(self.store_founder1[0])
        self.assertTrue(r.success, "error: cancel membership action failed")
        self.app.logout()
        r = self.app.login(*self.store_founder1)
        self.assertFalse(r.success, "error: canceled membership user succeeded with login")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: product found added by a canceled membership founder")

    def test_cancel_membership_of_store_owner(self):
        r = self.app.cancel_membership_of(self.store_owner1[0])
        self.assertTrue(r.success, "error: cancel membership action failed")
        self.app.logout()
        r = self.app.login(*self.store_owner1)
        self.assertFalse(r.success, "error: canceled membership user succeeded with login")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: product found added by a canceled membership founder")

    def test_cancel_membership_of_store_manager(self):
        r = self.app.cancel_membership_of(self.store_manager1[0])
        self.assertTrue(r.success, "error: cancel membership action failed")
        r = self.app.login(*self.store_manager1)
        self.assertFalse(r.success, "error: canceled membership user succeeded with login")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        products = self.app.get_products_by_name("bread").result
        self.assertEqual(0, len(products), "error: product found added by a canceled membership founder")

    def set_stores(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.appoint_owner(self.store_owner1[0], "bakery")
        self.app.appoint_owner(self.store_manager1[0], "bakery")
        self.app.add_permission("bakery", self.store_manager1[0], Permission.Add)
        self.app.logout()
