from unittest.mock import patch
from Service.bridge.proxy import Proxy
import unittest
from domain.main.Market.Permissions import Permission


class SystemAdmin(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.store_founder2 = ("usr2", "password")
        cls.store_owner1 = ("usr3", "password")
        cls.store_manager1 = ("usr4", "password")
        cls.registered_user = ("user5", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_founder2)
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_manager1)
        self.app.register(*self.registered_user)
        self.set_stores()
        self.app.login(*self.app.system_admin)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_cancel_membership_of_a_member(self):
        r = self.app.cancel_membership_of(self.registered_user[0])
        self.assertTrue(r.success, "error: cancel membership action failed")
        self.app.logout()
        r = self.app.login(*self.registered_user)
        self.assertFalse(r.success, "error: canceled membership user succeeded with login")
        r = self.app.open_store("WHATEVER") # Mendy store 'market' is opened since you open it from set_stores()
        self.assertFalse(r.success, "error: open store action succeeded")
        r = self.app.get_store("WHATEVER")
        self.assertFalse(r.success, "error: canceled membership user succeeded to open a store")

    def test_cancel_membership_of_store_founder(self):
        r = self.app.cancel_membership_of(self.store_founder1[0])
        self.assertFalse(r.success, "error: cancel membership action succeeded")
        self.app.logout()
        r = self.app.login(*self.store_founder1)
        self.assertTrue(r.success, "error: founder failed with login")
        r = self.app.add_product("bakery", "lafa", "1", 10, 15, ["basic", "x"])
        self.assertTrue(r.success, "error: add product action failed")
        products = self.app.get_products_by_name("lafa").result
        self.assertEqual(1, len(products), "error: product added by a founder not found")

    def test_cancel_membership_of_store_owner(self):
        r = self.app.cancel_membership_of(self.store_owner1[0])
        self.assertFalse(r.success, "error: cancel membership action succeeded")
        self.app.logout()
        r = self.app.login(*self.store_owner1)
        self.assertTrue(r.success, "error: owner failed with login")
        r = self.app.add_product("bakery", "lafa", "1", 10, 15, ["basic", "x"])
        self.assertTrue(r.success, "error: add product action failed")
        products = self.app.get_products_by_name("lafa").result
        self.assertEqual(1, len(products), "error: product added by a owner not found")

    def test_cancel_membership_of_store_manager(self):
        r = self.app.cancel_membership_of(self.store_manager1[0])
        self.assertFalse(r.success, "error: cancel membership action succeeded")
        self.app.logout()
        r = self.app.login(*self.store_manager1)
        self.assertTrue(r.success, "error: manager failed with login")
        r = self.app.add_product("bakery", "lafa", "1", 10, 15, ["basic", "x"])
        self.assertTrue(r.success, "error: add product action failed")
        products = self.app.get_products_by_name("lafa").result
        self.assertEqual(1, len(products), "error: product added by a manager not found")

    def test_retrieve_purchase_history(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.set_stores()
            self.app.add_to_cart("bakery", "bread", 10)
            self.app.add_to_cart("bakery", "pita", 15)
            self.app.add_to_cart("market", "tuna", 30)
            self.app.add_to_cart("market", "pita", 5)
            self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                            "ben-gurion", "1234", "beer sheva", "israel")
            self.app.login(*self.app.system_admin)
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'bread', Quantity: 10, Price: 10.0, Discount-Price: 10.0", purchase_history,
                          "error: the admin can't see the purchase history")
            self.assertIn("Product: 'pita', Quantity: 15, Price: 5.0, Discount-Price: 5.0", purchase_history,
                          "error: the admin can't see the purchase history")
            r = self.app.get_store_purchase_history("market")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'tuna', Quantity: 30, Price: 20.0, Discount-Price: 20.0", purchase_history,
                          "error: the admin can't see the purchase history")
            self.assertIn("Product: 'pita', Quantity: 5, Price: 8.5, Discount-Price: 8.5", purchase_history,
                          "error: the admin can't see the purchase history")

    def set_stores(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.appoint_owner(self.store_owner1[0], "bakery")
        self.app.appoint_manager(self.store_manager1[0], "bakery")
        self.app.add_permission("bakery", self.store_manager1[0], Permission.Add)
        self.app.logout()
        self.app.login(*self.store_founder2)
        self.app.open_store("market")
        self.app.add_product("market", "tuna", "1", 20, 40, ["basic", "z"])
        self.app.add_product("market", "pita", "1", 8.5, 20, ["basic", "y"])
        self.app.logout()
