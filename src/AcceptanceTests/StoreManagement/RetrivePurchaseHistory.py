from Service.bridge.proxy import Proxy
import unittest
from unittest.mock import patch


class PurchaseCart(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.store_founder2 = ("usr2", "password")
        cls.registered_buyer = ("usr3", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_founder2)
        self.app.register(*self.registered_buyer)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_retrieve_purchase_history_happy(self):
        self.set_stores()
        self.set_cart()
        self.buy_cart()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_purchase_history("bakery")
        self.assertTrue(r.success, "error: get purchase history action failed")
        purchase_history = r.result
        self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 10.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.app.logout()
        self.app.login(*self.store_founder2)
        r = self.app.get_store_purchase_history("market")
        self.assertTrue(r.success, "error: get purchase history action failed")
        purchase_history = r.result
        self.assertIn("Product: 'tuna', Quantity: 15, Price: 20.0, Discount-Price: 20.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.assertIn("Product: 'pita', Quantity: 20, Price: 8.5, Discount-Price: 8.5", purchase_history,
                      "error: the founder see incorrect purchase history")

    def test_retrieve_purchase_history_product_with_discount(self):
        self.set_stores()
        self.app.login(*self.store_founder1)
        self.app.add_simple_discount("bakery", "store", 50)
        self.app.logout()
        self.app.login(*self.store_founder2)
        self.app.add_simple_discount("market", "product", 50, "tuna")
        self.app.logout()
        self.set_cart()
        self.buy_cart()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_purchase_history("bakery")
        self.assertTrue(r.success, "error: get purchase history action failed")
        purchase_history = r.result
        self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 5.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 2.5", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.app.logout()
        self.app.login(*self.store_founder2)
        r = self.app.get_store_purchase_history("market")
        self.assertTrue(r.success, "error: get purchase history action failed")
        purchase_history = r.result
        self.assertIn("Product: 'tuna', Quantity: 15, Price: 20.0, Discount-Price: 10.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.assertIn("Product: 'pita', Quantity: 20, Price: 8.5, Discount-Price: 8.5", purchase_history,
                      "error: the founder see incorrect purchase history")

    def test_retrieve_purchase_history_bid_purchase(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.set_stores()
            self.app.login(*self.store_founder1)
            self.app.start_bid("bakery", "bread")
            self.app.logout()
            self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                        "ben-gurion", "1234", 15.5, "beer sheva", "israel")
            self.app.login(*self.store_founder1)
            self.app.approve_bid("bakery", "bread")
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'bread', Quantity: 1, Price: 15.5, Discount-Price: 15.5", purchase_history,
                          "error: the founder see incorrect purchase history")

    def test_retrieve_purchase_history_removed_product_before_purchase(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.remove_product("bakery", "bread")
            self.app.remove_product("bakery", "pita")
            self.app.logout()
            self.buy_cart()
            self.app.login(*self.store_founder1)
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertEqual(0, purchase_history, "error: purchase history not empty after purchase of removed product")
            self.app.logout()
            self.app.login(*self.store_founder2)
            r = self.app.get_store_purchase_history("market")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'tuna', Quantity: 15, Price: 20.0, Discount-Price: 20.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.assertIn("Product: 'pita', Quantity: 20, Price: 8.5, Discount-Price: 8.5", purchase_history,
                          "error: the founder see incorrect purchase history")

    def test_retrieve_purchase_history_removed_product_after_purchase(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.set_stores()
            self.set_cart()
            self.buy_cart()
            self.app.login(*self.store_founder1)
            self.app.remove_product("bakery", "bread")
            self.app.remove_product("bakery", "pita")
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 10.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.app.logout()
            self.app.login(*self.store_founder2)
            r = self.app.get_store_purchase_history("market")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'tuna', Quantity: 15, Price: 20.0, Discount-Price: 20.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.assertIn("Product: 'pita', Quantity: 20, Price: 8.5, Discount-Price: 8.5", purchase_history,
                          "error: the founder see incorrect purchase history")

    def test_retrieve_purchase_history_changed_product_name_before_purchase(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.change_product_name("bakery", "bread", "new_bread")
            self.app.logout()
            self.buy_cart()
            self.app.login(*self.store_founder1)
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'new_bread', Quantity: 5, Price: 10.0, Discount-Price: 10.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.app.logout()

    def test_retrieve_purchase_history_changed_product_name_after_purchase(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.set_stores()
            self.set_cart()
            self.buy_cart()
            self.app.login(*self.store_founder1)
            self.app.change_product_name("bakery", "bread", "new_bread")
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 10.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.app.logout()

    def test_retrieve_purchase_history_changed_product_price_before_purchase(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.change_product_price("bakery", 10, 20)
            self.app.logout()
            self.buy_cart()
            self.app.login(*self.store_founder1)
            self.app.change_product_price("bakery", 10, 20)
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'bread', Quantity: 5, Price: 20.0, Discount-Price: 20.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.app.logout()

    def test_retrieve_purchase_history_changed_product_price_after_purchase(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.set_stores()
            self.set_cart()
            self.buy_cart()
            self.app.login(*self.store_founder1)
            self.app.change_product_price("bakery", 10, 20)
            r = self.app.get_store_purchase_history("bakery")
            self.assertTrue(r.success, "error: get purchase history action failed")
            purchase_history = r.result
            self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 10.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                          "error: the founder see incorrect purchase history")
            self.app.logout()

    def test_retrieve_purchase_history_changed_product_discount_before_purchase(self):
        self.set_stores()
        self.set_cart()
        self.app.login(*self.store_founder1)
        self.app.add_simple_discount("bakery", "store", 50)
        self.app.logout()
        self.buy_cart()
        self.app.login(*self.store_founder1)
        r = self.app.get_store_purchase_history("bakery")
        self.assertTrue(r.success, "error: get purchase history action failed")
        purchase_history = r.result
        self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 5.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 2.5", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.app.logout()

    def test_retrieve_purchase_history_changed_product_discount_after_purchase(self):
        self.set_stores()
        self.set_cart()
        self.buy_cart()
        self.app.login(*self.store_founder1)
        self.app.add_simple_discount("bakery", "store", 50)
        r = self.app.get_store_purchase_history("bakery")
        self.assertTrue(r.success, "error: get purchase history action failed")
        purchase_history = r.result
        self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 10.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.app.logout()

    def test_retrieve_purchase_history_closed_store(self):
        self.set_stores()
        self.set_cart()
        self.buy_cart()
        self.app.login(*self.store_founder1)
        self.app.close_store("bakery")
        r = self.app.get_store_purchase_history("bakery")
        self.assertTrue(r.success, "error: get purchase history action failed")
        purchase_history = r.result
        self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 10.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.app.logout()

    def test_retrieve_purchase_history_removed_store(self):
        self.set_stores()
        self.set_cart()
        self.buy_cart()
        self.app.login(*self.store_founder1)
        self.app.remove_store("bakery")
        r = self.app.get_store_purchase_history("bakery")
        self.assertTrue(r.success, "error: get purchase history action failed")
        purchase_history = r.result
        self.assertIn("Product: 'bread', Quantity: 5, Price: 10.0, Discount-Price: 10.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.assertIn("Product: 'pita', Quantity: 10, Price: 5.0, Discount-Price: 5.0", purchase_history,
                      "error: the founder see incorrect purchase history")
        self.app.logout()

    def set_stores(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        self.app.login(*self.store_founder2)
        self.app.open_store("market")
        self.app.add_product("market", "tuna", "1", 20, 40, ["basic", "z"])
        self.app.add_product("market", "pita", "1", 8.5, 25, ["basic", "y"])
        self.app.logout()

    def set_cart(self):
        self.app.login(*self.registered_buyer)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("bakery", "pita", 10)
        self.app.add_to_cart("market", "tuna", 15)
        self.app.add_to_cart("market", "pita", 20)
        self.app.logout()

    def buy_cart(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.app.login(*self.registered_buyer)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: purchase shopping cart action failed")
            self.app.logout()
