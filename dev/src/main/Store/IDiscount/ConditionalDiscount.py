import operator
from abc import ABC, abstractmethod
from functools import reduce
from typing import Callable, TypeAlias

from dev.src.main.Store.IDiscount.Discount import IDiscount
from dev.src.main.User.Basket import Item, Basket

Predicate: TypeAlias = Callable[[Basket], bool]
Predicates: TypeAlias = list[Predicate]


class ConditionalDiscount(IDiscount, ABC):
    def __init__(self, days: int, percentage: float, name: str, predicates: Predicates, operator, identity_element):
        super().__init__(days, percentage, name)
        self.is_valid_basket = lambda basket: reduce(lambda acc, predicate: operator(acc, predicate(basket)), predicates, identity_element)

    def __str__(self):
        return f'ConditionalDiscount'

    def add(self, discount: 'IDiscount') -> bool:
        return False

    def remove(self, discount_name: str) -> bool:
        return False

    def apply(self, basket: Basket) -> Basket:
        return Basket(list(map(self.estimate, basket.items))) if self.is_valid_basket(basket) else basket


def make_logical_add_conditional_discount(days: int, percentage: float, predicates: Predicates) -> ConditionalDiscount:
    return ConditionalDiscount(days=days, percentage=percentage, name='And',predicates=predicates,
                               operator=operator.and_, identity_element=True)


def make_logical_or_conditional_discount(days: int, percentage: float, predicates: Predicates) -> ConditionalDiscount:
    return ConditionalDiscount(days=days, percentage=percentage, name='Or', predicates=predicates,
                               operator=operator.or_, identity_element=False)