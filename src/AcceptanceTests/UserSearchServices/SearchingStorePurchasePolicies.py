import unittest
from unittest.mock import patch
from Service.bridge.proxy import Proxy


class AppointOwner(unittest.TestCase):
    app: Proxy = Proxy()

    @classmethod
    def setUpClass(cls) -> None:
        cls.store_founder1 = ("usr1", "password")
        cls.registered_user = ("usr2", "password")

    def setUp(self) -> None:
        self.app.enter_market()
        self.app.load_configuration()
        self.app.register(*self.store_founder1)
        self.app.register(*self.registered_user)
        self.set_stores_and_bids()

    def tearDown(self) -> None:
        self.app.exit_market()
        self.app.clear_data()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.app.enter_market()
        cls.app.shutdown()

    def test_search_for_a_bid_happy(self):
        r = self.app.get_bid_products("bakery")
        self.assertTrue(r.success, "error: get bid product action failed")
        bids = r.result
        self.assertIn("bread", bids, "error: no bid found for a bread after a owner started a bid")
        self.assertEqual(0, bids["bread"])

    def test_search_for_a_bid_after_bid_raised(self):
        self.app.login(*self.registered_user)
        self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                    "ben-gurion", "1234", 15.5, "beer sheva", "israel")
        r = self.app.get_bid_products("bakery")
        self.assertTrue(r.success, "error: get bid product action failed")
        bids = r.result
        self.assertIn("bread", bids, "error: no bid found for a bread after a owner started a bid")
        self.assertEqual(15.5, bids["bread"])

    def test_search_for_a_bid_invalid_store_name(self):
        r = self.app.get_bid_products("xxx")
        self.assertFalse(r.success, "error: get bid product action succeeded")
        self.assertIsNone(r.result, "error: got bids for invalid store name")

    def test_search_for_a_bid_no_bids(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("market")
        self.app.add_product("market", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("market", "pita", "1", 5, 20, ["basic", "y"])
        self.app.logout()
        r = self.app.get_bid_products("market")
        self.assertTrue(r.success, "error: get bid product action failed")
        bids = r.result
        self.assertEqual(0, len(bids), "error: bids found for a a store with no bids")

    def test_search_for_a_bid_declined_bid(self):
        self.app.login(*self.registered_user)
        self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                    "ben-gurion", "1234", 15.5, "beer sheva", "israel")
        self.app.logout()
        self.app.login(*self.store_founder1)
        r = self.app.approve_bid("bakery", "bread", False)
        self.assertTrue(r.success, "error: approve bid action failed")
        self.app.logout()
        r = self.app.get_bid_products("bakery")
        self.assertTrue(r.success, "error: get bid product action failed")
        bids = r.result
        self.assertIn("bread", bids, "error: no bid found for bread after a founder disapproved the bid")
        self.assertEqual(0, bids["pita"])
        self.assertIn("pita", bids, "error: no bid found for pita after a founder started a bid")
        self.assertEqual(0, bids["pita"])

    def test_search_for_a_bid_after_bid_finished(self):
        with patch(self.app.provision_path, return_value=True), patch(self.app.payment_pay_path, return_value=True):
            self.app.login(*self.registered_user)
            self.app.purchase_with_non_immediate_policy("bakery", "bread", "card", ["123", "123", "12/6588"],
                                                        "ben-gurion", "1234", 15.5, "beer sheva", "israel")
            self.app.logout()
            self.app.login(*self.store_founder1)
            self.app.approve_bid("bakery", "bread")
            self.app.logout()
            r = self.app.get_bid_products("bakery")
            self.assertTrue(r.success, "error: get bid product action failed")
            bids = r.result
            self.assertNotIn("bread", bids, "error: found for bread after a bid finished successfully")
            self.assertIn("pita", bids, "error: no bid found for pita after a founder started a bid")
            self.assertEqual(0, bids["pita"])

    def test_search_for_a_bid_closed_store(self):
        self.app.login(*self.store_founder1)
        r = self.app.close_store("bakery")
        self.assertTrue(r.success, "error: close store action failed")
        self.app.logout()
        r = self.app.get_bid_products("bakery")
        self.assertFalse(r.success, "error: get bid product action succeeded")
        bids = r.result
        self.assertIsNone(bids, "error: bids found after a store closed")

    def test_search_for_a_bid_removed_product(self):
        self.app.login(*self.store_founder1)
        r = self.app.remove_product("bakery", "bread")
        self.assertTrue(r.success, "error: remove product action action failed")
        self.app.logout()
        r = self.app.get_bid_products("bakery")
        self.assertTrue(r.success, "error: get bid product action failed")
        bids = r.result
        self.assertNotIn("bread", bids, "error: found for bread after a founder removed bread")
        self.assertIn("pita", bids, "error: no bid found for pita after a founder started a bid")
        self.assertEqual(0, bids["pita"])

    def set_stores_and_bids(self):
        self.app.login(*self.store_founder1)
        self.app.open_store("bakery")
        self.app.add_product("bakery", "bread", "1", 10, 15, ["basic", "x"])
        self.app.add_product("bakery", "pita", "1", 5, 20, ["basic", "y"])
        self.app.start_bid("bakery", "bread")
        self.app.start_bid("bakery", "pita")
        self.app.logout()
