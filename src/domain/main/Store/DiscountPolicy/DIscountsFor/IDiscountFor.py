from abc import ABC, abstractmethod

from domain.main.Store.Product import Product
from domain.main.User.Basket import Basket


class IDiscountFor(ABC):
    @abstractmethod
    def get_products_to_apply_discount_to(self, products: set[Product]):
        ...