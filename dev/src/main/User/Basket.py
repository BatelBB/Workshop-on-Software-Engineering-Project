class Item:
    def __init__(self, product_name: str, quantity: int = 0, price: float = 0.0):
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
        self.discount_price = price

    def __str__(self):
        return f'Item: Product: \'{self.product_name}\', Quantity: {self.quantity}, Price: {self.price}, Discount' \
               f'-Price: {self.discount_price}'

    def __eq__(self, other):
        return self.product_name == other.product_name


class Basket:
    def __init__(self):
        self.items: list[Item] = list()

    def __str__(self):
        items_strings: list[str] = list(map(lambda i: i.__str__(), self.items))
        return "Basket: {" + ', '.join(items_strings) + '}'

    def add_item(self, item: Item) -> int:
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
        except:
            self.items.append(item)
        return new_quantity

    def remove_item(self, item: Item) -> None:
        try:
            self.remove_item(item)
        except:
            pass
