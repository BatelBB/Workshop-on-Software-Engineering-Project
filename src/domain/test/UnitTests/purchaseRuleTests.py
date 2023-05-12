import unittest

from domain.main.Store.Product import Product
from domain.main.Store.PurchaseRules.RuleCombiner.AndRule import AndRule
from domain.main.Store.PurchaseRules.RuleCombiner.ConditioningRule import ConditioningRule
from domain.main.Store.PurchaseRules.RuleCombiner.OrRule import OrRule
from domain.main.Store.PurchaseRules.SimpleRule import SimpleRule
from domain.main.User.Basket import Basket, Item
from src.domain.main.Market.Market import Market
from src.domain.main.Service.IService import IService


class purchaseRuleTests(unittest.TestCase):
    rule1: SimpleRule
    rule2: SimpleRule

    def test_lambdas(self):
        basket = Basket()
        p = Product("cup", "kitchen", 10)
        i = Item("cup", 3, 10)
        basket.add_item(i)

        srg_success = SimpleRule("cup", ">", 2)
        self.assertTrue(srg_success.enforce_rule(basket).success, "greater failed")
        srg_fail = SimpleRule("cup", ">", 5)
        self.assertFalse(srg_fail.enforce_rule(basket).success, "greater failed")

        srl_success = SimpleRule("cup", "<", 5)
        self.assertTrue(srl_success.enforce_rule(basket).success, "greater failed")
        srl_fail = SimpleRule("cup", "<", 2)
        self.assertFalse(srl_fail.enforce_rule(basket).success, "greater failed")

        sre_success = SimpleRule("cup", "=", 3)
        self.assertTrue(sre_success.enforce_rule(basket).success, "greater failed")
        sre_fail = SimpleRule("cup", "=", 2)
        self.assertFalse(sre_fail.enforce_rule(basket).success, "greater failed")

    def setup_2_rules(self):
        self.rule1 = SimpleRule("plate", ">", 4)
        self.rule2 = SimpleRule("cup", "=", 4)

    def test_cond_comb_success_1(self):
        basket = Basket()
        i = Item("cup", 4, 10)
        i2 = Item("plate", 5, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        condRule = ConditioningRule(self.rule1, self.rule2)
        self.assertTrue(condRule.enforce_rule(basket).success, "and failed")

    def test_cond_comb_success_2(self):
        basket = Basket()
        i = Item("cup", 5, 10)
        i2 = Item("plate", 2, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        condRule = ConditioningRule(self.rule1, self.rule2)
        self.assertTrue(condRule.enforce_rule(basket).success, "and failed")

    def test_cond_comb_fail(self):
        basket = Basket()
        i = Item("cup", 2, 10)
        i2 = Item("plate", 5, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        condRule = ConditioningRule(self.rule1, self.rule2)
        r = condRule.enforce_rule(basket)
        self.assertFalse(condRule.enforce_rule(basket).success, "and failed")

    def test_and_comb_success(self):
        basket = Basket()
        i = Item("cup", 4, 10)
        i2 = Item("plate", 5, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        andRule = AndRule(self.rule1, self.rule2)
        self.assertTrue(andRule.enforce_rule(basket).success, "and failed")

    def test_and_comb_fail(self):
        basket = Basket()
        i = Item("cup", 4, 10)
        i2 = Item("plate", 3, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        andRule = AndRule(self.rule1, self.rule2)
        res = andRule.enforce_rule(basket)
        self.assertFalse(res.success, "and failed")

    def test_or_comb_success_1(self):
        basket = Basket()
        i = Item("cup", 4, 10)
        i2 = Item("plate", 5, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        orRule = OrRule(self.rule1, self.rule2)
        self.assertTrue(orRule.enforce_rule(basket).success, "and failed")

    def test_or_comb_success_2(self):
        basket = Basket()
        i = Item("cup", 3, 10)
        i2 = Item("plate", 5, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        orRule = OrRule(self.rule1, self.rule2)
        self.assertTrue(orRule.enforce_rule(basket).success, "and failed")

    def test_or_comb_success_3(self):
        basket = Basket()
        i = Item("cup", 4, 10)
        i2 = Item("plate", 3, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        orRule = OrRule(self.rule1, self.rule2)
        self.assertTrue(orRule.enforce_rule(basket).success, "and failed")

    def test_or_comb_fail(self):
        basket = Basket()
        i = Item("cup", 2, 10)
        i2 = Item("plate", 2, 10)
        basket.add_item(i)
        basket.add_item(i2)

        self.setup_2_rules()
        orRule = OrRule(self.rule1, self.rule2)
        self.assertFalse(orRule.enforce_rule(basket).success, "and failed")


    def test_owner_adding_complex_rule(self):
        self.setup_2_rules()

        service = Market()
        s1 = service.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s")
        s1.add_product("s", "p1", "sus", 12, 5)
        s1.add_product("s", "p2", "sus", 4, 9)
        s1.add_purchase_complex_rule("s", "p1", "=", 2, "p2", ">", 3, "cond")

        s2 = service.enter()
        s2.add_to_cart("s", "p1", 2)

        res = s2.purchase_shopping_cart("card", ["asd", "asd", "Asd"], "ashdod", "74664")
        self.assertFalse(res.success, "fail")


    def test_owner_adding_complex_rule_2(self):
        service = Market()
        s1 = service.enter()
        s1.register("u1", "p1")
        s1.login("u1", "p1")
        s1.open_store("s")
        s1.add_product("s", "p1", "sus", 12, 5)
        s1.add_product("s", "p2", "sus", 4, 9)
        s1.add_purchase_complex_rule("s", "p1", "=", 2, "p2", ">", 3, "cond")

        s2 = service.enter()
        s2.add_to_cart("s", "p1", 2)
        s2.add_to_cart("s", "p2", 5)

        res = s2.purchase_shopping_cart("card", ["asd", "asd", "Asd"], "ashdod", "74664")
        self.assertTrue(res.success, "fail")
