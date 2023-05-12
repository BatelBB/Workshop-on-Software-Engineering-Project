from abc import ABC, abstractmethod

from domain.main.User.Basket import Basket
from domain.main.Utils.Response import Response


class Rule(ABC):

    @abstractmethod
    def enforce_rule(self, basket: Basket) -> Response[bool]:
        ...