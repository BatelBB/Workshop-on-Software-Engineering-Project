from abc import ABC, abstractmethod
from src.domain.main.StoreModule.Product import Product
from src.domain.main.UserModule.Basket import Basket


class IDiscount:

    def __init__(self, id: int):
        self.discount_id = id

    def apply_discount(self, basket: Basket, products: set[Product]) -> Basket:
        pass

    def check_id(self, id: int) -> bool:
        return self.discount_id == id

    def find_discount(self, id: int):
        if self.discount_id == id:
            return self
        return None

    def remove_discount(self, id) -> bool:
        pass

    def replace(self, id, discount) -> bool:
        pass

    def get_parents_id(self, id) -> int:
        pass

    def __str__(self, indent) -> str:
        pass

    def get_all_simple_discounts(self, d) -> dict:
        d[self.discount_id] = self.__repr__()
        return d

    def get_all_connectors(self, l):
        pass

    def set_disconted_price_in_product(self, p: Product):
        pass

    def delete_from_db(self):
        pass
