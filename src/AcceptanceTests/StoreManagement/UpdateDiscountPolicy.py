from unittest.mock import patch
from Service.bridge.proxy import Proxy
import unittest


class UpdateDiscountPolicy(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder = ("usr1", "password")
        cls.registered_buyer = ("usr2", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder)
        self.app.register(*self.registered_buyer)
        self.set_store()

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    # discount current id counter := x ,and starts from 0
    # ids of simple discount = x + 1
    # ids of complex discount = x + 3
    # simple discount types: store | category | product
    # discount connectors type: 
    #       xor - must add a rule, if rule holds then only 1 is valid else only 2 is valid
    #       max - choose between 1 or 2 according to the maximum discount for the basket
    #       or - choose between 1 or 2 according to the minimum discount for the basket
    #       add - choose both discounts
    # only xor discount can have a rule
    #
    # rules type: simple | basket | and | or | cond

    def test_add_simple_discount_for_product(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", 50, "bread")
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(325)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_store(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "store", 50)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(175)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_category(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "category", 50, "1")
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(275)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_product_with_simple_rule_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", 50, "bread",
                                             rule_type="simple", p1_name="pita", gle1=">", amount1=5)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(325)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_product_with_simple_rule_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", 50, "bread", rule_type="simple",
                                             p1_name="pita", gle1="=", amount1=20)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_store_with_basket_rule_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "store", 50, rule_type="basket", min_price=300)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(175)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_store_with_basket_rule_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "store", 50, rule_type="basket", min_price=400)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_category_with_conditional_rule_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "category", 50, "1", rule_type="cond",
                                             p1_name="bread", gle1=">", amount1=5, p2_name="pita", gle2="<", amount2=20)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(275)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_category_with_conditional_rule_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "category", 50, "1", rule_type="cond",
                                             p1_name="bread", gle1=">", amount1=5, p2_name="pita", gle2="=", amount2=0)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_product_with_and_rule_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", 50, "bread", rule_type="and",
                                             p1_name="bread", gle1=">", amount1=5, p2_name="pita", gle2=">", amount2=5)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(325)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_product_with_and_rule_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", 50, "bread", rule_type="and",
                                             p1_name="bread", gle1=">", amount1=5, p2_name="pita", gle2=">", amount2=20)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_product_with_or_rule_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", 50, "bread", rule_type="or",
                                             p1_name="bread", gle1="=", amount1=10, p2_name="pita", gle2="=",
                                             amount2=10)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(325)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_product_with_or_rule_sad(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", 50, "bread", rule_type="or",
                                             p1_name="bread", gle1="=", amount1=15, p2_name="pita", gle2="=",
                                             amount2=15)
            self.assertTrue(r.success, "error: add simple discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_xor_discounts_rule_holds(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "bread")
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "xor", rule_type="basket", min_price=300)
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(175)
            delivery_mock.assert_called_once()

    def test_xor_discounts_rule_doesnt_holds(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "bread")
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "xor", rule_type="basket", min_price=500)
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(325)
            delivery_mock.assert_called_once()

    def test_xor_discounts_for_simples_discounts_with_rules(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50, p1_name="bread", gle1="=", amount1=15)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "bread", p1_name="bread", gle1="=", amount1=50)
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "xor", rule_type="basket", min_price=500)
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_max_discounts(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "category", 50, "1")
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "max")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(175)
            delivery_mock.assert_called_once()

    def test_max_discounts_rule_holds(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50, p1_name="bread", gle1=">", amount1=8)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake", p1_name="bread", gle1=">", amount1=8)
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "max")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(175)
            delivery_mock.assert_called_once()

    def test_max_discounts_rule_doesnt_holds(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50, p1_name="bread", gle1=">", amount1=50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake", p1_name="bread", gle1=">", amount1=8)
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "max")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(250)
            delivery_mock.assert_called_once()

    def test_or_discounts(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake")
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "or")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(250)
            delivery_mock.assert_called_once()

    def test_or_discounts_rule_holds(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50, p1_name="bread", gle1="<", amount1=50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake", p1_name="bread", gle1=">", amount1=8)
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "or")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(250)
            delivery_mock.assert_called_once()

    def test_or_discounts_rule_doesnt_hold(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50, p1_name="bread", gle1="<", amount1=50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake", p1_name="bread", gle1=">", amount1=50)
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "or")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(175)
            delivery_mock.assert_called_once()

    def test_add_discounts(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake")
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "add")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(75)
            delivery_mock.assert_called_once()

    def test_add_discounts_rule_holds(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50, p1_name="bread", gle1=">", amount1=8)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake", p1_name="pita", gle1=">", amount1=8)
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "add")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(75)
            delivery_mock.assert_called_once()

    def test_add_discounts_rule_doesnt_holds(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50, p1_name="bread", gle1=">", amount1=8)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake", p1_name="pita", gle1=">", amount1=50)
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", r1.result, r2.result, "add")
            self.assertTrue(r.success, "error: connect discount action failed")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(175)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_product_negative_discount(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", -20, "bread")
            self.assertFalse(r.success, "error: add simple discount action succeeded")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_store_non_positive_discount(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "store", 0)
            self.assertFalse(r.success, "error: add simple discount action succeeded")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_add_simple_discount_for_category_negative_discount(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "category", -20, "1")
            self.assertFalse(r.success, "error: add simple discount action succeeded")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_simple_discounts_invalid_store_name(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("xxx", "product", 50, "bread")
            self.assertFalse(r.success, "error: add simple discount action succeeded")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_simple_discounts_invalid_discount_type(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "xxx", 50)
            self.assertFalse(r.success, "error: add simple discount action succeeded")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_simple_discounts_invalid_product_name(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "product", 50, "xxx")
            self.assertFalse(r.success, "error: add simple discount action succeeded")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_simple_discounts_invalid_category_name(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r = self.app.add_simple_discount("bakery", "category", 50, "xxx")
            self.assertFalse(r.success, "error: add simple discount action succeeded")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(350)
            delivery_mock.assert_called_once()

    def test_connect_discounts_invalid_ids(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.app.login(*self.store_founder)
            r1 = self.app.add_simple_discount("bakery", "store", 50)
            self.assertTrue(r1.success, "error: add simple discount action failed")
            r2 = self.app.add_simple_discount("bakery", "product", 50, "cake")
            self.assertTrue(r2.success, "error: add simple discount action failed")
            r = self.app.connect_discounts("bakery", 1, 8, "max")
            self.assertFalse(r.success, "error: connect discount action with invalid ids succeeded")
            self.app.logout()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(75)
            delivery_mock.assert_called_once()

    def test_discount_ids(self):
        self.app.login(*self.store_founder)
        r1 = self.app.add_simple_discount("bakery", "store", 50)
        self.assertTrue(r1.success, "error: add simple discount action failed")
        self.assertEqual(1, r1.result, "error: discount generated with incorrect id")
        r2 = self.app.add_simple_discount("bakery", "product", 50, "cake")
        self.assertTrue(r2.success, "error: add simple discount action failed")
        self.assertEqual(2, r2.result, "error: discount generated with incorrect id")
        r3 = self.app.add_simple_discount("bakery", "category", 50, "1")
        self.assertTrue(r3.success, "error: add simple discount action failed")
        self.assertEqual(3, r3.result, "error: discount generated with incorrect id")
        r4 = self.app.connect_discounts("bakery", 1, 2, "max")
        self.assertTrue(r4.success, "error: connect discounts action failed")
        self.assertEqual(6, r4.result, "error: discount generated with incorrect id")
        r5 = self.app.connect_discounts("bakery", 6, 3, "or")
        self.assertTrue(r5.success, "error: connect discounts action failed")
        self.assertEqual(9, r5.result, "error: discount generated with incorrect id")
        self.app.logout()

    def test_3_levels_discount(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_3_levels_discount()
            self.set_cart_and_buy()

            payment_mock.assert_called_once_with(325)
            delivery_mock.assert_called_once()

    def set_store(self):
        self.app.login(*self.store_founder)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 5, 40, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 10, 40, ["basic", "y"])
        self.app.add_product("bakery", "cake", "2", 20, 40, ["sweets", "z"])
        self.app.logout()

    def set_cart_and_buy(self):
        self.app.login(*self.registered_buyer)
        self.app.add_to_cart("bakery", "bread", 10)
        self.app.add_to_cart("bakery", "pita", 10)
        self.app.add_to_cart("bakery", "cake", 10)
        r = self.app.purchase_shopping_cart("card", ["1234123412341234", "123", "05/2028"],
                                            "ben-gurion", "1234", "beer sheva", "israel")
        self.assertTrue(r.success, "error: cart payment failed")
        self.app.logout()

    def set_3_levels_discount(self):
        # only r2 discount should be applied
        self.app.login(*self.store_founder)
        r1 = self.app.add_simple_discount("bakery", "store", 30, p1_name="bread", gle1=">", amount1=8)
        self.assertTrue(r1.success, "error: add simple discount action failed")
        r2 = self.app.add_simple_discount("bakery", "product", 50, "bread", p1_name="pita", gle1=">", amount1=8)
        self.assertTrue(r2.success, "error: add simple discount action failed")
        r3 = self.app.add_simple_discount("bakery", "product", 50, "cake", p1_name="cake", gle1=">", amount1=8)
        self.assertTrue(r3.success, "error: add simple discount action failed")
        r4 = self.app.add_simple_discount("bakery", "category", 50, "1", p1_name="bread", gle1="<", amount1=50)
        self.assertTrue(r4.success, "error: add simple discount action failed")

        r5 = self.app.connect_discounts("bakery", r1.result, r2.result, "or")
        self.assertTrue(r5.success, "error: connect discounts action failed")
        r6 = self.app.connect_discounts("bakery", r3.result, r4.result, "max")
        self.assertTrue(r6.success, "error: connect discounts action failed")

        r7 = self.app.connect_discounts("bakery", r5.result, r6.result, "xor", rule_type="basket", min_price=300)
        self.assertTrue(r7.success, "error: connect discounts action failed")
        self.app.logout()
