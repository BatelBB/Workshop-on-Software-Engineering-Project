from unittest.mock import patch
from Service.bridge.proxy import Proxy
import unittest


class UpdatePurchaseRules(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr11", "password")
        cls.registered_buyer1 = ("usr2", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.registered_buyer1)
        self.set_store()

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_simple_rule_greater_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", ">", 5)
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 8)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(80)
            delivery_mock.assert_called_once()

    def test_simple_rule_greater_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", ">", 5)
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_simple_rule_equal_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", "=", 5)
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 5)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(50)
            delivery_mock.assert_called_once()

    def test_simple_rule_equal_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", "=", 5)
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 8)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_simple_rule_lesser_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", "<", 5)
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(30)
            delivery_mock.assert_called_once()

    def test_simple_rule_lesser_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", "<", 5)
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 8)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_basket_rule_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_basket_purchase_rule("bakery", 20)
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(30)
            delivery_mock.assert_called_once()

    def test_basket_rule_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_basket_purchase_rule("bakery", 20)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 1)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_and_rule_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 5, "pita", "<", 8, "and")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 6)
            self.app.add_to_cart("bakery", "pita", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(75)
            delivery_mock.assert_called_once()

    def test_and_rule_sad_second_rule(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", "=", 6, "pita", ">", 2, "and")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 6)
            self.app.add_to_cart("bakery", "pita", 2)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_and_rule_sad_first_rule(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 5, "pita", ">", 2, "and")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 5)
            self.app.add_to_cart("bakery", "pita", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_and_rule_sad_both_rules(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", "=", 8, "pita", ">", 2, "and")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 5)
            self.app.add_to_cart("bakery", "pita", 2)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_conditioning_rule_happy_both_rules(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", "<", 10, "pita", ">", 2, "cond")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 5)
            self.app.add_to_cart("bakery", "pita", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(65)
            delivery_mock.assert_called_once()

    def test_conditioning_rule_happy_not_first_rule(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", ">", 20, "cond")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(30)
            delivery_mock.assert_called_once()

    def test_conditioning_rule_sad_only_first_rule(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", "=", 20, "cond")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 15)
            self.app.add_to_cart("bakery", "pita", 4)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_or_rule_happy_first_rule(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", ">", 20, "or")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 15)
            self.app.add_to_cart("bakery", "pita", 4)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(170)
            delivery_mock.assert_called_once()

    def test_or_rule_happy_second_rule(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", "=", 4, "or")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 5)
            self.app.add_to_cart("bakery", "pita", 4)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(70)
            delivery_mock.assert_called_once()

    def test_or_rule_happy_both_rules(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", "<", 10, "pita", "<", 20, "or")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 3)
            self.app.add_to_cart("bakery", "pita", 4)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(50)
            delivery_mock.assert_called_once()

    def test_or_rule_sad_both_rules(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", ">", 10, "or")
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 5)
            self.app.add_to_cart("bakery", "pita", 4)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_multiple_rules_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_complex_rules()
            self.app.add_to_cart("bakery", "bread", 30)
            self.app.add_to_cart("bakery", "pita", 20)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: cart payment failed")

            payment_mock.assert_called_once_with(400)
            delivery_mock.assert_called_once()

    def test_multiple_rules_sad_basket_price(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_complex_rules()
            self.app.add_to_cart("bakery", "bread", 10)
            self.app.add_to_cart("bakery", "pita", 24)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_multiple_rules_sad_cond_rule(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_complex_rules()
            self.app.add_to_cart("bakery", "bread", 37)
            self.app.add_to_cart("bakery", "pita", 35)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def set_store(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 100, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 100, ["basic", "y"])
        self.app.logout()

    def set_complex_rules(self):
        self.app.login(*self.store_founder1)
        self.app.add_purchase_simple_rule("bakery", "bread", ">", 5)
        self.app.add_purchase_simple_rule("bakery", "bread", "<", 50)
        self.app.add_purchase_simple_rule("bakery", "pita", ">", 5)
        self.app.add_purchase_simple_rule("bakery", "pita", "<", 100)
        self.app.add_purchase_complex_rule("bakery", "bread", "<", 40, "pita", ">", 10, "and")
        self.app.add_purchase_complex_rule("bakery", "bread", ">", 20, "pita", ">", 20, "or")
        self.app.add_purchase_complex_rule("bakery", "bread", ">", 35, "pita", "<", 30, "cond")
        self.app.add_basket_purchase_rule("bakery", 300)
        self.app.logout()
