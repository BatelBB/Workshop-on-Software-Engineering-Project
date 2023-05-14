from abc import ABC, abstractmethod

from domain.main.User.Basket import Basket
from src.domain.main.Utils.Response import Response


class IRule(ABC):

    @abstractmethod
    def enforce_rule(self, basket: Basket) -> Response[bool]:
        ...