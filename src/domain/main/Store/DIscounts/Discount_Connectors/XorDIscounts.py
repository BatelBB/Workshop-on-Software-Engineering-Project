from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Store.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from domain.main.Store.Product import Product
from domain.main.Store.PurchaseRules.IRule import IRule
from domain.main.UserModule.Basket import Basket


class MaxDiscounts(IDiscountConnector):
    def __init__(self, discount1: IDiscount, discount2: IDiscount, rule: IRule):
        super().__init__(discount1, discount2)
        self.rule = rule

    def apply_discount(self, basket: Basket, products: set[Product]):
        if self.rule.enforce_rule(basket).success:
            return self.discount1.apply_discount(basket, products)
        return self.discount2.apply_discount(basket, products)

