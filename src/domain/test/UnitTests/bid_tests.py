import unittest

from domain.main.Market.Market import Market
from domain.main.Store.PurchasePolicy.BidPolicy import BidPolicy


class bid_tests(unittest.TestCase):
    def test_bid_set_bid(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        # s1.start_auction("s1", "p1", 5, 2)
        policy = BidPolicy()
        store = market.stores.get("s1")
        s1.start_bid("s1", "p1")
        policy = store.products_with_bid_purchase_policy["p1"]

        s2 = market.enter()
        s2.register("u2", "p2")
        s2.login("u2", "p2")

        s2.purchase_with_non_immediate_policy("s1", "p1", "card", ["1123", "123", "13"], "beersheva", "7422", 6,
                                              "beersheva", "israel")
        self.assertTrue(policy.delivery_service.user_name == "u2", "incorrect delivery service")


    def test_bid_approved(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        # s1.start_auction("s1", "p1", 5, 2)
        policy = BidPolicy()
        store = market.stores.get("s1")
        s1.start_bid("s1", "p1")
        policy: BidPolicy = store.products_with_bid_purchase_policy["p1"]

        s2 = market.enter()
        s2.register("u2", "p2")
        s2.login("u2", "p2")

        s2.purchase_with_non_immediate_policy("s1", "p1", "card", ["1123", "123", "13"], "beersheva", "7422", 6,
                                              "beersheva", "israel")
        self.assertTrue(policy.delivery_service.user_name == "u2", "incorrect delivery service")
        s1.approve_bid("s1", "p1", True)
        self.assertTrue(policy.is_approved(), "bid should be approved")

    def test_bid_swich_user(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        # s1.start_auction("s1", "p1", 5, 2)
        policy = BidPolicy()
        store = market.stores.get("s1")
        s1.start_bid("s1", "p1")
        policy: BidPolicy = store.products_with_bid_purchase_policy["p1"]

        s2 = market.enter()
        s2.register("u2", "p2")
        s2.login("u2", "p2")
        s3 = market.enter()
        s3.register("u3", "p3")
        s3.login("u3", "p3")

        s2.purchase_with_non_immediate_policy("s1", "p1", "card", ["1123", "123", "13"], "beersheva", "7422", 6,
                                              "beersheva", "israel")
        s3.purchase_with_non_immediate_policy("s1", "p1", "card", ["1123", "123", "13"], "beersheva", "7422", 12,
                                              "beersheva", "israel")
        self.assertTrue(policy.delivery_service.user_name == "u3", "incorrect delivery service")


    def test_bid_2_owners_1_approves_swich_user_now_2_approves(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        # s1.start_auction("s1", "p1", 5, 2)
        policy = BidPolicy()
        store = market.stores.get("s1")
        s1.start_bid("s1", "p1")
        policy: BidPolicy = store.products_with_bid_purchase_policy["p1"]

        s2 = market.enter()
        s2.register("u2", "p2")
        s2.login("u2", "p2")
        s3 = market.enter()
        s3.register("u3", "p3")
        s3.login("u3", "p3")
        s4 = market.enter()
        s4.register("u4", "p4")
        s4.login("u4", "p4")

        s1.appoint_owner("u4", "s1")

        s2.purchase_with_non_immediate_policy("s1", "p1", "card", ["1123", "123", "13"], "beersheva", "7422", 6,
                                              "beersheva", "israel")
        self.assertTrue(policy.delivery_service.user_name == "u2", "incorrect delivery service")
        s1.approve_bid("s1", "p1", True)

        s3.purchase_with_non_immediate_policy("s1", "p1", "card", ["1123", "123", "13"], "beersheva", "7422", 12,
                                              "beersheva", "israel")
        self.assertTrue(policy.delivery_service.user_name == "u3", "incorrect delivery service")

        s1.approve_bid("s1", "p1", True)
        s4.approve_bid("s1", "p1", True)

        self.assertTrue(policy.is_approved(), "bid should be approved")
