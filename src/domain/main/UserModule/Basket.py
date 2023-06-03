from functools import reduce


class Item:
    def __init__(self, product_name: str, quantity: int = 0, price: float = 0.0):
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
        self.discount_price = price

    def __str__(self):
        return f'Product: \'{self.product_name}\', Quantity: {self.quantity}, Price: {self.price}, Discount-Price: {self.discount_price}'

    def __dic__(self) -> dict:
        return {"Quantity": self.quantity, "Price": self.price}

    def __eq__(self, other):
        return self.product_name == other.product_name

    def get_quantity(self):
        return self.quantity

    def get_name(self):
        return self.product_name

    def get_price(self) -> float:
        return self.price


class Basket:
    def __init__(self):
        self.items: list[Item] = list()

    def __str__(self):
        return reduce(lambda acc, item: acc + '\n' + item.__str__(), self.items, '')

    def __dic__(self):
        output = {}
        for i in self.items:
            output[i.product_name] = i.__dic__()
        return output

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
        except ValueError:
            self.items.append(item)
        return new_quantity

    def remove_item(self, item: Item) -> bool:
        try:
            self.items.remove(item)
            return True
        except Exception:
            return False

    def get_item(self, name):
        for i in self.items:
            if i.product_name == name:
                return i

