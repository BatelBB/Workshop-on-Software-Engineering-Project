from abc import ABC, abstractmethod

from src.domain.main.UserModule.Basket import Basket
from src.domain.main.Utils.Response import Response


class IRule(ABC):

    @abstractmethod
    def enforce_rule(self, basket: Basket) -> Response[bool]:
        ...

    @abstractmethod
    def __str__(self):
        ...