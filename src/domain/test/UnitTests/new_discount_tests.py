import unittest

from domain.main.Store.DIscounts.SimpleDiscount import SimpleDiscount
from domain.main.Store.PurchaseRules.BasketRule import BasketRule
from domain.main.Store.PurchaseRules.SimpleRule import SimpleRule
from domain.main.Store.Store import Store
from src.domain.main.Market.Market import Market
from src.domain.main.UserModule.Basket import Basket, Item


class new_discount_tests(unittest.TestCase):

    def test_simple_success(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        store = market.stores.get("s1")

        store.add_simple_discount(50, "product", discount_for_name="p1")

        self.assertTrue(store.discounts.is_level_o_discount(1), "incorrect")

    def test_Add_Discounts_success(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        store = market.stores.get("s1")
        s1.add_product("s1", "p1", "c1", 100, 50)

        store.add_simple_discount(50, "product", discount_for_name="p1")
        store.add_simple_discount(20, "product", discount_for_name="p1")
        store.add_simple_discount(10, "product", discount_for_name="p1")

        basket = Basket()
        item = Item("p1", "u1", "s1", 1, 100)
        basket.add_item(item)
        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 20, f"price should be 20 but is {price}")

    def test_add_with_rule(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        store = market.stores.get("s1")
        s1.add_product("s1", "p1", "c1", 100, 50)

        store.add_simple_discount(50, "product", BasketRule(150), discount_for_name="p1")
        store.add_simple_discount(20, "product", discount_for_name="p1")
        store.add_simple_discount(10, "product", discount_for_name="p1")

        basket = Basket()
        item = Item("p1", "u1", "s1", 1, 100)
        basket.add_item(item)
        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 70, f"price should be 70 but is {price}")

    def test_xor_01(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        store = market.stores.get("s1")
        s1.add_product("s1", "p1", "c1", 100, 50)

        store.add_simple_discount(50, "product", discount_for_name="p1")    # 1
        store.add_simple_discount(20, "product", discount_for_name="p1")    # 2
        store.add_simple_discount(10, "product", discount_for_name="p1")    # 3

        store.connect_discounts(1, 2, "xor", SimpleRule("p1", ">", 1))


        basket = Basket()
        item = Item("p1", "u1", "s1", 2, 100)
        basket.add_item(item)
        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 40, f"price should be 70 but is {price}")

    def test_xor_02(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        store = market.stores.get("s1")
        s1.add_product("s1", "p1", "c1", 100, 50)

        store.add_simple_discount(50, "product", discount_for_name="p1")    # 1
        store.add_simple_discount(20, "product", discount_for_name="p1")    # 2
        store.add_simple_discount(10, "product", discount_for_name="p1")    # 3

        store.connect_discounts(1, 2, "xor", SimpleRule("p1", "=", 1))


        basket = Basket()
        item = Item("p1", "u1", "s1", 2, 100)
        basket.add_item(item)
        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 70, f"price should be 70 but is {price}")


    def test_conn_2_level(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        store = market.stores.get("s1")
        s1.add_product("s1", "p1", "c1", 100, 50)

        store.add_simple_discount(50, "product", discount_for_name="p1")    # 1
        store.add_simple_discount(20, "product", discount_for_name="p1")    # 2
        store.add_simple_discount(90, "product", discount_for_name="p1")    # 3

        store.connect_discounts(1, 2, "xor", SimpleRule("p1", "=", 1))      # 4

        store.connect_discounts(3, 4, "max")


        basket = Basket()
        item = Item("p1", "u1", "s1", 2, 100)
        basket.add_item(item)
        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 20, f"price should be 10 but is {price}")

    def test_conn_3_level(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        store = market.stores.get("s1")
        s1.add_product("s1", "p1", "c1", 100, 50)

        store.add_simple_discount(50, "product", discount_for_name="p1")    # 1
        store.add_simple_discount(20, "product", discount_for_name="p1")    # 2
        store.add_simple_discount(90, "product", discount_for_name="p1")    # 3

        store.connect_discounts(1, 2, "xor", SimpleRule("p1", "=", 1))      # 4

        store.connect_discounts(3, 4, "max")                                # 5

        store.add_simple_discount(5, "product", discount_for_name="p1")     # 6

        store.connect_discounts(5, 6, "add")

        basket = Basket()
        item = Item("p1", "u1", "s1", 2, 100)
        basket.add_item(item)
        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 10, f"price should be 10 but is {price}")


    def test_conn_3_level_with_service_and_session(self):
        market = Market()
        s1 = market.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s1")
        store = market.stores.get("s1")
        s1.add_product("s1", "p1", "c1", 100, 50)

        # store.add_simple_discount(50, "product", discount_for_name="p1")    # 1
        s1.add_simple_discount("s1", "product", 50, "p1")
        # store.add_simple_discount(20, "product", discount_for_name="p1")    # 2
        s1.add_simple_discount("s1", "product", 20, "p1")
        # store.add_simple_discount(90, "product", discount_for_name="p1")    # 3
        s1.add_simple_discount("s1", "product", 90, "p1")

        # store.connect_discounts(1, 2, "xor", SimpleRule("p1", "=", 1))      # 4
        s1.connect_discounts("s1", 1, 2, "xor", "simple",  p1_name="p1", gle1="=", amount1=1)

        # store.connect_discounts(3, 4, "max")                                # 5
        s1.connect_discounts("s1", 3, 4, "max")

        # store.add_simple_discount(5, "product", discount_for_name="p1")     # 6
        s1.add_simple_discount("s1", "product", 5, "p1")

        # store.connect_discounts(5, 6, "add")
        s1.connect_discounts("s1", 5, 6, "add")

        basket = Basket()
        item = Item("p1", "u1", "s1", 2, 100)
        basket.add_item(item)
        price = store.calculate_basket_price(basket)

        self.assertTrue(price == 10, f"price should be 10 but is {price}")
        print(store.discounts.__str__(""))
