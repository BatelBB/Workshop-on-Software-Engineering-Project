from unittest.mock import patch
import unittest
from Service.bridge.proxy import Proxy
from domain.main.Market import Permissions
from domain.main.Market.Permissions import Permission


class RemoveManager(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.store_founder2 = ("usr2", "password")
        cls.store_owner1 = ("usr3", "password")
        cls.store_owner2 = ("usr6", "password")
        cls.store_manager1 = ("usr4", "password")
        cls.store_manager2_2 = ("usr7", "password")
        cls.store_manager1_2 = ("usr10", "password")
        cls.store_owner1_2 = ("usr8", "password")
        cls.store_owner2_2 = ("usr9", "password")
        cls.registered_user = ("user5", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.store_founder2)
        self.app.register(*self.store_owner1)
        self.app.register(*self.store_owner2)
        self.app.register(*self.store_manager1)
        self.app.register(*self.store_manager1_2)
        self.app.register(*self.store_manager2_2)
        self.app.register(*self.store_owner1_2)
        self.app.register(*self.store_owner2_2)
        self.app.register(*self.registered_user)

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_product_added_by_manager_is_in_store_after_manager_removed(self):
        self.set_store_and_appointments()
        products = self.app.get_products_by_name("pita").result
        self.assertEqual(1, len(products), "error: didn't get 1 stores that has the products while the market has 1")

    def test_fail_to_retrieve_purchase_history(self):
        with patch(self.app.provision_path, return_value=True), \
                patch(self.app.payment_pay_path, return_value=True):

            self.set_store_and_appointments()
            self.app.add_to_cart("bakery", "bread", 10)
            self.app.purchase_shopping_cart("card", ["123", "123", "12/6588"],
                                            "ben-gurion", "1234", "beer sheva", "israel")
            self.app.login(*self.store_manager1)
            r = self.app.get_store_purchase_history("bakery")
            self.assertFalse(r.success, "error: get purchase history action succeeded")
            self.assertEqual(None, r.result, "error: manager got purchase history after removed")

    def test_fail_to_retrieve_staff_details(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.get_store_staff("bakery")
        self.assertFalse(r.success, "error: get staff details action succeeded")
        self.assertEqual(None, r.result, "error: manager got staff details after removed")

    def test_fail_to_add_product(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.add_product("bakery", "lafa", "1", 5, 20, ["basic", "x"])
        self.assertFalse(r.success, "error: add product action succeeded")
        store = self.app.get_store("bakery").result
        self.assertNotIn("lafa", store, "error: lafa found")

    def test_fail_to_update_product_quantity(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.update_product_quantity("bakery", "bread", 50)
        self.assertFalse(r.success, "error: update product quantity action succeeded")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_update_product_name(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.change_product_name("bakery", "bread", "new_bread")
        self.assertFalse(r.success, "error: update product quantity action succeeded")
        store = self.app.get_store("bakery").result
        self.assertNotIn("new_bread", store, "error: new_bread found")
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_update_product_price(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.change_product_price("bakery", 10, 30)
        self.assertFalse(r.success, "error: update product price action succeeded")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_update_product_category(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.change_product_category("bakery", "bread", "gluten")
        self.assertFalse(r.success, "error: update product price action succeeded")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_remove_product(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.remove_product("bakery", "bread")
        self.assertFalse(r.success, "error: remove product action succeeded")
        store = self.app.get_store("bakery").result
        self.assertIn("bread", store, "error: bread not found")
        self.assertEqual("bread", store["bread"]["Name"], "error: bread name incorrect")
        self.assertEqual(10, store["bread"]["Price"], "error: bread price incorrect")
        self.assertEqual("1", store["bread"]["Category"], "error: bread category incorrect")
        self.assertEqual(5, store["bread"]["Rate"], "error: bread rate incorrect")
        self.assertEqual(15, store["bread"]["Quantity"], "error: bread quantity incorrect")

    def test_fail_to_appoint_owner(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.appoint_owner(self.registered_user[0], "bakery")
        self.assertFalse(r.success, "error: appoint owner action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        appointment = self.app.get_store_staff("bakery").result
        self.assertNotIn(self.registered_user[0], appointment)
        self.assertNotIn(self.store_manager1[0], appointment)

    def test_fail_to_appoint_manager(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.appoint_manager(self.registered_user[0], "bakery")
        self.assertFalse(r.success, "error: appoint manager action succeeded")
        self.app.logout()
        self.app.login(*self.store_founder1)
        appointment = self.app.get_store_staff("bakery").result
        self.assertNotIn(self.registered_user[0], appointment)
        self.assertNotIn(self.store_manager1[0], appointment)

    def test_fail_to_interact_with_a_customer(self):
        ...

    def test_fail_to_add_rule(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r1 = self.app.add_purchase_simple_rule("bakery", "bread", ">", 10)
        self.assertFalse(r1.success, "error: add simple rule action succeeded")
        r2 = self.app.add_basket_purchase_rule("bakery", 300)
        self.assertFalse(r2.success, "error: add basket rule action succeeded")
        r3 = self.app.add_purchase_complex_rule("bakery", "bread", ">", 10, "pita", ">", 10, "or")
        self.assertFalse(r3.success, "error: add complex rule action succeeded")
        r = self.app.get_purchase_rules("bakery")
        self.assertFalse(r.success, "error: get purchase rule action succeeded")
        self.assertIsNone(r.result, "error: removed manager can see the purchase rules")

    def test_fail_to_change_discount_policy(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:
            self.set_store_and_appointments()
            self.app.login(*self.store_manager1)
            r1 = self.app.add_simple_discount("bakery", "product", 50, "bread")
            self.assertFalse(r1.success, "error: add simple discount action succeeded")
            r2 = self.app.add_simple_discount("bakery", "store", 30)
            self.assertFalse(r2.success, "error: add simple discount action succeeded")
            r3 = self.app.connect_discounts("bakery", 1, 2, "max", "simple",
                                            p1_name="bread", gle1=">", amount1=3)
            self.assertFalse(r3.success, "error: connect discount action succeeded")
            r = self.app.get_discounts("bakery")
            self.assertFalse(r.success, "error: get discounts action succeeded")
            self.assertEqual(None, r.result)
            self.app.logout()
            self.app.add_to_cart("bakery", "bread", 10)
            r = self.app.purchase_shopping_cart("card", ["432143214321", "123", "05/2028"],
                                                "ben-gurion", "1234", "beer sheva", "israel")
            self.assertTrue(r.success, "error: payment failed")

            payment_mock.assert_called_once_with(100)
            delivery_mock.assert_called_once()

    def test_fail_to_start_bid(self):
        self.set_store_and_appointments()
        self.app.login(*self.store_manager1)
        r = self.app.start_bid("bakery", "bread")
        self.assertFalse(r.success, "error: start a bid action succeeded")
        self.app.logout()
        self.app.login(*self.registered_user)
        r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                        "ben-gurion", "1234", 10.5, "beer sheva", "israel")
        self.assertFalse(r.success, "error: purchase with a bid policy succeeded")
        r = self.app.get_bid_products("bakery")
        self.assertTrue(r.success, "error: get bid product action failed")
        self.assertNotIn("bread", r.result, "error: a bid found for a bread after a removed manager started a bid")

    def test_no_need_to_approve_a_bid(self):
        with patch(self.app.provision_path, return_value=True) as delivery_mock, \
                patch(self.app.payment_pay_path, return_value=True) as payment_mock:

            self.set_store_and_appointments()
            self.app.login(*self.store_founder1)
            r = self.app.start_bid("bakery", "bread")
            self.assertTrue(r.success, "error: start a bid action failed")
            r = self.app.get_store_approval_lists_and_bids("bakery")
            self.assertTrue(r.success, "error: get approval list for store bids action failed")
            bids = r.result["Bids"]
            self.assertIn("bread", bids, "error: bread not found in bids")
            self.assertEqual(0, bids["bread"]["price"], "error: bid initial price is not 0")
            self.assertEqual(1, len(bids["bread"]["to_approve"]), "error: not only founder in approval list")
            self.assertIn(self.store_founder1[0], bids["bread"]["to_approve"], "error: founder not in approval list")
            self.app.logout()
            self.app.login(*self.registered_user)
            r = self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                            "ben-gurion", "1234", 10.5, "beer sheva", "israel")
            self.assertTrue(r.success, "error: purchase with a bid policy failed")
            self.app.logout()
            self.app.login(*self.store_founder1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertTrue(r.success, "error: approve bid action failed")
            self.app.logout()
            payment_mock.assert_called_once_with(10.5)
            delivery_mock.assert_called_once()
            self.app.login(*self.store_manager1)
            r = self.app.approve_bid("bakery", "bread")
            self.assertFalse(r.success, "error: approve bid action succeeded")

    def set_store_and_appointments(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.appoint_manager(self.store_manager1[0], "bakery")
        for p in Permission:
            if p not in Permissions.get_default_manager_permissions():
                self.app.add_permission("bakery", self.store_manager1[0], p)
        self.app.logout()
        self.app.login(*self.store_manager1)
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        self.app.login(*self.store_founder1)
        self.app.remove_appointment(self.store_manager1[0], "bakery")
        self.app.logout()
