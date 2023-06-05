from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Store.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from domain.main.Store.Product import Product
from domain.main.UserModule.Basket import Basket


class MaxDiscounts(IDiscountConnector):
    def __init__(self, discount1: IDiscount, discount2: IDiscount):
        super().__init__(discount1, discount2)

    def apply_discount(self, basket: Basket, products: set[Product]):
        basket1 = self.discount1.apply_discount(basket, products)
        basket2 = self.discount2.apply_discount(basket, products)
        if basket1.calc_price() > basket2.calc_price():
            return basket1
        return basket2
