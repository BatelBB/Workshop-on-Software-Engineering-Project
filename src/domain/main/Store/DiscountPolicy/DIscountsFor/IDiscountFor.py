from abc import ABC, abstractmethod

from domain.main.User.Basket import Basket


class IDiscountFor(ABC):
    @abstractmethod
    def calculate_proce(self, basket: Basket):
        ...