from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Store.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from domain.main.Store.Product import Product
from domain.main.UserModule.Basket import Basket


class AddDiscounts(IDiscountConnector):
    def __init__(self):
        super().__init__()

    def apply_discount(self, basket: Basket, products: set[Product]):
        for discount in self.children:
            basket = discount.apply_discount(basket, products)
        return basket
