from src.domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from src.domain.main.StoreModule.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from src.domain.main.StoreModule.Product import Product
from src.domain.main.UserModule.Basket import Basket


class OrDiscounts(IDiscountConnector):
    def __init__(self, id: int):
        super().__init__(id)

    # returns the min discount
    def apply_discount(self, basket: Basket, products: set[Product]):
        initial = basket.calc_price()

        basket1 = basket.deep_copy()
        basket2 = basket.deep_copy()

        basket1 = self.children[0].apply_discount(basket1, products)
        price1 = basket1.calc_price()
        basket2 = self.children[1].apply_discount(basket2, products)
        price2 = basket2.calc_price()

        if price1 == initial:
            return basket2
        elif price2 == initial:
            return basket1
        elif price1 > price2:
            return basket1
        else:
            return basket2


    def __str__(self, indent):
        return f"{indent}Or connector:  \n{super().__str__(indent)} \n"

    def __repr__(self):
        return f"Or connector: {super().__repr__()}"