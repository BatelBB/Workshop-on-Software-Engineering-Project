from Service.bridge.proxy import Proxy
import unittest
from unittest.mock import patch


class PurchaseCart(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("bakery founder", "password")
        cls.store_founder2 = ("market founder", "password")
        cls.registered_buyer1 = ("buyer1", "password")
        cls.registered_buyer2 = ("buyer2", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_founder2)
        self.app.register(*self.registered_buyer1)
        self.app.register(*self.registered_buyer2)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    # purchase algorythm try to purchase what he can from each store
    # after a purchase the cart should be empty unless a product quantity doesn't match the store rule
    # if a store rule doesn't match then all store product wouldn't be bought and will remain in cart
    # first to pay first to take policy when the stock is limited

    def test_member_purchase_cart_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_called_once()

    def test_guest_purchase_cart_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.app.add_to_cart("bakery", "bread", 5)
            self.app.add_to_cart("bakery", "pita", 10)
            self.app.add_to_cart("market", "tuna", 15)
            self.app.add_to_cart("market", "pita", 20)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_called_once()

    def test_purchase_empty_cart(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchased with empty cart")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_first_to_pay_first_to_take_policy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer2)
            self.app.add_to_cart("market", "pita", 20)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            self.app.logout()
            payment_mock.assert_called_once_with(160)
            delivery_mock.assert_called()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_with(400)
            delivery_mock.assert_called()

    def test_purchase_with_invalid_card(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["xxx", "xxx", "xx/xxxx"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment with outdated card not failed")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_purchase_when_payment_fails(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=False) as payment_mock, \
                patch(self.app.payment_refund_path, return_value=True) as refund_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            refund_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_purchase_when_shipping_fails(self):
        with patch(self.app.provision_path, return_value=False) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock, \
                patch(self.app.payment_refund_path, return_value=True) as refund_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_called()
            refund_mock.assert_called_once_with(560)

    def test_purchase_when_payment_and_delivery_fails(self):
        with patch(self.app.provision_path, return_value=False) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=False) as payment_mock, \
                patch(self.app.payment_refund_path, return_value=True) as refund_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            refund_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_purchase_with_bid(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.app.login(*self.store_founder1)
            self.app.start_bid("bakery", "bread")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card",
                                                            ["1234567812345678", "123", "05/2028"], "ben-gurion",
                                                            "1234", 50, "beer sheva", "israel")
            self.assertTrue(r.success, "error: bid offer failed")
            self.app.login(*self.store_founder1)
            self.app.approve_bid("bakery", "bread")
            self.app.logout()
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(50)
            delivery_mock.assert_called_once()

    def test_purchase_after_complex_rule_added_rule_doesnt_affect_cart(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", "<", 10, "pita", ">", 50, "or")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_called_once()

    def test_purchase_after_complex_rule_added_rule_affect_cart(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", "<", 10, "pita", ">", 50, "and")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertNotIn("market", cart, "error: market store in cart after purchased successfully from market")
            self.assertIn("bread", cart["bakery"], "error: bread not in cart")
            self.assertIn("pita", cart["bakery"], "error: pita not in cart")
            self.app.logout()

            payment_mock.assert_called_once_with(460)
            delivery_mock.assert_called_once()

    def test_purchase_after_simple_rule_added_rule_affect_cart(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", ">", 10)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertNotIn("market", cart, "error: market store in cart after purchased successfully from market")
            self.assertIn("bread", cart["bakery"], "error: bread not in cart")
            self.assertIn("pita", cart["bakery"], "error: pita not in cart")
            self.app.logout()

            payment_mock.assert_called_once_with(460)
            delivery_mock.assert_called_once()

    def test_purchase_after_product_discount_changed(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.add_simple_discount("bakery", "store", 50)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(510)
            delivery_mock.assert_called_once()

    def test_purchase_after_product_name_changed(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.change_product_name("bakery", "bread", "new_bread")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_called_once()

    def test_purchase_after_product_price_changed(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder1)
            self.app.change_product_price("bakery", 10, 20)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(610)
            delivery_mock.assert_called_once()

    def test_purchase_after_founder_update_to_lower_quantity(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder2)
            self.app.update_product_quantity("market", "pita", 10)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(480)
            delivery_mock.assert_called_once()

    def test_purchase_after_founder_removing_product(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder2)
            self.app.remove_product("market", "pita")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(400)
            delivery_mock.assert_called_once()

    def test_purchase_after_closing_a_store(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_founder2)
            self.app.close_store("market")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(100)
            delivery_mock.assert_called_once()

    # todo
    def test_purchase_with_complex_rules_and_discount(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_stores()
            self.set_complex_rules_and_discounts()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["1234567812345678", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: payment failed")
            cart = self.app.show_cart().result
            self.assertDictEqual({}, cart, "error: cart not empty after a purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(100)
            delivery_mock.assert_called_once()

    def set_stores(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        self.app.login(*self.store_founder2)
        self.app.open_store("market")
        self.app.add_product("market", "tuna", "1", 20, 40, ["basic", "z"])
        self.app.add_product("market", "pita", "1", 8, 20, ["basic", "y"])
        self.app.logout()

    def set_cart(self):
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("bakery", "pita", 10)
        self.app.add_to_cart("market", "tuna", 15)
        self.app.add_to_cart("market", "pita", 20)
        self.app.logout()

    def set_complex_rules_and_discounts(self):
        ...
