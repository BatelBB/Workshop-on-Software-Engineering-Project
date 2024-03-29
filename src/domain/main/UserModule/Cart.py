from functools import reduce

from DataLayer.DAL import DAL
from src.domain.main.UserModule.Basket import Basket, Item


class Cart:
    def __init__(self, username):
        self.username = username
        self.baskets: dict[str, Basket] = dict()

    def __str__(self):
        return reduce(lambda acc, key: acc + f'Store \'{key}\'' + self.baskets[key].__str__() + '\n', self.baskets, '')

    def __dic__(self):
        output = {}
        for store_name, basket in self.baskets.items():
            output[store_name] = basket.__dic__()
        return output

    def has_basket(self, store_name: str) -> bool:
        return store_name in self.baskets

    def get_or_create_basket(self, store_name: str) -> Basket:
        if store_name not in self.baskets:
            self.baskets.update({store_name: Basket()})
        return self.baskets[store_name]

    def add_item(self, store_name: str, product_name: str, price: float, quantity: int) -> int:
        basket = self.get_or_create_basket(store_name)
        item = Item(product_name, self.username, store_name, quantity, price)
        return basket.add_item(item)

    def remove_item(self, store_name: str, product_name: str) -> bool:
        basket = self.get_or_create_basket(store_name)
        item = Item(product_name, self.username, store_name)
        return basket.remove_item(item)

    def update_item_quantity(self, store_name: str, product_name: str, quantity: int) -> bool:
        basket = self.get_or_create_basket(store_name)
        item = Item(product_name, self.username, store_name, quantity)
        return basket.update_item(item)

    def find_item(self, product_name, store_name) -> Item | None:
        basket = self.get_or_create_basket(store_name)
        try:
            i = basket.items.index(Item(product_name, self.username, store_name))
            return basket.items[i]
        except ValueError:
            return None

    def is_empty(self) -> bool:
        return len(self.baskets.items()) == 0

    def get_baskets(self) -> dict:
        return self.baskets

    def empty_basket(self, store_name: str):
        self.baskets.pop(store_name)

    @staticmethod
    def load_cart(username: str):
        cart = Cart(username)
        for r in DAL.retrieve_all(Item, lambda i: i.username == username):
            cart.add_item(r.store_name, r.product_name, r.price, r.quantity)
        return cart

    @staticmethod
    def clear_db():
        DAL.clear(Item)
