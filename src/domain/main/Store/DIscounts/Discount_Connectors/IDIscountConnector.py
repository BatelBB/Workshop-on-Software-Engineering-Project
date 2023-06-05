from abc import ABC

from domain.main.Store.DIscounts.IDIscount import IDiscount


class IDiscountConnector(IDiscount, ABC):
    def __init__(self, discount1: IDiscount, discount2: IDiscount):
        self.discount1 = discount1
        self.discount2 = discount2
