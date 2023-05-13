from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Callable

from dev.src.main.User.Basket import Item, Basket


class IDiscount(ABC):
    def __init__(self, days: int, percentage: float, name: str):
        self.percentage = percentage
        self.name = name
        self.start_date = datetime.now()
        self.due_date = datetime.now() + timedelta(days=days)

    def __str__(self):
        def date_to_string(date) -> str: return date.strftime("%d/%m/%Y %H:%M:%S")
        return f'{self}, Percentage: {self.percentage}, Start Date: {date_to_string(self.start_date)}, Due Date:{date_to_string(self.due_date)}'

    def __eq__(self, other):
        return self.name == other.name

    def is_valid(self) -> bool:
        return self.start_date <= self.due_date

    def estimate(self, item: Item) -> Item:
        return Item(item.product, item.quantity, (1 - self.percentage) * item.product.price, self.due_date)

    @abstractmethod
    def add(self, discount: 'IDiscount') -> bool:
        ...

    @abstractmethod
    def remove(self, discount_name: str) -> bool:
        ...

    @abstractmethod
    def apply(self, basket: Basket) -> Basket:
        ...
