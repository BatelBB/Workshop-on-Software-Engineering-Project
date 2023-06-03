from Service.bridge.proxy import Proxy
import unittest
from unittest.mock import patch


class PurchaseCart(unittest.TestCase):
    app: Proxy
    service_admin = None

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Proxy()
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

    def test_purchase_empty_cart(self):
        self.app.login(*self.registered_buyer1)
        r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                            "ben-gurion", "1234", "beer sheva", "israel")
        self.assertFalse(r.success, "error: purchased with empty cart")
        self.app.logout()

    def test_purchase_while_product_quantity_in_store_is_insufficient_due_to_owner(self):
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
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchased pita with quantity 20 while in store only 10")
            cart = self.app.show_cart().result
            self.assertIn("bread", cart["bakery"], "error: bread not in cart")
            self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
            self.assertEqual(10, cart["bakery"]["bread"]["Price"], "error: bread price doesn't match")
            self.assertIn("pita", cart["bakery"], "error: pita not in cart")
            self.assertEqual(10, cart["bakery"]["pita"]["Quantity"], "error: pita quantity doesn't match")
            self.assertEqual(5, cart["bakery"]["pita"]["Price"], "error: pita price doesn't match")
            self.assertIn("tuna", cart["market"], "error: tuna not in cart")
            self.assertEqual(15, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
            self.assertEqual(20, cart["market"]["tuna"]["Price"], "error: tuna price doesn't match")
            self.assertIn("pita", cart["market"], "error: pita not in cart")
            self.assertEqual(20, cart["market"]["pita"]["Quantity"], "error: pita quantity doesn't match the buyer "
                                                                     "added quantity after it lowered by the owner")
            self.assertEqual(8, cart["market"]["pita"]["Price"], "error: pita price doesn't match")
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
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchased pita after another purchase made the quantity insufficient")
            cart = self.app.show_cart().result
            self.assertIn("bread", cart["bakery"], "error: bread not in cart")
            self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
            self.assertEqual(10, cart["bakery"]["bread"]["Price"], "error: bread price doesn't match")
            self.assertIn("pita", cart["bakery"], "error: pita not in cart")
            self.assertEqual(10, cart["bakery"]["pita"]["Quantity"], "error: pita quantity doesn't match")
            self.assertEqual(5, cart["bakery"]["pita"]["Price"], "error: pita price doesn't match")
            self.assertIn("tuna", cart["market"], "error: tuna not in cart")
            self.assertEqual(15, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
            self.assertEqual(20, cart["market"]["tuna"]["Price"], "error: tuna price doesn't match")
            self.assertIn("pita", cart["market"], "error: pita not in cart")
            self.assertEqual(20, cart["market"]["pita"]["Quantity"], "error: pita quantity doesn't match the buyer "
                                                                     "added quantity after it lowered by another "
                                                                     "purchase")
            self.assertEqual(8, cart["market"]["pita"]["Price"], "error: pita price doesn't match")
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
            r = self.app.purchase_shopping_cart("card", ["xxx", "xxx", "xx/xxxx"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment with outdated card not failed")
            cart = self.app.show_cart().result
            self.assertIn("bread", cart["bakery"], "error: bread not in cart")
            self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
            self.assertEqual(10, cart["bakery"]["bread"]["Price"], "error: bread price doesn't match")
            self.assertIn("pita", cart["bakery"], "error: pita not in cart")
            self.assertEqual(10, cart["bakery"]["pita"]["Quantity"], "error: pita quantity doesn't match")
            self.assertEqual(5, cart["bakery"]["pita"]["Price"], "error: pita price doesn't match")
            self.assertIn("tuna", cart["market"], "error: tuna not in cart")
            self.assertEqual(15, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
            self.assertEqual(20, cart["market"]["tuna"]["Price"], "error: tuna price doesn't match")
            self.assertIn("pita", cart["market"], "error: pita not in cart")
            self.assertEqual(20, cart["market"]["pita"]["Quantity"], "error: tuna price doesn't match")
            self.assertEqual(8, cart["market"]["pita"]["Price"], "error: pita price doesn't match")
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
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment with outdated card not failed")
            cart = self.app.show_cart().result
            self.assertIn("bread", cart["bakery"], "error: bread not in cart")
            self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
            self.assertEqual(10, cart["bakery"]["bread"]["Price"], "error: bread price doesn't match")
            self.assertIn("pita", cart["bakery"], "error: pita not in cart")
            self.assertEqual(10, cart["bakery"]["pita"]["Quantity"], "error: pita quantity doesn't match")
            self.assertEqual(5, cart["bakery"]["pita"]["Price"], "error: pita price doesn't match")
            self.assertIn("tuna", cart["market"], "error: tuna not in cart")
            self.assertEqual(15, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
            self.assertEqual(20, cart["market"]["tuna"]["Price"], "error: tuna price doesn't match")
            self.assertIn("pita", cart["market"], "error: pita not in cart")
            self.assertEqual(20, cart["market"]["pita"]["Quantity"], "error: tuna price doesn't match")
            self.assertEqual(8, cart["market"]["pita"]["Price"], "error: pita price doesn't match")
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
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: cart payment with outdated card not failed")
            cart = self.app.show_cart().result
            self.assertIn("bread", cart["bakery"], "error: bread not in cart")
            self.assertEqual(5, cart["bakery"]["bread"]["Quantity"], "error: bread quantity doesn't match")
            self.assertEqual(10, cart["bakery"]["bread"]["Price"], "error: bread price doesn't match")
            self.assertIn("pita", cart["bakery"], "error: pita not in cart")
            self.assertEqual(10, cart["bakery"]["pita"]["Quantity"], "error: pita quantity doesn't match")
            self.assertEqual(5, cart["bakery"]["pita"]["Price"], "error: pita price doesn't match")
            self.assertIn("tuna", cart["market"], "error: tuna not in cart")
            self.assertEqual(15, cart["market"]["tuna"]["Quantity"], "error: tuna quantity doesn't match")
            self.assertEqual(20, cart["market"]["tuna"]["Price"], "error: tuna price doesn't match")
            self.assertIn("pita", cart["market"], "error: pita not in cart")
            self.assertEqual(20, cart["market"]["pita"]["Quantity"], "error: tuna price doesn't match")
            self.assertEqual(8, cart["market"]["pita"]["Price"], "error: pita price doesn't match")
            self.app.logout()

            payment_mock.assert_called_once_with(560)
            delivery_mock.assert_not_called()
            refund_mock.assert_called_once_with(560)

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
