
import unittest

from domain.main.Market.Market import Market
from domain.main.Store.PurchasePolicy.AuctionPolicy import AuctionPolicy


class auction_tests(unittest.TestCase):

    def test_lottery_simple(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.start_lottery("s1", "p1")
        # policy = AuctionPolicy(5, 3)
        store = market.stores.get("s1")
        # store.add_product_to_special_purchase_policy("p1", policy)

        s2 = market.enter()
        s2.register("u2", "p2")
        s2.login("u2", "p2")

        s1.purchase_with_non_immediate_policy("s1", "p1", "card", ["1123", "123", "13"], "beersheva", "7422", 3,
                                              "beersheva", "israel")
        res = s2.purchase_with_non_immediate_policy("s1", "p1", "card", ["1123", "123", "13"], "beersheva", "7422", 8,
                                              "beersheva", "israel")
        # self.assertTrue(policy.delivery_service.user_name == "u2", "incorrect delivery service")
        print("what to test?")