import unittest

from domain.main.Market.Market import Market
from domain.main.Service.IService import IService
from domain.main.Store.PurchasePolicy.AuctionPolicy import AuctionPolicy
from domain.main.Utils.Response import Response


class test_purchase_policy:

    def __init__(self):
        self.service = None

    def setUp(self) -> None:
        self.service: Market = Market()

    def test_auction(self):
        s1 = self.service.enter()
        res = s1.register("sus", "rezah")
        re = s1.login("sus", "rezah")
        res = s1.open_store("burekas gedera")
        res = s1.add_product("burekas gedera", "burekas pitriot", "burekasim", 5, 5, ["burekas", "maafe", "bake"])
        res = s1.start_auction("burekas gedera", "burekas pitriot", 2, 1)
        store = self.service.stores.get("burekas gedera")
        print(store.products_with_special_purchase_policy)

        s2 = self.service.enter()
        res = s2.register("u2", "p2")
        res = s2.login("u2", "p2")
        res = s2.purchase_with_non_immediate_policy("burekas gedera", "burekas pitriot", "credit",
                                                    ["4580", "12/2030", "333"],
                                                    "beer sheva", "3777777")
        store.new_day()