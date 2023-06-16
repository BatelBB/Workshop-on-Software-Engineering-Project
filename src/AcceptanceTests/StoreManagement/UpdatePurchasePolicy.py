from unittest.mock import patch
from Service.bridge.proxy import Proxy
import unittest
from domain.main.Market.Permissions import Permission


class UpdatePurchasePolicy(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.store_owner1 = ("usr3", "password")
        cls.store_owner2 = ("usr6", "password")
        cls.store_manager = ("usr4", "password")
        cls.registered_user = ("user5", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.store_manager)
        self.app.register(*self.registered_user)
        self.set_store()

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    # managers and owners with Permission.StartBid can start a bid
    # only owners with Permission.ApproveBid can approve bid

    def test_approve_bid_founder_started_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            self.offer_bid()
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")

            payment_mock.assert_called_once_with(10.5)
            delivery_mock.assert_called_once()

    def test_approve_bid_owner_started_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_owner1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            self.offer_bid()
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")

            payment_mock.assert_called_once_with(10.5)
            delivery_mock.assert_called_once()

    def test_approve_bid_manager_started_happy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_manager)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            self.offer_bid()
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")

            payment_mock.assert_called_once_with(10.5)
            delivery_mock.assert_called_once()

    def test_start_bid_owner_without_permission(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            self.app.remove_permission("bakery", self.store_owner1[0], Permission.StartBid)
            self.app.logout()
            self.app.login(*self.store_owner1)
            r = self.app.start_bid("bakery", "bread")
            self.assertFalse(r.success, "error: start bid action succeeded")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertFalse(r.success, "error: offer a bid action succeeded")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_start_bid_manager_without_permission(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            self.app.remove_permission("bakery", self.store_manager[0], Permission.StartBid)
            self.app.logout()
            self.app.login(*self.store_manager)
            r = self.app.start_bid("bakery", "bread")
            self.assertFalse(r.success, "error: start bid action succeeded")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertFalse(r.success, "error: offer a bid action succeeded")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_not_approve_bid(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            self.offer_bid()
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread", False)
            self.assertTrue(r.success, "error: approve bid action failed")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_approve_bid_accept_higher_bid(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            self.offer_bid()
            self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                        "ben-gurion", "1234", 20, "beer sheva", "israel")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")

            payment_mock.assert_called_once_with(20)
            delivery_mock.assert_called_once()

    def test_approve_bid_after_removing_owner_appointment(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            self.offer_bid()
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            r = self.app.remove_appointment(self.store_owner2[0], "bakery")
            self.assertTrue(r.success, "error: remove appointment action failed")

            payment_mock.assert_called_once_with(10.5)
            delivery_mock.assert_called_once()

    def test_approve_bid_after_removing_owner_permission(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            self.offer_bid()
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            r = self.app.remove_permission("bakery", self.store_owner2[0], Permission.ApproveBid)
            self.assertTrue(r.success, "error: remove appointment action failed")

            payment_mock.assert_called_once_with(10.5)
            delivery_mock.assert_called_once()

    def test_start_bid_invalid_product_name(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "xxx")
            self.assertFalse(r.success, "error: start bid action succeeded")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertFalse(r.success, "error: offer a bid action succeeded")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "xxx")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "xxx")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "xxx")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_add_to_cart_all_stock_before_bid_started(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.add_to_cart("bakery", "bread", 15)
            self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                            "ben-gurion", "1234", "beer sheva", "israel")
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertFalse(r.success, "error: start bid action succeeded when no quantity left")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertFalse(r.success, "error: offer a bid action succeeded")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_called_once_with(150)
            delivery_mock.assert_called_once()

    def test_add_to_cart_all_stock_after_bid_started_before_offer(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            r = self.app.add_to_cart("bakery", "bread", 15)
            self.assertFalse(r.success, "error: add to cart action succeeded with exceeding amount")
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchase cart action succeeded when cart should be empty")
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertTrue(r.success, "error: offer a bid action failed")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")

            payment_mock.assert_called_once_with(10.5)
            delivery_mock.assert_called_once()

    def test_add_to_cart_all_stock_after_offer_before_approval(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertTrue(r.success, "error: offer a bid action failed")
            r = self.app.add_to_cart("bakery", "bread", 15)
            self.assertFalse(r.success, "error: add to cart action succeeded with exceeding amount")
            r = self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertFalse(r.success, "error: purchase cart action succeeded when cart should be empty")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")

            payment_mock.assert_called_once_with(10.5)
            delivery_mock.assert_called_once()

    def test_start_bid_removed_product_before_bid_started(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            self.app.remove_product("bakery", "bread")
            r = self.app.start_bid("bakery", "bread")
            self.assertFalse(r.success, "error: start bid action succeeded")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertFalse(r.success, "error: offer a bid action succeeded")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_approve_bid_removed_product_after_bid_started_before_offer(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            r = self.app.remove_product("bakery", "bread")
            self.assertTrue(r.success, "error: remove product action failed")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertFalse(r.success, "error: offer a bid action succeeded")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_approve_bid_removed_product_after_bid_started_after_offer(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertTrue(r.success, "error: offer a bid action failed")
            self.app.login(*self.store_founder1)
            r = self.app.remove_product("bakery", "bread")
            self.assertTrue(r.success, "error: remove product action failed")
            self.app.logout()
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_start_bid_closed_store_before_bid_started(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            self.app.close_store("bakery")
            r = self.app.start_bid("bakery", "bread")
            self.assertFalse(r.success, "error: start bid action succeeded")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertFalse(r.success, "error: offer a bid action succeeded")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_approve_bid_closed_store_after_bid_started_before_offer(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            r = self.app.close_store("bakery")
            self.assertTrue(r.success, "error: close store action failed")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertFalse(r.success, "error: offer a bid action succeeded")
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def test_approve_bid_closed_store_after_bid_started_after_offer(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start bid action failed")
            self.app.logout()
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertTrue(r.success, "error: offer a bid action failed")
            self.app.login(*self.store_founder1)
            r = self.app.close_store("bakery")
            self.assertTrue(r.success, "error: close store action failed")
            self.app.logout()
            self.app.login(*self.store_owner1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_owner2)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

            payment_mock.assert_not_called()
            delivery_mock.assert_not_called()

    def set_store(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.appoint_manager(self.store_manager[0], "bakery")
        self.app.add_permission("bakery", self.store_manager[0], Permission.StartBid)
        self.app.appoint_owner(self.store_owner1[0], "bakery")
        self.app.appoint_owner(self.store_owner2[0], "bakery")
        self.app.logout()
        self.app.login(*self.store_owner1)
        self.app.approve_owner(self.store_owner2[0], "bakery")
        self.app.logout()

    def offer_bid(self):
        self.app.login(*self.registered_user)
        self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                    "ben-gurion", "1234", 10.5, "beer sheva", "israel")
        self.app.logout()
