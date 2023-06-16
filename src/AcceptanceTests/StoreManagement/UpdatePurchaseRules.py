from unittest.mock import patch

from Service.bridge.proxy import Proxy
import unittest


class Login(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr11", "password")
        cls.registered_buyer1 = ("usr2", "password")
        cls.service_admin = ('Kfir', 'Kfir')
        cls.provision_path = 'src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter' \
                             '.provisionService.getDelivery'
        cls.payment_pay_path = 'src.domain.main.ExternalServices.Payment.ExternalPaymentServices' \
                               '.ExternalPaymentServiceReal.payWIthCard'
        cls.payment_refund_path = 'src.domain.main.ExternalServices.Payment.ExternalPaymentServices' \
                                  '.ExternalPaymentServiceReal.refundToCard'

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.logout()
        self.app.register(*self.store_founder1)
        self.app.register(*self.registered_buyer1)
        self.set_store()

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_simple_rule_greater_happy(self):
        with patch(self.provision_path, return_value=True) as delivery_mock, \
                patch(self.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", ">", 5)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 8)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_called_once_with(15)
            delivery_mock.assert_not_called()

    def test_simple_rule_greater_sad(self):
        with patch(self.provision_path, return_value=True) as delivery_mock, \
                patch(self.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", ">", 5)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_simple_rule_equal(self):
        with patch(self.provision_path, return_value=True) as delivery_mock, \
                patch(self.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", "=", 5)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_simple_rule_lesser(self):
        with patch(self.provision_path, return_value=True) as delivery_mock, \
                patch(self.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_simple_rule("bakery", "bread", ">", 5)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()


    def test_basket_rule(self):
        with patch(self.provision_path, return_value=True) as delivery_mock, \
                patch(self.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_basket_purchase_rule("bakery", 20)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_and_rule(self):
        with patch(self.provision_path, return_value=True) as delivery_mock, \
                patch(self.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", ">", 20, "and")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_conditioning_rule(self):
        with patch(self.provision_path, return_value=True) as delivery_mock, \
                patch(self.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", ">", 20, "cond")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_or_rule(self):
        with patch(self.provision_path, return_value=True) as delivery_mock, \
                patch(self.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder1)
            self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", ">", 20, "cond")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            self.app.add_to_cart("bakery", "bread", 3)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment succeeded")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_multiple_rules(self):
        ...
    def set_store(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
