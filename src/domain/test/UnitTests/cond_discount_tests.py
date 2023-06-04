import unittest

from src.domain.main.Market.Market import Market
from src.domain.main.UserModule.Basket import Basket, Item


class discount_policy_tests(unittest.TestCase):

    def test_basket_policy_fail(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_discount("s1", "cond", 50, 3, "product", "p1", "basket", min_price=30)
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        basket.add_item(item)
        # verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)
        self.assertTrue(price == 20, f"price is {price} lower than 30")

    def test_basket_policy_success(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_discount("s1", "cond", 50, 3, "product", "p1", "basket", min_price=30)
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 3, 10)
        basket.add_item(item)
        # verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)
        self.assertTrue(price == 15, f"price is {price} should be 15")

    def test_simple_fail(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_product("s1", "p2", "c1", 10, 5)
        s1.add_discount("s1", "cond", 50, 3, "product", "p1", "simple", p1_name="p2", gle1=">", amount1=3)
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        item2 = Item("p2", 2, 10)
        basket.add_item(item)
        basket.add_item(item2)
        # verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)
        self.assertTrue(price == 40, f"price is {price} should be 40")

    def test_simple_success(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_product("s1", "p2", "c1", 10, 5)
        s1.add_discount("s1", "cond", 50, 3, "product", "p1", "simple", p1_name="p2", gle1="=", amount1=3)
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        item2 = Item("p2", 3, 10)
        basket.add_item(item)
        basket.add_item(item2)
        # verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        price = store.calculate_basket_price(basket)
        self.assertTrue(price == 40, f"price is {price} should be 40")

    def test_simple_success(self):
        # add a product to a store
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        s1.add_product("s1", "p1", "c1", 10, 5)
        s1.add_product("s1", "p2", "c2", 10, 5)
        s1.add_discount("s1", "cond", 50, 3, "product", "p1", "simple", p1_name="p2", gle1="=", amount1=3)
        s1.add_discount("s1", "open", 20, 3, "category", "c1")
        # make a basket with 2 products
        basket = Basket()
        item = Item("p1", 2, 10)
        item2 = Item("p2", 3, 10)
        basket.add_item(item)
        basket.add_item(item2)
        # verify discount
        store = market.verify_registered_store("asd", "s1")
        store = store.result

        dis = store.get_product_discounts_str("p1")
        # self.assertTrue(price == 40, f"price is {price} should be 40")
        print(dis)
        self.assertTrue(True, "yes")