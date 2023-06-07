from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Store.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from domain.main.Store.Product import Product
from domain.main.UserModule.Basket import Basket


class MaxDiscounts(IDiscountConnector):
    def __init__(self, discount1: IDiscount, discount2: IDiscount):
        super().__init__()

    def apply_discount(self, basket: Basket, products: set[Product]):
        basket_save = basket.deep_copy()
        best_price = basket.calc_price()

        for discount in self.children:
            next_basket = discount.apply_discount(basket_save, products)
            if next_basket.calc_price() < best_price:
                basket = basket_save
            else:
                basket_save = basket.deep_copy()

        return basket