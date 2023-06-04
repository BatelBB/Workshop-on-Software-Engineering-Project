import unittest

from src.domain.main.Market.Market import Market
from src.domain.main.UserModule.Basket import Basket, Item


class discount_policy_tests(unittest.TestCase):

    def test_open_policy_success(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_discount("s1", "open", 20, 3, "product", "p1")
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 12)
        basket.add_item(item)
        #verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)
        self.assertTrue(price == 16, f"price should be 16 but is {price}")

    def test_open_discount_with_multiple_products_and_discounts(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_product("s1", "p2", "c1", 10, 5)
        s1.add_discount("s1", "open", 20, 3, "product", "p1")
        s1.add_discount("s1", "open", 50, 3, "product", "p2")
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        item2 = Item("p2", 1, 10)
        basket.add_item(item)
        basket.add_item(item2)
        # verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 21, f"price should be 16 but is {price}")


    def test_open_discount_for_category(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_product("s1", "p2", "c1", 10, 5)
        s1.add_discount("s1", "open", 20, 3, "category", "c1")
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        item2 = Item("p2", 1, 10)
        basket.add_item(item)
        basket.add_item(item2)
        # verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 24, f"price should be 16 but is {price}")

    def test_open_discount_for_store(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_product("s1", "p2", "c1", 10, 5)
        s1.add_discount("s1", "open", 20, 3, "store")
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        item2 = Item("p2", 1, 10)
        basket.add_item(item)
        basket.add_item(item2)
        # verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 24, f"price should be 16 but is {price}")

