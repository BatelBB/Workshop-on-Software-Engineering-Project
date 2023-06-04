from abc import ABC, abstractmethod

from src.domain.main.Store.Product import Product
from src.domain.main.UserModule.Basket import Basket


class IDiscountFor(ABC):
    @abstractmethod
    def get_products_to_apply_discount_to(self, products: set[Product]):
        ...

