from abc import ABC, abstractmethod

from domain.main.Store.DIscounts.IDIscount import IDiscount
from domain.main.Utils.Logger import report
from domain.main.Utils.Response import Response


class IDiscountConnector(IDiscount, ABC):
    def __init__(self, id: int):
        super().__init__(id)
        self.children: list[IDiscount] = []

    def add_discount_to_connector(self, discount) -> Response:
        self.children.append(discount)
        return report("added discount", True)
