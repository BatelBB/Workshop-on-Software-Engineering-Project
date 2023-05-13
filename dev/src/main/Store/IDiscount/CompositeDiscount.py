import random
from abc import ABC
from functools import reduce
from typing import Callable

from dev.src.main.Store.IDiscount.Discount import IDiscount
from dev.src.main.User.Basket import Basket


class CompositeDiscount(IDiscount, ABC):
    def __init__(self, days: int, percentage: float, name: str, composite: Callable[[list[IDiscount], Basket], Basket],
                 leafs: list[IDiscount] = None):
        super().__init__(days, percentage, name)
        self.composite = composite
        self.leafs = leafs
        if self.leafs is None:
            self.leafs = []

    def __str__(self):
        return f'CompositeDiscount'

    def add(self, discount: 'IDiscount') -> bool:
        self.leafs.append(discount)
        return True

    def remove(self, discount_name: str) -> bool:
        return True

    def apply(self, basket: Basket) -> Basket:
        return self.composite(self.leafs, basket)


def make_xor_composite_discount(days: int, percentage: float) -> CompositeDiscount:
    return CompositeDiscount(days=days, percentage=percentage, name='Xor',
                             composite=lambda basket, discounts: random.choice(discounts).apply(basket))


def make_addition_composite_discount(days: int, percentage: float) -> CompositeDiscount:
    return CompositeDiscount(days=days, percentage=percentage, name='Add',
                             composite=lambda basket, discounts: reduce(lambda basket, discount: discount.apply(basket),
                                                                        discounts, basket))


def make_max_composite_discount(days: int, percentage: float) -> CompositeDiscount:
    return CompositeDiscount(days=days, percentage=percentage, name='Max',
                             composite=lambda basket, discounts: reduce(
                                 lambda basket, discount: discount.apply(basket) if discount.apply(basket).total_price > basket.total_price else basket,
                                 discounts, basket))
