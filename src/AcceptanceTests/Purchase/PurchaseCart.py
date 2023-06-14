from Service.bridge.proxy import Proxy
import unittest
from unittest.mock import patch


class PurchaseCart(unittest.TestCase):
    app: Proxy = Proxy()
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_owner1 = ("usr11", "password")
        cls.store_owner2 = ("usr4", "password")
        cls.registered_buyer1 = ("usr2", "password")
        cls.registered_buyer2 = ("usr3", "password")
        cls.service_admin = ('Kfir', 'Kfir')

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.registered_buyer1)
        self.app.register(*self.registered_buyer2)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.login(*cls.service_admin)
        cls.app.shutdown()

    def test_member_purchase_cart_happy(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True) as payment_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success and r.result, "error: cart payment with card failed")
            cart = self.app.show_cart().result
            self.assertEqual({}, cart, "error: cart not empty after purchase!")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_called_once()

    def test_guest_purchase_cart_happy(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True) as payment_mock:

            self.set_stores()
            self.app.add_to_cart("bakery", "bread", 5)
            self.app.add_to_cart("bakery", "pita", 10)
            self.app.add_to_cart("market", "tuna", 15)
            self.app.add_to_cart("market", "pita", 20)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success and r.result, "error: cart payment with card failed")
            cart = self.app.show_cart().result
            self.assertEqual({}, cart, "error: cart not empty after purchase!")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_called_once()

    def test_purchase_empty_cart(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True) as payment_mock:

            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchased with empty cart")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_purchase_while_product_quantity_in_store_is_insufficient_due_to_owner_removing_quantity(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True) as payment_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_owner2)
            self.app.update_product_quantity("market", "pita", 10)
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchased pita with quantity 20 while in store only 10")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_purchase_products_while_after_owner_removing_product(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True) as payment_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_owner2)
            self.app.remove_product("market", "pita")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchased pita with quantity 20 while in store only 10")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_purchase_while_product_quantity_in_store_is_insufficient_due_to_owner_closing_the_store(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True) as payment_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.store_owner2)
            self.app.close_store("market")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchased pita with quantity 20 while in store only 10")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_purchase_while_product_quantity_in_store_is_insufficient_due_to_another_purchase(self):
        # first to pay first to take policy test
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True) as payment_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer2)
            self.app.add_to_cart("market", "pita", 10)
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success and r.result, "error: cart payment with card failed")
            self.app.logout()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchased pita after another purchase made the quantity insufficient")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(80)
            delivery_mock.assert_called_once()

    def test_purchase_with_invalid_card(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=False) as payment_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["xxx", "xxx", "xx/xxxx"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment with outdated card not failed")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_not_called()

    def test_purchase_when_payment_fails(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=True) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=False) as payment_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment with outdated card not failed")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_not_called()

    def test_purchase_when_shipping_fails(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=False) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=True) as payment_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.refund',
                      return_value=True) as refund_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment with outdated card not failed")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_called()
            refund_mock.assert_called_once_with(560)

    def test_purchase_when_payment_and_delivery_fails(self):
        with patch('src.domain.main.ExternalServices.Provision.ProvisionServiceAdapter.provisionService.getDelivery',
                   return_value=False) as delivery_mock, \
                patch('src.domain.main.ExternalServices.Payment.PaymentServices.PayWithCard.pay',
                      return_value=False) as payment_mock:

            self.set_stores()
            self.set_cart()
            self.app.login(*self.registered_buyer1)
            cart_before = self.app.show_cart().result
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment with outdated card not failed")
            cart_after = self.app.show_cart().result
            self.assertDictEqual(cart_before, cart_after, "error: cart changed after failed purchase")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_not_called()

    def test_purchase_with_complex_rules_and_discount(self):
    def test_purchase_with_bid(self):

    def test_owner_change_product_name_and_cart_using_old_name_can_purchase(self):
    def test_purchase_after_product_name_changed(self):
    def test_purchase_after_product_price_changed(self):
    def test_purchase_after_product_rule_changed(self):
    def test_purchase_after_product_discount_changed(self):

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

    def set_cart(self):
        self.app.login(*self.registered_buyer1)
        self.app.add_to_cart("bakery", "bread", 5)
        self.app.add_to_cart("bakery", "pita", 10)
        self.app.add_to_cart("market", "tuna", 15)
        self.app.add_to_cart("market", "pita", 20)
        self.app.logout()
