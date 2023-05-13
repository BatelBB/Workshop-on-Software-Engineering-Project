from datetime import datetime
from functools import reduce
from typing import Optional

from dev.src.main.Store.Product import Product


class Item:
    def __init__(self, product: Product, quantity: int = 1, discount_price: float = None, discount_due_date: datetime = None):
        self.product = product
        self.quantity = quantity
        self.discount_price = discount_price
        self.discount_due_date = discount_due_date
        if self.discount_price is None:
            self.discount_price = product.price

    def __str__(self):
        discount_price_str = f', Discount Price: {self.discount_price}, Discount Due Date: {self.discount_due_date}' \
            if self.discount_price < self.product.price else ''
        return f'{self.product}, Quantity: {self.quantity}{discount_price_str}.'

    def __eq__(self, other):
        return self.product == other.product


class Basket:
    def __init__(self, items: list[Item] = None):
        self.items = items
        if self.items is None:
            self.items = []
        self.purchaser = ''
        self.seller = ''
        self.total_price = self.estimate_total_price()

    def __str__(self):
        items_strings: list[str] = list(map(lambda i: i.__str__(), self.items))
        total_price_str = f'\nTotal Price: {self.total_price}.' if self.total_price > 0.0 else ''
        return "Basket: {" + ', '.join(items_strings) + '}' + total_price_str

    def add(self, item: Item) -> int:
        new_quantity = item.quantity
        try:
            item_index = self.items.index(item)
            additional_quantity = item.quantity
            item_in_basket = self.items[item_index]
            new_quantity = item_in_basket.quantity + additional_quantity
            if new_quantity <= 0:
                self.items.remove(item)
                new_quantity = 0
            else:
                item_in_basket.quantity = new_quantity
        except Exception:
            self.items.append(item)
        return new_quantity

    def remove(self, item: Item) -> None:
        try:
            self.items.remove(item)
        except Exception:
            pass

    def estimate_total_price(self) -> float:
        return reduce(lambda total, item: total + (item.discount_price * item.quantity), self.items, 0.000)
