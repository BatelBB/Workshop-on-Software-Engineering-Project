import unittest

from domain.main.Market.Market import Market
from domain.main.User.Basket import Basket, Item


class xor_discount_tests(unittest.TestCase):

    # def xor_test_fail(self):
    #     # add a product to a store



    def test_fail(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_product("s1", "p2", "c2", 10, 5)
        s1.add_product("s1", "p3", "c2", 10, 5)
        s1.add_discount("s1", "xor", 50, 3, "product", "p1", "basket", 100, "category", "c2", min_price=30)
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        basket.add_item(item)
        #verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)
        self.assertTrue(price == 20, f"price is {price} lower than 30")

    def test_success(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_product("s1", "p2", "c2", 10, 5)
        s1.add_product("s1", "p3", "c2", 10, 5)
        s1.add_discount("s1", "xor", 50, 3, "product", "p1", "basket", 50, "category", "c2", min_price=30)
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        item2 = Item("p2", 2, 10)
        item3 = Item("p3", 2, 10)
        basket.add_item(item)
        basket.add_item(item2)
        basket.add_item(item3)
        #verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)
        self.assertTrue(price == 40, f"price is {price} lower than 30")
