from domain.main.StoreModule.DIscounts.IDIscount import IDiscount
from domain.main.StoreModule.DIscounts.Discount_Connectors.IDIscountConnector import IDiscountConnector
from domain.main.StoreModule.Product import Product
from domain.main.UserModule.Basket import Basket


class AddDiscounts(IDiscountConnector):
    def __init__(self, id: int):
        super().__init__(id)

    def apply_discount(self, basket: Basket, products: set[Product]):
        for discount in self.children:
            basket = discount.apply_discount(basket, products)
        return basket

    def is_level_o_discount(self, id: int) -> bool:
        for discount in self.children:
            if discount.check_id(id):
                return True
        return False

    def __str__(self, indent):
        return f"{indent}Add connector:  \n{super().__str__(indent)} \n"

    def __repr__(self):
        return f"Add connector: {super().__repr__()}"
