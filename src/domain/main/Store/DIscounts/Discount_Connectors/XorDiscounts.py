from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Store.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from domain.main.Store.Product import Product
from domain.main.Store.PurchaseRules.IRule import IRule
from domain.main.UserModule.Basket import Basket
from domain.main.Utils.Logger import report_error


class XorDiscounts(IDiscountConnector):
    def __init__(self, id: int, discount1: IDiscount, discount2: IDiscount, rule: IRule):
        super().__init__(id)
        self.children.append(discount1)
        self.children.append(discount2)
        self.rule = rule

    def apply_discount(self, basket: Basket, products: set[Product]):
        if self.rule.enforce_rule(basket).success:
            return self.children[0].apply_discount(basket, products)
        return self.children[1].apply_discount(basket, products)

    def add_discount_to_connector(self, discount):
        return report_error("add_discount_to_connector", "cannot add discount to xor")
