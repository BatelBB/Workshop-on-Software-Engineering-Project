from abc import ABC, abstractmethod
from domain.main.Store.Product import Product
from domain.main.UserModule.Basket import Basket


class IDiscount(ABC):
    @abstractmethod
    def apply_discount(self, basket: Basket, products: set[Product]) -> Basket:
        ...
