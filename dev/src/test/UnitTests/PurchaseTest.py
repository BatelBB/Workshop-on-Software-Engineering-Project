import unittest

from dev.src.main.Market.Market import Market
from dev.src.main.Service.IService import IService
from dev.src.main.Utils.Response import Response


class PurchaseTest(unittest.TestCase):
    def setUp(self) -> None:
        # Note: each test create a new, fresh market with a unique session identifier
        self.service: IService = Market()
        self.session = self.service.enter()

    def tearDown(self) -> None:
        self.service.shutdown()

    def registerAndLoginDefault(self):
        self.session.register("test", "test_pass")
        self.session.login("test", "test_pass")

    def openStoreDefault(self):
        self.session.open_store("IHerb")

    def addProductsDefault(self):
        self.session.add_product("IHerb", "Vitamin A", "Vitamins", 19.9, 20)
        self.session.add_product("IHerb", "Toothpaste", "Hygiene", 21.2, 25)
    def test_purchaseFlow_returnCorrectly(self):
        self.registerAndLoginDefault()
        self.openStoreDefault()
        self.addProductsDefault()
        self.session.add_to_cart("IHerb","Vitamin A", 2)
        response: Response[bool] = self.session.purchase_shopping_cart("card", ["123", "123", "12345"])
        self.assertTrue(response.result)  # add assertion here
