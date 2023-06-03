from functools import reduce

from src.domain.main.Store.Product import Product
from src.domain.main.UserModule.Basket import Basket, Item


class Cart:
    def __init__(self):
        self.baskets: dict[str, Basket] = dict()

    def __str__(self):
        return reduce(lambda acc, key: acc + f'Store \'{key}\'' + self.baskets[key].__str__() + '\n', self.baskets, '')

    def __dic__(self):
        output = {}
        for store_name, basket in self.baskets.items():
            output[store_name] = basket.__dic__()
        return output

    def get_or_create_basket(self, store_name: str) -> Basket:
        if store_name not in self.baskets:
            self.baskets.update({store_name: Basket()})
        return self.baskets[store_name]

    def add_item(self, store_name: str, product_name: str, price: float, quantity: int) -> None:
        basket = self.get_or_create_basket(store_name)
        item = Item(product_name, quantity, price)
        basket.add_item(item)

    def remove_item(self, store_name: str, product_name: str) -> None:
        basket = self.get_or_create_basket(store_name)
        item = Item(product_name)
        basket.add_item(item)

    def update_item_quantity(self, store_name: str, product_name: str, quantity: int) -> int:
        basket = self.get_or_create_basket(store_name)
        item = Item(product_name, quantity)
        basket.add_item(item)

    def is_empty(self) -> bool:
        return len(self.baskets.items()) == 0

    def get_baskets(self) -> dict:
        return self.baskets

    def empty_basket(self, store_name: str):
        self.baskets.pop(store_name)
