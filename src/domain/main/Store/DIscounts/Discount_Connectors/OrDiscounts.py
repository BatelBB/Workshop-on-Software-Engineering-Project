from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Store.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from domain.main.Store.Product import Product
from domain.main.UserModule.Basket import Basket


class OrDiscounts(IDiscountConnector):
    def __init__(self, id: int):
        super().__init__(id)

    # returns the min discount
    def apply_discount(self, basket: Basket, products: set[Product]):
        basket_save = basket.deep_copy()
        best_price = basket.calc_price()

        for discount in self.children:
            next_basket = discount.apply_discount(basket.deep_copy(), products)
            if next_basket.calc_price() > best_price:
                best_price = next_basket.calc_price()
                basket_save = next_basket.deep_copy()

        return basket_save

    def __str__(self, indent):
        return f"{indent}Or connector:  \n{super().__str__(indent)} \n"

    def __repr__(self):
        return f"Add connector: {super().__repr__()}"