from dev.src.main.Store.Product import Product
from dev.src.main.User.Basket import Basket, Item


class Cart:
    def __init__(self):
        self.baskets: dict[str, Basket] = dict()

    def __str__(self):
        output = "Cart:\n"
        for store_name, basket in self.baskets.items():
            output += f'\tStore \'{store_name}\'\n\t{basket}'
        return output

    def get_or_create_basket(self, store_name: str) -> Basket:
        if store_name not in self.baskets:
            self.baskets.update({store_name: Basket()})
        return self.baskets[store_name]

    def add(self, store_name: str, product: Product, quantity: int) -> None:
        basket = self.get_or_create_basket(store_name)
        item = Item(product, quantity)
        basket.add(item)

    def remove(self, store_name: str, product: Product) -> None:
        basket = self.get_or_create_basket(store_name)
        item = Item(product)
        basket.remove(item)

    def update(self, store_name: str, product: Product, quantity: int) -> int:
        basket = self.get_or_create_basket(store_name)
        item = Item(product, quantity)
        basket.add(item)
