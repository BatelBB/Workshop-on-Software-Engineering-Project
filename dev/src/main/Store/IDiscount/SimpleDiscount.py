from abc import ABC
from typing import Callable

from dev.src.main.Store.IDiscount.Discount import IDiscount
from dev.src.main.User.Basket import Item, Basket


class SimpleDiscount(IDiscount, ABC):
    def __init__(self, days: int, percentage: float, name: str, filter: Callable[[Item], bool]):
        super().__init__(days, percentage, name)
        self.filter = filter

    def __str__(self):
        return f'SimpleDiscount: {self.name}'

    def estimate(self, item: Item) -> Item:
        return super().estimate(item) if self.filter(item) else item

    def add(self, discount: 'IDiscount') -> bool:
        return False

    def remove(self, discount_name: str) -> bool:
        return False

    def apply(self, basket: Basket) -> Basket:
        return Basket(list(map(self.estimate, basket.items)))


def make_uniform_simple_discount(days: int, percentage: float) -> SimpleDiscount:
    return SimpleDiscount(days=days, percentage=percentage, name='Uniform',filter=lambda item: True)


def make_categorical_simple_discount(days: int, percentage: float, category: str) -> SimpleDiscount:
    return SimpleDiscount(days=days, percentage=percentage, name=f'Categorical={category}',
                          filter=lambda item: item.product.category == category)


def make_hidden_discount(days: int, percentage: float, coupon: str) -> SimpleDiscount:
    return SimpleDiscount(days=days, percentage=percentage, name=f'Hidden(coupon={coupon})',
                          filter=lambda item: coupon in item.product.keywords)
