from abc import ABC, abstractmethod
from domain.main.Store.Product import Product
from domain.main.UserModule.Basket import Basket


class IDiscount(ABC):

    def __init__(self, id: int):
        self.id = id
        
    @abstractmethod
    def apply_discount(self, basket: Basket, products: set[Product]) -> Basket:
        ...

    def check_id(self, id: int) -> bool:
        return self.id == id

    def find_discount(self, id: int):
        if self.check_id(id):
            return self
        return None

    @abstractmethod
    def remove_discount(self, id) -> bool:
        ...

    @abstractmethod
    def replace(self, id, discount) -> bool:
        ...

    @abstractmethod
    def get_parents_id(self, id) -> int:
        ...